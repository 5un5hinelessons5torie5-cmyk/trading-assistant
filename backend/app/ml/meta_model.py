import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import os
import pickle
import logging
from sklearn.ensemble import RandomForestClassifier
from ..models.signal import Signal

MODEL_PATH = "ml_models/tp1_meta_model.pkl"

class MLMetaLayer:
    def __init__(self, model_version: str = "rf_v1.0.2"):
        self.version = model_version
        self.model = self._load_model()

    def _load_model(self) -> Optional[RandomForestClassifier]:
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logging.error(f"Error loading ML model: {e}")
                return None
        return None

    async def predict_tp1_prob(self, signal: Signal, features: Dict[str, Any]) -> float:
        if not self.model:
            # Fallback to a rule-based heuristic if model not trained yet
            base_prob = signal.confidence * 0.7
            if signal.strategy_role == "entry_engine":
                base_prob += 0.1
            return min(0.95, base_prob)

        try:
            # Prepare feature vector (must match training order)
            # Standardizing features: confidence, queue_quality, entry_price
            X = [[
                features.get("confidence", 0.5),
                features.get("queue_quality", 0.5),
                features.get("entry_price", 0.0)
            ]]
            # Real inference
            probs = self.model.predict_proba(X)[0]
            # Prob of class 1 (success)
            return float(probs[1]) if len(probs) > 1 else 0.5
        except Exception as e:
            logging.error(f"Inference error: {e}")
            return 0.5

    async def rank_signals(self, signals: List[Signal]) -> List[Signal]:
        for s in signals:
            features = {
                "confidence": s.confidence,
                "queue_quality": s.queue_quality,
                "entry_price": s.entry_price,
            }
            s.ml_score = await self.predict_tp1_prob(s, features)
            s.ml_pass = s.ml_score > 0.65
            s.ml_reason = "Probable TP1 expansion" if s.ml_pass else "Low historical edge in current regime"
            s.ml_model_version = self.version
        return sorted(signals, key=lambda x: x.ml_score or 0.0, reverse=True)

class MLTrainer:
    def __init__(self):
        os.makedirs("ml_models", exist_ok=True)

    def train_from_history(self, closed_positions: List[Any]):
        """Trains the model from closed trade history."""
        if len(closed_positions) < 10: # Lowered threshold for demonstration/initial phase
            logging.info(f"Not enough training samples: {len(closed_positions)}")
            return False

        data = []
        for p in closed_positions:
            # Target: did price hit TP1 before SL? (PnL > 0 used as proxy)
            success = 1 if p.pnl > 0 else 0
            data.append({
                'confidence': p.confidence if hasattr(p, 'confidence') else 0.5,
                'queue_quality': p.queue_quality if hasattr(p, 'queue_quality') else 0.5,
                'entry_price': p.entry_price,
                'success': success
            })

        df = pd.DataFrame(data)
        X = df[['confidence', 'queue_quality', 'entry_price']]
        y = df['success']

        # Guard against single-class training which breaks predict_proba
        if len(y.unique()) < 2:
            logging.info("Training data only has one outcome class. Skipping.")
            return False

        model = RandomForestClassifier(n_estimators=100)
        model.fit(X, y)

        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)

        logging.info("ML Model retrained and saved.")
        return True

ml_meta_layer = MLMetaLayer()
ml_trainer = MLTrainer()

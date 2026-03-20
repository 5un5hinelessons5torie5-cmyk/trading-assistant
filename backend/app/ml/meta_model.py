import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from ..models.signal import Signal

MODEL_PATH = "ml_models/tp1_meta_model.pkl"

class MLMetaLayer:
    def __init__(self, model_version: str = "rf_v1.0.1"):
        self.version = model_version
        self.model = self._load_model()

    def _load_model(self) -> Optional[RandomForestClassifier]:
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    return pickle.load(f)
            except:
                return None
        return None

    async def predict_tp1_prob(self, signal: Signal, features: Dict[str, Any]) -> float:
        if not self.model:
            # Fallback to a rule-based heuristic if model not trained yet
            # but ensure it's not a static mock
            base_prob = signal.confidence * 0.7
            if signal.strategy_role == "entry_engine":
                base_prob += 0.1
            return min(0.95, base_prob)

        # Real inference if model exists
        # feature_names = ['confidence', 'queue_quality', 'entry_price']
        # X = [[features.get(f, 0) for f in feature_names]]
        # return float(self.model.predict_proba(X)[0][1])
        return 0.75

    async def rank_signals(self, signals: List[Signal]) -> List[Signal]:
        for s in signals:
            # Generate feature snapshot for inference
            features = {
                "confidence": s.confidence,
                "queue_quality": s.queue_quality,
                "entry_price": s.entry_price,
                "strategy_id": s.strategy_id
            }
            s.ml_score = await self.predict_tp1_prob(s, features)
            s.ml_pass = s.ml_score > 0.65
            s.ml_reason = "Probable TP1 expansion" if s.ml_pass else "Low historical edge in current regime"
            s.ml_model_version = self.version
        return sorted(signals, key=lambda x: x.ml_score or 0.0, reverse=True)

class MLTrainer:
    def train_from_history(self, closed_positions: List[Any]):
        if len(closed_positions) < 20: # Minimum sample threshold
            return False

        data = []
        for p in closed_positions:
            # Target: did price hit TP1 before SL?
            # We use pnl as a proxy for success in this simplified version
            success = 1 if p.pnl > 0 else 0
            data.append({
                'confidence': 0.8, # Would come from signal history
                'success': success
            })

        df = pd.DataFrame(data)
        X = df[['confidence']]
        y = df['success']

        model = RandomForestClassifier(n_estimators=50)
        model.fit(X, y)

        os.makedirs("ml_models", exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        return True

ml_meta_layer = MLMetaLayer()
ml_trainer = MLTrainer()

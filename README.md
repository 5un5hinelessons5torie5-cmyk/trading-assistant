# Commissioning-Grade Trading Workstation

A professional, supervised trading assistant focused on high-integrity signals, evidence-backed decisions, and operator control.

## Workflow
Market Scan -> Signal Identification -> Queue -> Operator Approval -> Broker Execution -> Position Management -> Journaling -> Analytics -> Validation Lab

## Features
- **Strategy Lab**: Scan for high-probability setups using multiple engines (EMA Pullback, Breakout Retest).
- **Execution Queue**: Disciplined trade entry with risk controls and manual approval.
- **Validation Lab**: Full historical backtesting engine with walk-forward Out-of-Sample (OOS) validation.
- **ML Meta-Layer**: Automatic model retraining from closed trades to rank and filter signals.
- **Operations Cockpit**: Real-time overview of system health, active presets, and portfolio state.
- **Journaling**: Record post-trade reflections, discipline scores, and identify pattern mistakes.

## Tech Stack
- **Backend**: FastAPI, SQLModel (SQLite), Scikit-Learn, Pandas.
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Broker**: First-class support for Exness (MT5) and built-in Paper broker.

## How to Run
1. **Install Dependencies**:
   ```bash
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install
   ```
2. **Start the Application**:
   ```bash
   ./start.sh
   ```
3. **Access the UI**:
   Open [http://localhost:5173](http://localhost:5173) in your browser.

## Reliability & Trust
- **Kill Switch**: Global emergency stop for all executions.
- **Risk Controls**: Max open positions and asset group exposure caps.
- **Audit Trail**: Every execution and signal is tracked with a detailed history.
- **Evidence-Driven**: Experiments must pass OOS winrate thresholds before promotion to "Active".

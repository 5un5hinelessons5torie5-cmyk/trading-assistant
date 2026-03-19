# ⚡️ Trading Workstation (Commissioning Grade)

A high-integrity, supervised trading workstation designed for individual operators who value evidence and trust over signal quantity.

## 🚀 Quick Start (Recommended)

To get the workstation up and running as quickly as possible:

1.  **Run Setup**: This installs all Python and Node dependencies.
    ```bash
    ./setup.sh
    ```
2.  **Start the Workstation**:
    ```bash
    ./start.sh
    ```
3.  **Open in Browser**:
    Go to: **[http://localhost:5173](http://localhost:5173)**

---

## 🛠 Key Components

### 1. Strategy Lab
Perform market scans using core engines:
- **EMA Pullback**: Identifies trend reclaim opportunities.
- **Breakout Retest**: Tracks volatility expansions.
- **Auto Best Setup**: Automatically finds the strongest setup across timeframes.

### 2. Execution Queue
Strict trade admission with mandatory operator approval.
- Built-in **Risk Sizing** (Volume normalization for Exness/MT5).
- **Duplicate Position Protection**.
- **Audit Trails** for every decision.

### 3. Validation Lab
Don't trust, verify.
- **Realistic Backtesting Engine**: Replay strategies over historical data with spread and commission models.
- **Walk-forward Validation**: Automatic split of In-Sample and Out-of-Sample (OOS) data.

### 4. ML Meta-Layer
- **Automatic Retraining**: The background scheduler periodically retrains a meta-model on your closed trade history.
- **Ranking & Filtering**: Signals are ranked by probability of success before entering the queue.

### 5. Position Management
- **Live MT5 Integration**: Connected to Exness via MT5 adapter.
- **Paper Broker**: Built-in environment for risk-free testing.
- **Management Loop**: Auto Break-even, Trailing Stops, and Target Ladders.

---

## 🛡 Reliability & Safety
- **Kill Switch**: Instant global trade blockage.
- **Exposure Caps**: Max open positions and Asset Group (Forex, Crypto, etc.) limits.
- **Journaling**: Integrated post-trade reflections and discipline scoring.
- **Backups**: One-click state export for system recovery.

## 🧰 Tech Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS.
- **Backend**: FastAPI (Python), SQLModel, Scikit-Learn (ML), Pandas.

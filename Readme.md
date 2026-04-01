🏎️ Slipstream — F1 Analytics Web App
> **Stack decision:** Plotly Dash (Python-only) · DuckDB · FastF1 · scikit-learn / XGBoost  
> Single-server architecture. No React. No separate API. Learn one thing at a time.
---
1. Architecture
```
Browser (Dash renders HTML/JS automatically)
        ↓  ↑  callbacks (Python functions, not REST)
  Dash Server (app.py)
        ↓
  Data Layer
    ├── FastF1  →  fetches from F1 API on first load
    └── DuckDB  →  persists laps/telemetry, skips API on subsequent loads
        ↓
  ML Layer
    └── scikit-learn / XGBoost models trained on DuckDB data
```
Why not FastAPI + React?  
Two servers, CORS config, JSON serialisation overhead, and two languages to debug simultaneously — all for a personal dashboard. Dash handles reactivity natively in Python. Add a FastAPI layer only if you want to expose a public API for other clients later.
---
2. Tech Stack
Frontend — Plotly Dash
What	Package	Notes
Web framework	`dash`	Reactive UI in pure Python
Layout components	`dash-bootstrap-components`	Bootstrap grid, dark/light themes
Charts	`plotly` (via `dash`)	Line, scatter, box, heatmap, subplots
In-memory state	`dcc.Store`	Share data between callbacks without re-fetching
> **The one JS you will write:** `clientside_callback` snippets for hover-sync between subplots. ~10 lines total, optional.
Backend — Python services
What	Package	Notes
F1 data	`fastf1 >= 3.3`	Telemetry, laps, strategy, weather
DataFrames	`pandas` + `polars`	pandas for FastF1 compat, polars for heavy queries
Analytical DB	`duckdb`	Columnar, fast GROUP BY, no server needed
DataFrame ↔ DB	`pyarrow`	Zero-copy bridge between pandas and DuckDB
Config	`python-dotenv`	Cache paths, DB path, debug flag
Logging	`loguru`	Drop-in replacement for stdlib logging
> **Why DuckDB over SQLite?**  
> DuckDB is columnar — it runs analytical queries (averages, window functions, GROUP BY) 10–50× faster than SQLite on lap-scale data. After 5 seasons you will have ~100k rows. SQLite gets slow. DuckDB does not.
ML Stack
What	Package
Core ML	`scikit-learn`
Gradient boosting	`xgboost`, `lightgbm`
Explainability	`shap`
Hyperparameter tuning	`optuna`
---
3. Project Structure
```
slipstream/
│
├── app.py                        # Entry point — run this
├── requirements.txt
├── .env.example                  # Copy to .env, set cache paths
│
├── data/
│   ├── loader.py                 # FastF1 wrapper — get_session(), get_laps(), get_telemetry()
│   ├── store.py                  # DuckDB layer — save_laps(), query_laps(), init_db()
│   ├── cache/                    # FastF1 disk cache (gitignore this, can reach 5GB+)
│   └── f1.duckdb                 # Created on first run (gitignore this too)
│
├── app/
│   ├── layout.py                 # Page structure — dropdowns, tabs, stat cards
│   ├── callbacks.py              # Reactive logic — all @callback functions
│   └── components/
│       └── charts.py             # Plotly figure functions — one function per chart type
│
└── ml/
    ├── models/                   # Trained model artefacts (.pkl, .json)
    │   └── tyre_deg.py           # Tyre degradation model class
    ├── notebooks/
    │   └── exploration.ipynb     # Sandbox — test everything here before wiring into app
    └── utils/
        └── features.py           # Shared feature engineering functions
```
Key naming rule: `app/components/` holds Pydantic/data schemas if you ever add them — not ML models. ML model artefacts live in `ml/models/`. The naming collision in the original spec caused confusion; this structure avoids it.
---
4. Module Reference
Data layer
Purpose	Module	Why this one
F1 telemetry + timing	`fastf1`	Only library with full telemetry access
Disk cache for FastF1	built into fastf1	`fastf1.Cache.enable_cache()` — call on startup
Analytical queries	`duckdb`	Columnar, in-process, SQL interface
DataFrames	`pandas`	FastF1 returns pandas; use polars for heavy transforms
App layer
Purpose	Module	Why this one
Web app + charts	`dash` + `plotly`	Python-native, no JS needed
UI components	`dash-bootstrap-components`	Grid, cards, dropdowns, themes
Cross-callback state	`dcc.Store`	Serialises DataFrames to browser memory
ML layer
Purpose	Module	Alternatives
Regression / classification	`scikit-learn`	—
Gradient boosting	`xgboost`	`lightgbm` (faster on large data)
Feature importance	`shap`	eli5 (simpler but less powerful)
Hyperparameter search	`optuna`	sklearn GridSearchCV (slower)
---
5. Development Phases
Phase 1 — Environment & first data · 2–3 days
Goal: Load one race session and print lap data in a notebook.
Tasks:
`pip install -r requirements.txt`
`cp .env.example .env`
Enable FastF1 cache (`fastf1.Cache.enable_cache('./data/cache')`)
Load 2023 Bahrain Race, inspect `session.laps` columns
Fetch one lap of telemetry, plot speed vs distance
You are done when you can answer: what do `LapTime`, `TyreLife`, `SpeedI1`, and `IsPersonalBest` mean?
> ⚠️ **Cache first.** Without the disk cache, every session re-downloads ~50 MB. Enable it before writing any other code.
---
Phase 2 — Persistent storage · 2 days
Goal: Never re-fetch a session you've already loaded.
Tasks:
`python -m data.store` — creates `data/f1.duckdb`
Call `save_laps()` after loading each session
Read data back with `query_laps()` — confirm FastF1 is not called
Write 3 raw SQL queries in the notebook (avg pace per driver, best lap, compound breakdown)
You are done when the notebook Task 2 cells run without any FastF1 API calls.
---
Phase 3 — Plotly charts · 3–4 days
Goal: Five working chart functions, each testable in isolation with `fig.show()`.
Build them in this order — each one introduces a new Plotly concept:
Sub-task	Chart	New concept
3A	Lap time box plot	`px.box`, categorical colour maps
3B	Speed / throttle / brake trace	`make_subplots`, shared x-axis
3C	Track map coloured by speed	`px.scatter` with continuous colour scale
3D	Tyre strategy timeline	`go.Bar` horizontal, stint grouping logic
3E	Lap delta between two drivers	`cumsum`, dual-driver merge
> **3D hint:** stint grouping is the trickiest piece of pandas in the project.  
> `(df['Compound'] != df['Compound'].shift()).cumsum()` gives you a stint ID column.
---
Phase 4 — Dash app · 3–4 days
Goal: Browser shows dropdowns, stat cards, and all 5 chart tabs with real data.
Tasks:
`python app.py` → open `http://localhost:8050`
Read `app/layout.py` fully before touching it
Wire Callback 5B first (Load button → `dcc.Store`) — everything else depends on it
Test: 2023 Bahrain Race → click Load → stat cards update?
Test: select driver + lap → speed trace renders?
Callback order to implement:
#	Callback	Key concept
1	Year → event dropdown	Chained `Input`/`Output`
2	Load button → `dcc.Store`	`State`, JSON serialisation
3	Store → stat cards	Multiple `Output` from one `Input`
4	Store → lap time chart	Reading from store
5	Driver + lap → telemetry charts	`State` + session reload from cache
> **Debugging tip:** open browser DevTools → Console tab while developing callbacks. Dash prints the full callback error there.
---
Phase 5 — ML: tyre degradation · 3–4 days
Goal: Train a model, plot degradation curves per compound, understand the output.
Tasks:
Load the `TyreDegradationModel` class from `ml/models/tyre_deg.py`
Fit on one race (Bahrain 2023 is a good baseline)
Plot SOFT / MEDIUM / HARD degradation curves with Plotly
Compare linear regression vs GBM — which handles the Soft cliff better?
Add a "Predictions" tab to the Dash app showing the curves
You are done when you can explain in plain language why the Soft curve drops faster than Hard — using your model's output as evidence.
---
Phase 6 — Polish & deploy · 3–5 days
Tasks:
Error handling in callbacks (`try/except`, user-facing error messages)
Loading spinners on slow callbacks (`dcc.Loading`)
Environment-based config (debug off in production)
Deploy backend to Render or Railway
Persistent DuckDB via mounted volume (or export to parquet and re-import on startup)
---
6. ML Side Quests
Difficulty is honest here — ordered by actual implementation complexity, not just concept familiarity.
🟢 Beginner
Driver consistency score  
Metric: `std()` of lap times per driver per stint, excluding SC and pit laps.  
Output: ranking table. One pandas `groupby` call.
Tyre degradation model (Phase 5)  
Predict lap time from tyre age and compound. Linear regression first, then GBM.  
Output: degradation curve per compound.
---
🟡 Intermediate
Lap time prediction  
Predict lap time from: compound, tyre life, lap number, air/track temp, fuel load estimate.  
Harder than it looks — SC laps and pit laps need filtering, fuel load is estimated not measured.
Race outcome predictor  
Inputs: grid position, team, circuit type, qualifying delta.  
Output: predicted finishing position (regression or ordinal classification).  
Train on 5+ seasons for meaningful signal.
Anomaly detection — safety car periods  
Lap time z-scores spike sharply during SC periods. Detect and annotate them automatically.  
Useful as a preprocessing step for every other model (SC laps corrupt degradation signal).
---
🔴 Advanced
Pit stop strategy optimizer  
Model undercut/overcut windows. Either a Bayesian simulation (tractable) or a Gymnasium RL environment (ambitious). Requires tyre degradation model as a component.
Driver style clustering  
K-means or UMAP on telemetry features: average braking point per corner, minimum corner speed, throttle application distance, DRS usage rate. Produces a "driving DNA" fingerprint per driver.
Lap time sequence forecasting  
LSTM or Temporal Fusion Transformer on stint sequences. Predicts the next lap time given the last N laps. Requires PyTorch. Most data-hungry model in the list — needs multiple seasons.
SHAP explainability dashboard  
Add a Dash tab that runs `shap.TreeExplainer` on the race outcome predictor and renders feature importance interactively. Bridges the ML and viz layers.
---
7. Key Decisions — Rationale
Decision	Choice	Why
Frontend framework	Dash	Python-only, no JS build toolchain, reactive callbacks replace REST endpoints
Database	DuckDB	Columnar for analytical queries; 10–50× faster than SQLite on GROUP BY at lap scale
No FastAPI	—	Redundant with Dash's server; add only if you want a public API for other consumers

Cache early	FastF1 disk cache	Without it, each session costs ~50 MB + 30s download. Blocks fast iteration.
Charts in isolation	`charts.py` functions	Each `make_X()` returns a `go.Figure`, testable with `fig.show()` in notebooks
`dcc.Store` for state	In-memory store	Serialise once on load; all callbacks read from store, not from FastF1
---
8. Prerequisites
Python / Data
pandas `groupby`, `merge`, `cumsum`
Basic SQL (SELECT, WHERE, GROUP BY, window functions)
matplotlib enough to read a plot — Plotly will feel familiar
Dash / Plotly
How `@callback` with `Input` / `Output` / `State` works
What `dcc.Store` is and why it exists
Difference between `px` (express, quick) and `go` (graph objects, flexible)
ML
Train / test split, cross-validation, MAE/RMSE
What overfitting looks like on a learning curve
One-hot encoding for categorical features
---
9. High-Impact Features (priority order)
Driver comparison — lap-by-lap delta between any two drivers
Tyre degradation curves — per compound, per circuit, with model overlay
Strategy strip — stint timeline coloured by compound for all drivers
Track map — circuit coloured by speed, corner by corner
Animated race replay — position by lap (stretch goal, requires careful data prep)
Strategy simulator — 1-stop vs 2-stop lap time delta (ML-driven)
---
10. Development Principles
Cache before anything else. A 30-second load per session kills iteration speed.
Build charts in notebooks first. Wire into Dash only when `fig.show()` looks right.
One callback at a time. Implement, test, commit. Don't wire all callbacks at once.
SC laps corrupt your models. Filter them out in every ML feature pipeline — not just the degradation model.
Start with one season. Get the full pipeline working for 2023 before loading all history.
DuckDB is your friend after data is stored. SQL is faster to write than pandas chains for multi-session aggregations.
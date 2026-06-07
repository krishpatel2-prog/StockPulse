
# StockPulse 📈

StockPulse is an enterprise-grade financial intelligence and predictive market modeling dashboard designed to construct a multi-factor investment signal payload. The platform dynamically bridges the gap between pure technical data, consensus-driven predictive betting markets, deep-learning institutional text parsing, and public dialogue trends.

By processing asynchronous quantitative pipelines and text streams in parallel, StockPulse normalizes cross-platform dataset variables into singular, actionable market signals (`STRONG BUY`, `BUY`, `HOLD`, `SELL`, `STRONG SELL`) backed by statistical confidence scores.




https://github.com/user-attachments/assets/1f9954ac-c690-44e1-95b5-a5bece1d054a




---

## 🛠️ System Architecture & Data Flow

StockPulse operates via a highly decoupled, asynchronously optimized architecture consisting of a processing backend engine and an analytical terminal layout.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Streamlit Frontend UI                         │
│   (Custom Dark-Mode Grid Metrics, Plotly Subplots, Real-Time Logs)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Asynchronous HTTP Requests)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                             FastAPI Gateway                            │
│           (Query Validation Matrices & 5-Min Global TTL Cache)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│  DATA LAYER  │             │  NLP ENGINE  │             │SCORING ENGINE│
└──────────────┘             └──────────────┘             └──────────────┘
 • yfinance API               • FinBERT Local              • Asymmetric 
 • Polymarket Ingest            Transformer                  Weighting
 • Custom Scrapers            • Gemini Router              • tanh Velocity

```

1. **Ingestion Layer:** Gathers absolute pricing metrics, prediction contract states, and text data from live endpoints.


2. **AI Processing Layer:** Performs text transformations via a dedicated financial NLP model and filters irrelevant topics using an LLM router.


3. **Synthesis Layer:** Compresses multi-factor data streams through specialized mathematical functions ($\text{log1p}$, $\tanh$) into an asset-blending model.


4. **Presentation Layer:** Mounts the final unified data payloads onto a custom dark-theme dashboard.



---

## 🚀 Deep-Dive Feature Specifications

### 1. Quantitative Technical Analytics Engine

* **Vectorized Technical Formulations:** Communicates directly with Yahoo Finance (`yfinance`) to build point-in-time Open, High, Low, Close, and Volume (OHLCV) timeseries arrays, overlaying advanced indicators:


* **RSI (Relative Strength Index):** Computed using an Exponential Moving Average (`ewm`) mapping over a strict 14-period lookback window.


* **MACD (Moving Average Convergence Divergence):** Implements fast (12) and slow (26) EMAs paired with a 9-period signal histogram vector.


* **Bollinger Bands:** Projects structural macro boundaries via a 20-period rolling Simple Moving Average (SMA) flanked by standard deviation offsets ($\pm2.0\sigma$).


* **Baseline Trend Lines:** Tracks broader market trajectory by continuously managing 7-day, 21-day, and 50-day SMAs.




* **Intraday Boundary Handling:** To avoid rigid third-party API rate limits and data clipping, the module dynamically manages data requests, capping intraday bars (`5m`, `15m`, `30m`) to a 59-day maximum threshold and hourly (`1h`) windows to 729 days.



### 2. Prediction Market Synthesis Engine

* **Polymarket Extraction Array:** Connects to the Gamma API to discover, clean, and process active macroeconomic and asset-specific predictive events.


* **Liquidity & Noise Filtration:** Excludes uninformative or illiquid market data by automatically ignoring contracts with less than a $50 order-book liquidity floor. It also drops fully decided markets where probabilities float at extreme levels ($<0.02$ or $>0.98$).


* **Directional Logic Parsing:** Uses specialized regular expression mapping to dissect free-form contract questions containing terms like `above`, `below`, `range`, `hit_high`, and `hit_low`. This ensures YES/NO betting tokens are translated correctly into absolute directional sentiment.


* **At-The-Money (ATM) Band Isolation:** Targets high-uncertainty consensus zones where the probability floats directly between 35% and 65% YES, successfully extracting pure signals from complex, multi-tiered contract trees.



### 3. Dual-Layer AI Sentiment Infrastructure

* **Institutional NLP Subsystem:** Routes scraped financial news headlines through a locally managed HuggingFace pipeline running **ProsusAI/finbert**—a BERT model explicitly optimized for financial language sequence analysis.


* **Contextual Heuristic Rules:** Overlays custom rule maps to catch and correct edge-case model misinterpretations, such as re-evaluating consumer price hikes or subscription pricing surges from "positive text sentiment" back to an accurate bearish market contraction vector.


* **LLM Filtering Layer:** Leverages the `gemini-2.5-flash` runtime model to act as an intelligent context router, reading raw predictive market structures to strip out non-financial elements (such as sports or pop-culture events) before they reach core calculation models.


* **Public Mood Harvesting Pipeline:** Scrapes public dialogue real-time using custom-built parsing tools. If client-side platform limits block standard scrapers, it cascades gracefully into a secondary layout structure (`old.reddit.com` ingestion) while executing regex cleaning rules to eliminate spam triggers (`pump`, `airdrop`, `100x`).



### 4. Multi-Factor Blending & Scoring Engine

* **Asymmetric Weighting Configuration:** Synchronizes structural indicators into a unified market payload using a mathematically balanced model:

$$\text{Final Score} = (\text{Polymarket Score} \times 0.45) + (\text{News Sentiment} \times 0.30) + (\text{Technical Score} \times 0.25)$$



* **Compressive Volume Weighting:** Uses a log-transformed volume vector ($\text{log1p}$) to scale crowd indicators elegantly, ensuring single whale events do not introduce artificial volatility into the score.


* **Hyperbolic Confidence Calibration:** Smooths out public engagement tracking using a hyperbolic tangent ($\tanh$) function to model genuine crowd velocity against a stable volume-factor ceiling.



---

## 📊 Core API Endpoints

All data processing is exposed via structured REST endpoints built on FastAPI:

| Endpoint | Method | Operational Focus |
| --- | --- | --- |
| `/api/signal` | `GET` | Evaluates absolute technical metrics, prediction indexes, and text analysis to export localized trade executions and model certainty.

 |
| `/api/kpis` | `GET` | Compiles core asset data points including spot values, percentage deltas, RSI states, and structural moving average lines.

 |
| `/api/price-history` | `GET` | Exposes raw OHLCV timeseries datasets enriched with vectorized mathematical analytics indicators.

 |
| `/api/sentiment` | `GET` | Streams text data outputs showing specific confidence indexes computed by FinBERT and public data harvesting.

 |
| `/api/polymarket` | `GET` | Ingests asset keywords to map real-time predictive probabilities, protected by a 5-minute TTL cache layer.

 |

---

## 💻 Tech Stack Specifications

* **Backend Environment:** FastAPI, PyTorch, HuggingFace Transformers, Google GenAI SDK.


* **Data Processing Layer:** Pandas, NumPy, Vectorized Lookbacks.


* **Visualization Engine:** Plotly (Candlestick overlays, volume subplots).


* **UI Interface:** Streamlit (Custom premium dark-theme CSS injection framework).



---

## 📦 Installation & Local Configuration

### 1. Pre-requisites

Ensure your local system runs Python 3.10+ and has access to environment configurations.

### 2. Environment Provisioning

```bash
# Clone project repository
git clone https://github.com/rajhodedara/stockpulse.git
cd stockpulse

# Deploy required technical dependencies
pip install -r requirements.txt

```

### 3. Environment Variable Injection

Create a `.env` file in the project's root folder to map your API keys:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here

```

### 4. Running the Application

Launch the processing backend and terminal interfaces in separate terminal paths:

```bash
# Terminal Step 1: Initialize the FastAPI Gateway
python backend/main.py

# Terminal Step 2: Initialize the Streamlit Frontend Terminal
streamlit run frontend/app.py

```

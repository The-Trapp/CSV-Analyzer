# 📊 AI-Powered CSV Visualizer & Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google GenAI](https://img.shields.io/badge/Google%20GenAI-Gemini%20Flash-4285F4.svg)](https://aistudio.google.com/)
[![Altair](https://img.shields.io/badge/Visualization-Altair-brightgreen.svg)](https://altair-viz.github.io/)

An intelligent, interactive tabular data visualization web application. Upload any CSV file, ask questions in natural language, and let Gemini automatically analyze schemas, follow domain-specific charting skills, and generate interactive Altair visualizations.

---

## ✨ Features

- **Any CSV Ingestion:** Upload arbitrary CSV files (up to 10MB) or choose from built-in sample datasets (Café Tips, Medical Insurance).
- **Automatic Schema Extraction:** Extracts columns, types, null counts, and sample values without exposing the entire dataset over the wire.
- **Skill-Guided Visualization:** Gemini reads a dedicated visualization skill ([`skills/csv-visualization/SKILL.md`](skills/csv-visualization/SKILL.md)) to enforce best design practices (chart selection, unit labeling, non-null handling).
- **Self-Healing Code Execution:** Evaluates Altair code locally inside an isolated namespace. If execution fails, errors are fed back into Gemini's tool loop for an automatic repair attempt.
- **Interactive Altair Charts:** Fully responsive charts with hover tooltips, zoom/pan capabilities, and stretch width.
- **Code & Trace Transparency:** Expandable panels allow inspecting the generated Python code and viewing the agent's complete tool execution trace.
- **Personal Website Embeddable:** Configured for cross-origin iframe embedding on personal portfolios or blogs.

---

## 🚀 How to Run Locally

### Option A: Using `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/csv-analyzer.git
cd csv-analyzer

# Create environment and run
uv sync
uv run streamlit run app.py
```

### Option B: Using Standard Python `pip`

```bash
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up your environment key (or input in the app sidebar)
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY

# Run the app
streamlit run app.py
```
---

## 🐳 Docker Deployment

For self-hosting on your own VPS, Render, Railway, or Fly.io:

```bash
# Build Docker image
docker build -t csv-analyzer .

# Run container
docker run -p 8501:8501 -e GEMINI_API_KEY="your_api_key" csv-analyzer
```
Access at `http://localhost:8501`.

---

## 📂 Project Structure

```text
CSV Analyzer/
├── .streamlit/
│   ├── config.toml               # Server, theme, and CORS configuration
│   └── secrets.toml.example      # Streamlit secrets reference template
├── data/
│   ├── cafe.csv                  # 15-row sample cafe transactions dataset
│   └── insurance.csv             # 40-row sample medical insurance dataset
├── skills/
│   └── csv-visualization/
│       └── SKILL.md              # Charting skill guidelines for Gemini
├── .env.example                  # Environment variables template
├── .gitignore                    # Ensures API keys and caches are never committed
├── app.py                        # Main Streamlit application
├── Dockerfile                    # Containerization for web deployments
├── pyproject.toml                # Project metadata and dependencies
├── README.md                     # Documentation
└── requirements.txt              # Pip requirements for cloud deployment
```
---

## 🔒 Security & Privacy

- **No Data Persistence:** Uploaded CSVs are stored in memory only during the active browser session and never saved to a database or disk.
- **Client Key Isolation:** Visitors can provide their own Gemini API key in the sidebar if they prefer.
- **Safe Execution:** Chart execution explicitly checks for and prevents execution of forbidden operations (`os`, `sys`, `subprocess`, `open`).


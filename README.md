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

## 🌐 Deploy Constantly 24/7 for Free (Streamlit Cloud)

The fastest and easiest way to keep this app running constantly on the web for your portfolio or personal website:

1. **Push this folder to a new GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI CSV Analyzer"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Community Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
   - Click **New app**.
   - Select your repository, branch (`main`), and set the main file path to `app.py`.
   - Click **Advanced settings** -> **Secrets** and paste:
     ```toml
     GEMINI_API_KEY = "your_actual_gemini_api_key_here"
     GEMINI_MODEL = "gemini-flash-latest"
     ```
   - Click **Deploy!**

Your app is now live 24/7 at `https://<your-app-name>.streamlit.app`!

---

## 💻 Embed on Your Personal Website

To embed your live CSV Analyzer directly into any page of your personal website, portfolio, or blog, add this `<iframe>` snippet to your HTML:

```html
<div style="width: 100%; max-width: 1200px; margin: 0 auto;">
  <iframe
    src="https://<your-app-name>.streamlit.app/?embed=true"
    width="100%"
    height="850px"
    frameborder="0"
    style="border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
    allow="clipboard-write"
  ></iframe>
</div>
```

*(Replace `<your-app-name>` with your actual deployed Streamlit URL).*

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
- **Client Key Isolation:** Visitors can provide their own Gemini API key in the sidebar if you prefer not to use your own cloud secret.
- **Safe Execution:** Chart execution explicitly checks for and prevents execution of forbidden operations (`os`, `sys`, `subprocess`, `open`).


"""AI-Powered CSV Visualizer & Analyzer

A production-ready Streamlit application that allows users to upload any CSV,
ask natural-language questions, and receive publication-ready Altair charts
generated using Gemini tools and charting skills.
"""

import os
from pathlib import Path
import re
import time

import altair as alt
from dotenv import load_dotenv
from google import genai
from google.genai import types
import numpy as np
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Environment & Secrets Setup
# -----------------------------------------------------------------------------
APP_DIR = Path(__file__).parent.resolve()
load_dotenv(APP_DIR / ".env")
load_dotenv(APP_DIR / "key.env")

# Check Streamlit Cloud secrets first, then environment variables
HOSTED_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        HOSTED_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not HOSTED_KEY:
    HOSTED_KEY = os.getenv("GEMINI_API_KEY", "")

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# -----------------------------------------------------------------------------
# 2. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-Powered CSV Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 AI-Powered CSV Visualizer & Analyzer")
st.markdown(
    "Upload any tabular dataset, ask analytical questions in plain English, and let **Gemini** "
    "follow expert visualization skills to write, verify, and render interactive Altair charts."
)

# -----------------------------------------------------------------------------
# 3. Sidebar: Configuration, Secrets & Guidance
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings & Info")

    active_api_key = HOSTED_KEY

    # If no key is configured on the host/secrets, prompt the user
    if not HOSTED_KEY:
        st.info("💡 **API Key Required:** To run charts, enter a Gemini API Key below.")
        user_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            help="Get a free API key at https://aistudio.google.com/",
        )
        if user_key:
            active_api_key = user_key
        st.markdown(
            "[👉 Get a free Gemini API key](https://aistudio.google.com/)"
        )
    else:
        st.success("✅ Gemini API Key connected")
        with st.expander("🔑 Override API Key", expanded=False):
            custom_key = st.text_input(
                "Use custom API Key",
                type="password",
                help="Optional: Override the server default API key with your own.",
            )
            if custom_key:
                active_api_key = custom_key

    st.divider()
    st.markdown("### 🤖 Model Selection")
    env_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    popular_models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.8-pro",
        "gemini-flash-latest",
    ]
    if env_model in popular_models:
        default_idx = popular_models.index(env_model)
    else:
        popular_models.insert(0, env_model)
        default_idx = 0

    selected_model = st.selectbox(
        "Gemini Model",
        options=popular_models,
        index=default_idx,
        help="If a model is overloaded (503), the app automatically retries with fallbacks.",
    )

    st.divider()
    st.markdown("### 📋 Specs & Limits")
    st.markdown(
        """
        - **Max File Size:** 10 MB
        - **Supported Format:** UTF-8 CSV
        - **Engine:** Google GenAI (`google-genai` SDK)
        - **Chart Library:** Altair (Vega-Lite)
        - **Repair:** Automatic error feedback loop
        """
    )

    st.divider()
    st.markdown("### 💡 Example Prompts")
    st.caption("**Café Tips Dataset:**")
    st.markdown("• *What is the average tip for each day?*")
    st.markdown("• *How is total bill related to tip?*")
    st.caption("**Medical Insurance Dataset:**")
    st.markdown("• *Compare average charges between smokers and non-smokers across regions.*")
    st.markdown("• *Show the distribution of BMI across age groups.*")


# -----------------------------------------------------------------------------
# 4. Session State Management
# -----------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "dataset_id": None,
        "chart": None,
        "code": None,
        "explanation": None,
        "error": None,
        "tool_trace": [],
        "repair_count": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def clear_analysis_state():
    st.session_state.chart = None
    st.session_state.code = None
    st.session_state.explanation = None
    st.session_state.error = None
    st.session_state.tool_trace = []
    st.session_state.repair_count = 0


init_session_state()

# -----------------------------------------------------------------------------
# 5. Data Selection & Loading
# -----------------------------------------------------------------------------
data_source = st.radio(
    "Select data source:",
    options=[
        "Upload a CSV file",
        "Sample 1: Café Tips (15 rows)",
        "Sample 2: Medical Insurance (40 rows)",
    ],
    horizontal=True,
)

df = None
current_dataset_id = None

if data_source == "Upload a CSV file":
    uploaded_file = st.file_uploader(
        "Upload a CSV file (up to 10MB)",
        type=["csv"],
        help="Upload an ordinary UTF-8 CSV dataset.",
    )
    if uploaded_file is not None:
        current_dataset_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File exceeds the 10MB limit. Please upload a smaller CSV.")
        else:
            try:
                df = pd.read_csv(uploaded_file)
                if df.empty:
                    st.error("The uploaded CSV is empty.")
                    df = None
            except pd.errors.EmptyDataError:
                st.error("The uploaded file contains no data.")
            except pd.errors.ParserError as pe:
                st.error(f"Failed to parse CSV: {pe}")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

elif data_source == "Sample 1: Café Tips (15 rows)":
    sample_path = APP_DIR / "data" / "cafe.csv"
    if sample_path.exists():
        current_dataset_id = "sample_cafe.csv"
        df = pd.read_csv(sample_path)
    else:
        st.error(f"Sample file not found at {sample_path}.")

elif data_source == "Sample 2: Medical Insurance (40 rows)":
    sample_path = APP_DIR / "data" / "insurance.csv"
    if sample_path.exists():
        current_dataset_id = "sample_insurance.csv"
        df = pd.read_csv(sample_path)
    else:
        st.error(f"Sample file not found at {sample_path}.")

# Reset cached analysis if dataset changed
if current_dataset_id != st.session_state.dataset_id:
    st.session_state.dataset_id = current_dataset_id
    clear_analysis_state()

if df is None:
    st.info("👆 Upload a CSV or select one of the built-in sample datasets to get started.")
    st.stop()


# -----------------------------------------------------------------------------
# 6. Data Preview & Schema Inspection
# -----------------------------------------------------------------------------
st.subheader("📋 Dataset Preview & Schema")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", f"{len(df.columns)}")
missing_cells = int(df.isna().sum().sum())
col3.metric("Missing Values", f"{missing_cells}")
col4.metric("Memory Usage", f"{df.memory_usage().sum() / 1024:.1f} KB")

with st.expander("🔍 View Data Preview & Column Schema", expanded=True):
    st.dataframe(df.head(100), width="stretch")

    schema_summary = pd.DataFrame(
        {
            "Data Type": df.dtypes.astype(str),
            "Non-Null Count": df.notnull().sum(),
            "Null Count": df.isnull().sum(),
            "Unique Values": df.nunique(),
            "Sample Values": [
                str(df[col].dropna().unique()[:3].tolist()) for col in df.columns
            ],
        }
    )
    st.caption("**Column Schema Summary:**")
    st.dataframe(schema_summary, width="stretch")


# -----------------------------------------------------------------------------
# 7. Schema Description for Gemini Prompt
# -----------------------------------------------------------------------------
def build_dataset_description(dataframe: pd.DataFrame) -> str:
    """Format column names, types, null counts, and examples for Gemini."""
    lines = [
        f"The uploaded dataset contains {len(dataframe)} rows and {len(dataframe.columns)} columns.",
        "Available columns and summary statistics:",
    ]
    for col in dataframe.columns:
        dtype = str(dataframe[col].dtype)
        null_count = int(dataframe[col].isna().sum())
        non_null_count = int(dataframe[col].count())
        sample_vals = dataframe[col].dropna().unique()[:4].tolist()
        lines.append(
            f"- Column '{col}' (type: {dtype}): {non_null_count} non-null values, "
            f"{null_count} missing values. Sample distinct values: {sample_vals}"
        )
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# 8. Tools: Skill Loading & Safe Altair Execution
# -----------------------------------------------------------------------------
SKILL_PATH = APP_DIR / "skills" / "csv-visualization" / "SKILL.md"


def read_skill() -> str:
    """Read the instructions and best practices for creating quality Altair charts."""
    st.session_state.tool_trace.append({"tool": "read_skill"})
    if SKILL_PATH.exists():
        return SKILL_PATH.read_text(encoding="utf-8")
    return (
        "Chart creation guidelines:\n"
        "- Choose bar chart for category comparisons, scatter for numeric correlations.\n"
        "- Use exact column names.\n"
        "- Label axes clearly with units and aggregations.\n"
        "- Drop null values for plotted columns rather than treating missing as zero.\n"
        "- Assign the completed chart to variable `chart`."
    )


def sanitize_code(code: str) -> str:
    """Strip markdown backticks, fences, and whitespace."""
    code = code.strip()
    match = re.search(r"```(?:python)?\s*(.*?)\s*```", code, re.DOTALL)
    if match:
        return match.group(1).strip()
    return code


def create_chart(code: str) -> dict:
    """Execute Altair code using the uploaded DataFrame and report success or failure.

    Args:
        code: Python code that uses `df` and `alt` and assigns an Altair chart to `chart`.
    """
    clean_code = sanitize_code(code)
    st.session_state.tool_trace.append(
        {"tool": "create_chart", "code": clean_code}
    )

    # Security check for untrusted execution
    forbidden = ["import os", "import sys", "subprocess", "__import__", "eval(", "exec(", "open("]
    for bad in forbidden:
        if bad in clean_code:
            err_msg = f"Security restriction: '{bad}' is forbidden in visualization code."
            return {"ok": False, "error": err_msg}

    # Execution namespace
    local_vars = {
        "df": df,
        "alt": alt,
        "pd": pd,
        "np": np,
    }

    try:
        exec(clean_code, local_vars)
    except Exception as exc:
        st.session_state.repair_count += 1
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {str(exc)}",
            "suggestion": "Check column names, Altair syntax, or data transformations.",
        }

    chart_obj = local_vars.get("chart")
    if chart_obj is None:
        st.session_state.repair_count += 1
        return {
            "ok": False,
            "error": "The code executed but did not assign an Altair chart to variable `chart`.",
        }

    # Verify Altair spec
    try:
        chart_dict = chart_obj.to_dict()
        if not isinstance(chart_dict, dict) or not chart_dict:
            raise ValueError("chart.to_dict() returned an empty or invalid dictionary.")
    except Exception as exc:
        st.session_state.repair_count += 1
        return {
            "ok": False,
            "error": f"Invalid Altair chart specification: {exc}",
        }

    st.session_state.chart = chart_obj
    st.session_state.code = clean_code
    return {"ok": True, "message": "Chart successfully created and validated."}


# -----------------------------------------------------------------------------
# 9. Natural Language Question Interface
# -----------------------------------------------------------------------------
st.subheader("💬 Ask an Analytical Question")

col_q, col_quick = st.columns([3, 1])
question = col_q.text_input(
    "What would you like to visualize?",
    placeholder="e.g., What is the average tip for each day?",
    help="Enter an analytical question comparing categories, examining correlations, or viewing distributions.",
)

generate_clicked = st.button("🚀 Generate Chart", type="primary")

if generate_clicked:
    if not question.strip():
        st.warning("Please enter a question before clicking Generate Chart.")
    elif not active_api_key:
        st.error("Missing Gemini API Key. Please provide one in the sidebar.")
    else:
        clear_analysis_state()
        data_description = build_dataset_description(df)

        system_instruction = (
            "You are an expert data visualization assistant. "
            "Your goal is to answer the user's analytical question by generating an Altair chart.\n\n"
            "Workflow:\n"
            "1. ALWAYS call `read_skill()` first to load the charting guidelines.\n"
            "2. Review the provided dataset schema to identify column names and types.\n"
            "3. If the user asks about a column or concept NOT present in the dataset, "
            "   do NOT invent columns. Explain clearly why the question cannot be answered.\n"
            "4. If the question can be answered, generate pure Python Altair code and call "
            "   `create_chart(code=...)`. The code must assign the chart to `chart`.\n"
            "5. If `create_chart` returns an error, analyze the error, repair your code, "
            "   and call `create_chart` again (up to 1 repair attempt).\n"
            "6. Once the chart succeeds, provide a clear, concise summary answering the user's "
            "   question, mentioning any aggregations and noting how missing values were handled.\n"
        )

        prompt = (
            f"Dataset Schema and Summary:\n"
            f"{data_description}\n\n"
            f"User Question:\n"
            f"{question.strip()}\n\n"
            "Please read the charting skill and create an appropriate Altair visualization."
        )

        models_to_try = [selected_model]
        fallbacks = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.8-pro", "gemini-flash-latest"]
        for fb in fallbacks:
            if fb not in models_to_try:
                models_to_try.append(fb)

        response = None
        used_model = None
        last_error = None

        with st.spinner("🤖 Gemini is analyzing data, selecting chart type, and verifying code..."):
            client = genai.Client(api_key=active_api_key)

            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            tools=[read_skill, create_chart],
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                                maximum_remote_calls=8
                            ),
                        ),
                    )
                    used_model = m
                    break
                except Exception as err:
                    err_str = str(err)
                    last_error = err_str
                    # Check if error is 503 (high demand) or 404 (deprecated/not found)
                    is_unavailable = any(code in err_str for code in ["503", "404"]) or any(
                        k in err_str.lower() for k in ["high demand", "unavailable", "no longer available", "not found"]
                    )
                    if is_unavailable:
                        st.toast(
                            f"Model '{m}' is unavailable or retired. Trying next model...",
                            icon="🔄",
                        )
                        time.sleep(1.0)
                        continue
                    else:
                        break

            if response is not None:
                if used_model != selected_model:
                    st.info(f"ℹ️ Handled request using fallback model: `{used_model}` (Primary model `{selected_model}` was unavailable)")
                if response.text:
                    st.session_state.explanation = response.text
                if response.function_calls and not st.session_state.chart:
                    st.session_state.error = (
                        "Chart generation reached the call limit before completing. "
                        "Please try simplifying your question."
                    )
            else:
                st.session_state.error = (
                    f"API request error: {last_error}\n\n"
                    "Tip: High demand spikes are usually temporary. "
                    "Try switching the model in the sidebar (e.g. to `gemini-2.5-flash` or `gemini-2.0-flash`)."
                )


# -----------------------------------------------------------------------------
# 10. Display Results: Visualization, Analysis, Code & Trace
# -----------------------------------------------------------------------------
if st.session_state.error:
    st.error(f"❌ {st.session_state.error}")

if st.session_state.chart is not None:
    st.subheader("📈 Generated Visualization")
    st.altair_chart(st.session_state.chart, width="stretch")

    if st.session_state.explanation:
        st.markdown("### 📝 Analysis & Key Insights")
        st.markdown(st.session_state.explanation)

    with st.expander("💻 Inspect Generated Python Code", expanded=False):
        st.code(st.session_state.code, language="python")

    with st.expander("🛠️ Tool Trace & Agent Execution Details", expanded=False):
        st.caption(
            f"Total tool actions: {len(st.session_state.tool_trace)} | "
            f"Repairs attempted: {st.session_state.repair_count}"
        )
        for idx, item in enumerate(st.session_state.tool_trace, 1):
            st.markdown(f"**Step {idx}: `{item.get('tool')}`**")
            if "code" in item:
                st.code(item["code"], language="python")

elif st.session_state.explanation and not st.session_state.error:
    st.info(st.session_state.explanation)


---
name: csv-visualization
description: Expert guidelines for generating clean, accurate Altair visualizations from tabular data.
---

# CSV Visualization Skill Guidelines

Follow these principles when generating Python code for Altair charts based on tabular CSV data:

## 1. Plan Before Charting
- Review the available columns, data types, and non-null counts.
- Identify the user's analytical question and determine which variables, aggregations, or filters are required.
- If the question cannot be answered with the available columns, explain why clearly instead of inventing columns.

## 2. Choosing the Appropriate Chart Type
- **Categorical Comparisons (e.g., comparing averages or totals across categories):**
  - Use Bar Charts: `alt.Chart(df).mark_bar()`.
  - Place categories on X (or Y for horizontal bars when category labels are long) and metrics on the opposite axis.
- **Relationships Between Two Continuous Variables:**
  - Use Scatter Plots: `alt.Chart(df).mark_circle(size=60)` or `alt.Chart(df).mark_point()`.
- **Trends Over Time / Sequences:**
  - Use Line Charts: `alt.Chart(df).mark_line(point=True)`.
- **Distributions:**
  - Single numeric variable: Histogram `alt.Chart(df).mark_bar().encode(alt.X('col:Q', bin=True), alt.Y('count()'))`.
  - Numeric distribution across categories: Boxplot `alt.Chart(df).mark_boxplot()`.

## 3. Schema and Column Name Integrity
- Use ONLY the exact column names present in the dataset (case-sensitive, matching the schema).
- Always specify field types in Altair encodings:
  - `:Q` for quantitative (numeric continuous) data.
  - `:N` for nominal (categorical without ordering) data.
  - `:O` for ordinal (ordered categories) data.
  - `:T` for temporal (date/time) data.

## 4. Aggregations, Units, and Labels
- Always specify descriptive, human-readable axis titles with units when applicable (e.g., `alt.Y('mean(tip):Q', title='Average Tip ($)')`).
- Provide an informative chart title explaining what is displayed.
- Specify reasonable dimensions (e.g. `.properties(title="...", width=550, height=350)`).

## 5. Deliberate Handling of Missing Values
- **Never treat missing values as zero** unless explicitly instructed.
- When plotting variables that contain missing values, drop nulls for those specific columns first (e.g. `plot_df = df.dropna(subset=['column_name'])`) or note the exclusion in the summary.
- A missing value represents unrecorded data, not a zero measurement.

## 6. Code Execution Requirements
- The code must be pure Python that assigns the resulting Altair chart to a variable named `chart`.
- Available in the execution namespace:
  - `df`: the uploaded pandas DataFrame.
  - `alt`: the Altair module.
  - `pd`: the pandas module.
  - `np`: the numpy module.
- Do NOT call `chart.show()`, `st.altair_chart()`, or `plt.show()`.
- The code must be directly executable and assign `chart = ...`.


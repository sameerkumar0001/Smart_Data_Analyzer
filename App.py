%%writefile app.py
import os
import io
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Data Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize required session state variables so data persists across tabs."""
    if "original_df" not in st.session_state:
        st.session_state.original_df = None
    if "working_df" not in st.session_state:
        st.session_state.working_df = None
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = None
    if "filename" not in st.session_state:
        st.session_state.filename = None
    if "is_titanic_sample" not in st.session_state:
        st.session_state.is_titanic_sample = False

init_session_state()

# -----------------------------------------------------------------------------
# 2. REUSABLE HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def load_dataset(df, filename, is_titanic=False):
    """Store a newly loaded dataset into session state after basic validation."""
    if df is None or df.empty:
        st.error("The selected dataset is empty. Please upload a file containing valid rows and columns.")
        return False

    if df.columns.duplicated().any():
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [
                f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))
            ]
        df.columns = cols
        st.warning("Duplicate column names were detected and automatically renamed.")

    st.session_state.original_df = df.copy()
    st.session_state.working_df = df.copy()
    st.session_state.filtered_df = df.copy()
    st.session_state.filename = filename
    st.session_state.is_titanic_sample = is_titanic
    return True

def reset_working_dataset():
    """Restore the working dataset from the untouched original copy."""
    if st.session_state.original_df is not None:
        st.session_state.working_df = st.session_state.original_df.copy()
        st.session_state.filtered_df = st.session_state.original_df.copy()

def clear_all_data():
    """Completely clear session state."""
    st.session_state.original_df = None
    st.session_state.working_df = None
    st.session_state.filtered_df = None
    st.session_state.filename = None
    st.session_state.is_titanic_sample = False

def get_column_types(df):
    """Return lists of numerical and categorical/text columns."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    return num_cols, cat_cols

def fig_to_bytes(fig):
    """Convert a Matplotlib figure into PNG bytes for downloading."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    return buf.getvalue()

def check_data_loaded():
    """Verify if a dataset is available in session state before rendering a page."""
    if st.session_state.working_df is None:
        st.info("No dataset is currently loaded. Please go to **Home** or **Upload Dataset** to load a file first.")
        return False
    return True

# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & STATUS PANEL
# -----------------------------------------------------------------------------
st.sidebar.title("Smart Data Analyzer")
st.sidebar.caption("Interactive Data Analytics Platform")

sections = [
    "1. Home",
    "2. Upload Dataset",
    "3. Data Overview",
    "4. Data Cleaning",
    "5. Data Analysis",
    "6. Custom Charts",
    "7. Insights",
    "8. Download Results"
]

selected_section = st.sidebar.radio("Navigate to Section:", sections)

st.sidebar.markdown("---")
if st.session_state.working_df is not None:
    st.sidebar.success(f"**Loaded File:** {st.session_state.filename}")
    st.sidebar.write(f"**Current Rows:** {st.session_state.working_df.shape[0]}")
    st.sidebar.write(f"**Current Columns:** {st.session_state.working_df.shape[1]}")

    if st.sidebar.button("Reset to Original Dataset"):
        reset_working_dataset()
        st.sidebar.success("Working dataset restored to original state.")
        st.rerun()

    if st.sidebar.button("Unload Dataset"):
        clear_all_data()
        st.rerun()
else:
    st.sidebar.warning("Status: No Dataset Loaded")

# -----------------------------------------------------------------------------
# SECTION 1: HOME PAGE
# -----------------------------------------------------------------------------
if selected_section == "1. Home":
    st.title("Smart Data Analyzer – Interactive Data Analytics Platform")
    st.write(
        "Welcome to **Smart Data Analyzer**, a dynamic web application built with Python and Streamlit. "
        "This platform allows you to upload any tabular dataset, inspect its structure, clean missing or duplicate records, "
        "perform statistical analysis, build charts, filter records, and export your results without writing code."
    )

    st.subheader("Supported File Formats")
    st.markdown(
        "- **CSV Files (`.csv`)**\n"
        "- **Microsoft Excel Files (`.xlsx`)** (Supports multi-sheet selection)"
    )

    st.subheader("How to Use This Application")
    st.markdown(
        "1. **Upload Dataset:** Navigate to **Upload Dataset** to upload your own CSV/Excel file, or load the Titanic sample dataset below.\n"
        "2. **Data Overview:** Check total rows, columns, data types, missing values, and summary statistics.\n"
        "3. **Data Cleaning:** Handle missing values, drop duplicates, or convert column data types on a safe working copy.\n"
        "4. **Data Analysis:** Explore automatic numerical & categorical statistics, interactive data filtering, and automatic visual charts.\n"
        "5. **Custom Charts:** Build your own Bar, Line, Histogram, Scatter, or Pie charts and download them.\n"
        "6. **Insights:** Read automatically calculated factual observations from your dataset.\n"
        "7. **Download Results:** Export your cleaned dataset, filtered dataset, or statistical summary reports as CSV files."
    )

    st.subheader("Quick Start")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Option A: Load Sample Titanic Dataset (`data/train.csv`)**")
        sample_path = os.path.join("data", "train.csv")
        if os.path.exists(sample_path):
            if st.button("Load Titanic Sample Dataset"):
                try:
                    df_sample = pd.read_csv(sample_path)
                    if load_dataset(df_sample, "train.csv (Titanic Sample)", is_titanic=True):
                        st.success("Titanic sample dataset loaded! Use the sidebar to explore Data Overview, Cleaning, or Analysis.")
                except Exception as e:
                    st.error(f"Could not read sample file: {e}")
        else:
            st.info("Place `train.csv` inside the `data/` folder to enable one-click loading of the Titanic sample dataset.")

    with col2:
        st.markdown("**Option B: Upload Your Own Dataset**")
        st.write("Switch to **2. Upload Dataset** in the left sidebar to upload any custom CSV or Excel file.")

# -----------------------------------------------------------------------------
# SECTION 2: UPLOAD DATASET
# -----------------------------------------------------------------------------
elif selected_section == "2. Upload Dataset":
    st.title("Upload Dataset")
    st.write("Upload a CSV (`.csv`) or Excel (`.xlsx`) file to begin your analysis.")

    uploaded_file = st.file_uploader("Select a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        file_name = uploaded_file.name
        try:
            if file_name.lower().endswith(".csv"):
                try:
                    df_uploaded = pd.read_csv(uploaded_file)
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df_uploaded = pd.read_csv(uploaded_file, encoding="latin1")

                if load_dataset(df_uploaded, file_name, is_titanic=("train.csv" in file_name.lower())):
                    st.success(f"Successfully loaded **{file_name}**!")

            elif file_name.lower().endswith(".xlsx"):
                excel_file = pd.ExcelFile(uploaded_file, engine="openpyxl")
                sheet_names = excel_file.sheet_names
                selected_sheet = st.selectbox("Select Excel Sheet to Load:", sheet_names)
                if st.button("Load Selected Sheet"):
                    df_uploaded = pd.read_excel(uploaded_file, sheet_name=selected_sheet, engine="openpyxl")
                    display_name = f"{file_name} [{selected_sheet}]"
                    if load_dataset(df_uploaded, display_name, is_titanic=False):
                        st.success(f"Successfully loaded **{display_name}**!")

        except pd.errors.EmptyDataError:
            st.error("The uploaded file contains no data. Please upload a valid non-empty file.")
        except Exception as e:
            st.error(f"Unable to read file. Please check that the file is a valid CSV or Excel document. Details: {e}")

    if st.session_state.working_df is not None:
        st.markdown("---")
        st.subheader("Currently Active Dataset Summary")
        df_curr = st.session_state.working_df
        c1, c2, c3 = st.columns(3)
        c1.metric("Uploaded Filename", st.session_state.filename)
        c2.metric("Total Rows", df_curr.shape[0])
        c3.metric("Total Columns", df_curr.shape[1])
        st.dataframe(df_curr.head(5), use_container_width=True)

# -----------------------------------------------------------------------------
# SECTION 3: DATA OVERVIEW
# -----------------------------------------------------------------------------
elif selected_section == "3. Data Overview":
    st.title("Data Overview")
    if check_data_loaded():
        df = st.session_state.working_df
        num_cols, cat_cols = get_column_types(df)

        total_rows = df.shape[0]
        total_cols = df.shape[1]
        total_missing = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Total Rows", total_rows)
        k2.metric("Total Columns", total_cols)
        k3.metric("Numerical Columns", len(num_cols))
        k4.metric("Categorical Columns", len(cat_cols))
        k5.metric("Missing Values", total_missing)
        k6.metric("Duplicate Rows", duplicate_rows)

        st.markdown("---")
        st.subheader("Dataset Preview")
        preview_count = st.radio("Select number of preview rows:", [5, 10, 25], horizontal=True)
        st.dataframe(df.head(preview_count), use_container_width=True)

        st.markdown("---")
        st.subheader("Column Names, Data Types & Missing Value Summary")
        info_df = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Non-Null Count": df.notnull().sum().values,
            "Missing Count": df.isnull().sum().values,
            "Missing (%)": ((df.isnull().sum().values / max(total_rows, 1)) * 100).round(2),
            "Unique Values": [df[col].nunique(dropna=True) for col in df.columns]
        })
        st.dataframe(info_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Summary Statistics (`describe()`)")
        tab_num, tab_cat = st.tabs(["Numerical Summary", "Categorical / Object Summary"])
        with tab_num:
            if num_cols:
                st.dataframe(df[num_cols].describe().T, use_container_width=True)
            else:
                st.info("No numerical columns found in this dataset.")
        with tab_cat:
            if cat_cols:
                st.dataframe(df[cat_cols].describe().T, use_container_width=True)
            else:
                st.info("No categorical columns found in this dataset.")

        st.markdown("---")
        st.subheader("Full Dataset Table Explorer")
        st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------------------------
# SECTION 4: DATA CLEANING
# -----------------------------------------------------------------------------
elif selected_section == "4. Data Cleaning":
    st.title("Data Cleaning")
    if check_data_loaded():
        df = st.session_state.working_df
        orig_df = st.session_state.original_df

        st.write(
            "All cleaning actions are applied to a **separate working copy**. "
            "Your original uploaded dataset remains untouched and can be restored anytime."
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Working Rows", df.shape[0], delta=df.shape[0] - orig_df.shape[0])
        c2.metric("Working Columns", df.shape[1], delta=df.shape[1] - orig_df.shape[1])
        c3.metric("Remaining Missing Values", int(df.isnull().sum().sum()))
        c4.metric("Remaining Duplicates", int(df.duplicated().sum()))

        if st.button("Reset Working Dataset to Original"):
            reset_working_dataset()
            st.success("Working dataset has been reset to the original uploaded data.")
            st.rerun()

        st.markdown("---")
        st.subheader("Automatic Data Quality Diagnostics")
        missing_series = df.isnull().sum()
        cols_with_missing = missing_series[missing_series > 0]
        single_val_cols = [col for col in df.columns if df[col].nunique(dropna=False) <= 1]
        all_null_cols = [col for col in df.columns if df[col].isnull().all()]

        suspected_type_cols = []
        for col in df.select_dtypes(include=["object"]).columns:
            non_null = df[col].dropna()
            if len(non_null) > 0:
                converted = pd.to_numeric(non_null, errors="coerce")
                if converted.notnull().mean() > 0.8:
                    suspected_type_cols.append(col)

        d1, d2 = st.columns(2)
        with d1:
            if not cols_with_missing.empty:
                st.warning(f"**Columns with Missing Values ({len(cols_with_missing)}):**")
                st.dataframe(
                    pd.DataFrame({
                        "Column": cols_with_missing.index,
                        "Missing Count": cols_with_missing.values,
                        "Missing %": ((cols_with_missing.values / max(len(df), 1)) * 100).round(2)
                    }),
                    use_container_width=True
                )
            else:
                st.success("No missing values detected in any column.")

        with d2:
            st.write(f"- **Duplicate Rows Found:** `{int(df.duplicated().sum())}`")
            st.write(f"- **Columns with Only 1 Unique Value:** `{', '.join(single_val_cols) if single_val_cols else 'None'}`")
            st.write(f"- **Completely Empty Columns:** `{', '.join(all_null_cols) if all_null_cols else 'None'}`")
            st.write(f"- **Text Columns Likely Representing Numbers:** `{', '.join(suspected_type_cols) if suspected_type_cols else 'None'}`")

        if st.session_state.is_titanic_sample and {"Cabin", "Age", "Embarked"}.issubset(set(df.columns)):
            st.markdown("---")
            st.subheader("Titanic Original Report Cleaning Preset")
            st.caption("Apply the exact 3 steps from the Titanic EDA report: Drop 'Cabin' (687 missing), fill 'Age' (177 missing) with median, and fill 'Embarked' (2 missing) with mode.")
            if st.button("Apply Titanic Reference Cleaning"):
                temp_df = df.copy()
                if "Cabin" in temp_df.columns:
                    temp_df.drop(columns=["Cabin"], inplace=True)
                if "Age" in temp_df.columns:
                    temp_df["Age"] = temp_df["Age"].fillna(temp_df["Age"].median())
                if "Embarked" in temp_df.columns and not temp_df["Embarked"].mode().empty:
                    temp_df["Embarked"] = temp_df["Embarked"].fillna(temp_df["Embarked"].mode()[0])
                st.session_state.working_df = temp_df
                st.success("Applied Titanic reference cleaning: dropped Cabin, filled Age with median, filled Embarked with mode.")
                st.rerun()

        st.markdown("---")
        tab_miss, tab_dup, tab_dtype = st.tabs([
            "1. Handle Missing Values",
            "2. Remove Duplicates & Constant Columns",
            "3. Convert Data Types"
        ])

        with tab_miss:
            st.subheader("Missing Value Treatment")
            target_scope = st.selectbox(
                "Select Target Column (or apply to all applicable columns):",
                ["All Applicable Columns"] + df.columns.tolist()
            )
            miss_action = st.selectbox(
                "Choose Missing Value Action:",
                [
                    "Remove rows containing missing values",
                    "Remove columns containing missing values",
                    "Fill numerical missing values with Mean",
                    "Fill numerical missing values with Median",
                    "Fill categorical missing values with Mode",
                    "Fill missing values with a Custom Value"
                ]
            )

            custom_val = ""
            if miss_action == "Fill missing values with a Custom Value":
                custom_val = st.text_input("Enter Custom Value to Fill:")

            if st.button("Apply Missing Value Action"):
                new_df = df.copy()
                try:
                    if miss_action == "Remove rows containing missing values":
                        if target_scope == "All Applicable Columns":
                            new_df.dropna(axis=0, inplace=True)
                        else:
                            new_df.dropna(subset=[target_scope], inplace=True)
                        st.success("Removed rows with missing values.")

                    elif miss_action == "Remove columns containing missing values":
                        if target_scope == "All Applicable Columns":
                            cols_to_drop = new_df.columns[new_df.isnull().any()].tolist()
                            if cols_to_drop:
                                new_df.drop(columns=cols_to_drop, inplace=True)
                                st.success(f"Removed columns with missing values: {', '.join(cols_to_drop)}")
                            else:
                                st.info("No columns contained missing values.")
                        else:
                            new_df.drop(columns=[target_scope], inplace=True)
                            st.success(f"Removed column '{target_scope}'.")

                    elif miss_action == "Fill numerical missing values with Mean":
                        cols = [target_scope] if target_scope != "All Applicable Columns" else new_df.select_dtypes(include=[np.number]).columns.tolist()
                        filled_any = False
                        for c in cols:
                            if pd.api.types.is_numeric_dtype(new_df[c]) and not new_df[c].dropna().empty:
                                new_df[c] = new_df[c].fillna(new_df[c].mean())
                                filled_any = True
                        if filled_any:
                            st.success("Filled missing numerical values with column Mean.")
                        else:
                            st.warning("Selected column is not numerical or contains only missing values.")

                    elif miss_action == "Fill numerical missing values with Median":
                        cols = [target_scope] if target_scope != "All Applicable Columns" else new_df.select_dtypes(include=[np.number]).columns.tolist()
                        filled_any = False
                        for c in cols:
                            if pd.api.types.is_numeric_dtype(new_df[c]) and not new_df[c].dropna().empty:
                                new_df[c] = new_df[c].fillna(new_df[c].median())
                                filled_any = True
                        if filled_any:
                            st.success("Filled missing numerical values with column Median.")
                        else:
                            st.warning("Selected column is not numerical or contains only missing values.")

                    elif miss_action == "Fill categorical missing values with Mode":
                        cols = [target_scope] if target_scope != "All Applicable Columns" else new_df.columns.tolist()
                        filled_any = False
                        for c in cols:
                            mode_vals = new_df[c].mode(dropna=True)
                            if not mode_vals.empty:
                                new_df[c] = new_df[c].fillna(mode_vals[0])
                                filled_any = True
                        if filled_any:
                            st.success("Filled missing values with Mode (most frequent value).")
                        else:
                            st.warning("Could not compute mode because the target column is completely empty.")

                    elif miss_action == "Fill missing values with a Custom Value":
                        if custom_val == "":
                            st.warning("Please enter a custom value before clicking Apply.")
                        else:
                            cols = [target_scope] if target_scope != "All Applicable Columns" else new_df.columns.tolist()
                            for c in cols:
                                if pd.api.types.is_numeric_dtype(new_df[c]):
                                    try:
                                        val_to_fill = float(custom_val)
                                    except ValueError:
                                        val_to_fill = custom_val
                                else:
                                    val_to_fill = custom_val
                                new_df[c] = new_df[c].fillna(val_to_fill)
                            st.success(f"Filled missing values with '{custom_val}'.")

                    if new_df.empty:
                        st.error("Operation aborted because it would result in an empty dataset (0 rows).")
                    else:
                        st.session_state.working_df = new_df
                        st.rerun()
                except Exception as e:
                    st.error(f"Could not complete operation: {e}")

        with tab_dup:
            st.subheader("Duplicate Records & Single-Value Columns")
            dup_count = int(df.duplicated().sum())
            st.write(f"Current Duplicate Rows: **{dup_count}**")
            if st.button("Remove Duplicate Rows"):
                if dup_count > 0:
                    st.session_state.working_df = df.drop_duplicates().reset_index(drop=True)
                    st.success(f"Removed {dup_count} duplicate rows.")
                    st.rerun()
                else:
                    st.info("No duplicate rows to remove.")

            if single_val_cols:
                st.markdown("---")
                st.write(f"Columns with only 1 unique value: `{', '.join(single_val_cols)}`")
                if st.button("Drop Single-Value Columns"):
                    st.session_state.working_df = df.drop(columns=single_val_cols)
                    st.success("Dropped single-value columns.")
                    st.rerun()

        with tab_dtype:
            st.subheader("Convert Column Data Types")
            col_to_convert = st.selectbox("Select Column to Convert:", df.columns.tolist())
            current_dtype = str(df[col_to_convert].dtype)
            st.write(f"Current Data Type of **{col_to_convert}**: `{current_dtype}`")
            target_dtype = st.selectbox(
                "Convert To:",
                ["Numeric (Float/Int)", "Text / String (object)", "Categorical (category)", "Date/Time (datetime64)"]
            )
            if st.button("Convert Data Type"):
                new_df = df.copy()
                try:
                    if target_dtype == "Numeric (Float/Int)":
                        converted = pd.to_numeric(new_df[col_to_convert], errors="coerce")
                        if converted.isnull().all() and not new_df[col_to_convert].isnull().all():
                            st.error("Conversion failed: values in this column cannot be converted to numbers.")
                        else:
                            new_df[col_to_convert] = converted
                            st.session_state.working_df = new_df
                            st.success(f"Converted '{col_to_convert}' to Numeric.")
                            st.rerun()
                    elif target_dtype == "Text / String (object)":
                        new_df[col_to_convert] = new_df[col_to_convert].astype(str)
                        st.session_state.working_df = new_df
                        st.success(f"Converted '{col_to_convert}' to Text/String.")
                        st.rerun()
                    elif target_dtype == "Categorical (category)":
                        new_df[col_to_convert] = new_df[col_to_convert].astype("category")
                        st.session_state.working_df = new_df
                        st.success(f"Converted '{col_to_convert}' to Categorical.")
                        st.rerun()
                    elif target_dtype == "Date/Time (datetime64)":
                        converted = pd.to_datetime(new_df[col_to_convert], errors="coerce")
                        if converted.isnull().all():
                            st.error("Conversion failed: values in this column could not be parsed as dates.")
                        else:
                            new_df[col_to_convert] = converted
                            st.session_state.working_df = new_df
                            st.success(f"Converted '{col_to_convert}' to Date/Time.")
                            st.rerun()
                except Exception as e:
                    st.error(f"Could not convert column data type: {e}")

        st.markdown("---")
        st.subheader("Updated Working Dataset Preview")
        st.dataframe(st.session_state.working_df.head(15), use_container_width=True)

# -----------------------------------------------------------------------------
# SECTION 5: DATA ANALYSIS
# -----------------------------------------------------------------------------
elif selected_section == "5. Data Analysis":
    st.title("Data Analysis, Interactive Explorer & Automatic Charts")
    if check_data_loaded():
        df = st.session_state.working_df
        num_cols, cat_cols = get_column_types(df)

        tab_stats, tab_explorer, tab_autocharts = st.tabs([
            "1. Statistical Analysis",
            "2. Interactive Data Explorer (Filter & Search)",
            "3. Automatic Visualizations"
        ])

        with tab_stats:
            st.subheader("Numerical Column Statistics")
            if num_cols:
                num_stats_rows = []
                for col in num_cols:
                    series = df[col].dropna()
                    if len(series) > 0:
                        mode_series = series.mode()
                        mode_val = mode_series.iloc[0] if not mode_series.empty else np.nan
                        num_stats_rows.append({
                            "Column": col,
                            "Count": int(series.count()),
                            "Mean": round(float(series.mean()), 3),
                            "Median": round(float(series.median()), 3),
                            "Mode": round(float(mode_val), 3) if pd.notnull(mode_val) else np.nan,
                            "Minimum": round(float(series.min()), 3),
                            "Maximum": round(float(series.max()), 3),
                            "Std Deviation": round(float(series.std()), 3) if len(series) > 1 else 0.0
                        })
                if num_stats_rows:
                    st.dataframe(pd.DataFrame(num_stats_rows), use_container_width=True)
                else:
                    st.info("Numerical columns contain only missing values.")
            else:
                st.info("No numerical columns available for calculation.")

            st.markdown("---")
            st.subheader("Categorical Column Statistics")
            if cat_cols:
                cat_summary_rows = []
                for col in cat_cols:
                    series = df[col].dropna().astype(str)
                    total_valid = len(series)
                    if total_valid > 0:
                        vc = series.value_counts()
                        top_cat = vc.index[0]
                        top_freq = int(vc.iloc[0])
                        top_pct = round((top_freq / total_valid) * 100, 2)
                        cat_summary_rows.append({
                            "Column": col,
                            "Unique Categories": int(series.nunique()),
                            "Most Frequent Category": top_cat,
                            "Highest Frequency": top_freq,
                            "Top Category (%)": f"{top_pct}%"
                        })
                if cat_summary_rows:
                    st.dataframe(pd.DataFrame(cat_summary_rows), use_container_width=True)

                selected_cat = st.selectbox("Select a Categorical Column for Detailed Frequency Breakdown:", cat_cols)
                if selected_cat:
                    vc = df[selected_cat].dropna().astype(str).value_counts()
                    pct = (vc / max(len(df[selected_cat].dropna()), 1) * 100).round(2)
                    freq_table = pd.DataFrame({
                        "Category": vc.index,
                        "Frequency Count": vc.values,
                        "Percentage (%)": pct.values
                    })
                    st.dataframe(freq_table, use_container_width=True)
            else:
                st.info("No categorical columns available in this dataset.")

        with tab_explorer:
            st.subheader("Interactive Data Explorer")
            st.write("Filter your dataset dynamically using text search, categories, numerical ranges, or dates without altering the main working dataset.")

            filtered = df.copy()

            search_query = st.text_input("Keyword Search (searches across all columns):")
            if search_query.strip():
                mask = filtered.astype(str).apply(
                    lambda row: row.str.contains(search_query.strip(), case=False, na=False)
                ).any(axis=1)
                filtered = filtered[mask]

            col_f1, col_f2 = st.columns(2)

            with col_f1:
                st.markdown("**Categorical Filters**")
                filter_cats = st.multiselect("Select Categorical Columns to Filter:", cat_cols)
                for c in filter_cats:
                    unique_vals = filtered[c].dropna().unique().tolist()
                    selected_vals = st.multiselect(f"Values for `{c}`:", unique_vals, default=unique_vals)
                    filtered = filtered[filtered[c].isin(selected_vals)]

            with col_f2:
                st.markdown("**Numerical Range Filters**")
                filter_nums = st.multiselect("Select Numerical Columns to Filter:", num_cols)
                for c in filter_nums:
                    valid_num = filtered[c].dropna()
                    if not valid_num.empty:
                        min_v = float(valid_num.min())
                        max_v = float(valid_num.max())
                        if min_v < max_v:
                            r_min, r_max = st.slider(
                                f"Range for `{c}`:",
                                min_value=min_v,
                                max_value=max_v,
                                value=(min_v, max_v)
                            )
                            filtered = filtered[(filtered[c] >= r_min) & (filtered[c] <= r_max)]
                        else:
                            st.caption(f"Column `{c}` has constant value {min_v}.")

            date_cols = filtered.select_dtypes(include=["datetime64", "datetimetz"]).columns.tolist()
            if date_cols:
                st.markdown("**Date Range Filters**")
                for dc in date_cols:
                    valid_dates = filtered[dc].dropna()
                    if not valid_dates.empty:
                        min_d = valid_dates.min().date()
                        max_d = valid_dates.max().date()
                        if min_d < max_d:
                            start_d, end_d = st.date_input(f"Date range for `{dc}`:", value=(min_d, max_d))
                            filtered = filtered[(filtered[dc].dt.date >= start_d) & (filtered[dc].dt.date <= end_d)]

            st.session_state.filtered_df = filtered

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Matching Records", len(filtered))
            m2.metric("Total Working Records", len(df))
            pct_match = round((len(filtered) / max(len(df), 1)) * 100, 2)
            m3.metric("Percentage Matched", f"{pct_match}%")

            st.dataframe(filtered, use_container_width=True)

            if not filtered.empty and num_cols:
                with st.expander("View Summary Statistics of Filtered Records"):
                    st.dataframe(filtered[num_cols].describe().T, use_container_width=True)

            csv_filtered = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Filtered Dataset (CSV)",
                data=csv_filtered,
                file_name="filtered_dataset.csv",
                mime="text/csv"
            )

        with tab_autocharts:
            st.subheader("Automatic Data Visualizations")
            st.write("Charts below are automatically chosen and generated based on your dataset's column types.")

            plot_num_cols = [
                c for c in num_cols
                if df[c].dropna().nunique() > 1 and not c.lower().endswith("id")
            ]
            if not plot_num_cols and num_cols:
                plot_num_cols = [c for c in num_cols if df[c].dropna().nunique() > 1]

            plot_cat_cols = [
                c for c in cat_cols
                if 1 < df[c].dropna().nunique() <= 15
            ]

            c_left, c_right = st.columns(2)

            if plot_num_cols:
                target_num = plot_num_cols[0]
                with c_left:
                    st.markdown(f"**1. Distribution Histogram (`{target_num}`)**")
                    fig1, ax1 = plt.subplots(figsize=(6, 4))
                    sns.histplot(df[target_num].dropna(), kde=True, ax=ax1, color="#2b5c8f")
                    ax1.set_title(f"Histogram of {target_num}")
                    ax1.set_xlabel(target_num)
                    ax1.set_ylabel("Frequency")
                    st.pyplot(fig1)
                    plt.close(fig1)

                with c_right:
                    st.markdown(f"**2. Box Plot (`{target_num}`)**")
                    fig2, ax2 = plt.subplots(figsize=(6, 4))
                    sns.boxplot(x=df[target_num].dropna(), ax=ax2, color="#388e3c")
                    ax2.set_title(f"Box Plot of {target_num}")
                    ax2.set_xlabel(target_num)
                    st.pyplot(fig2)
                    plt.close(fig2)

            if plot_cat_cols:
                target_cat = plot_cat_cols[0]
                c_left2, c_right2 = st.columns(2)
                with c_left2:
                    st.markdown(f"**3. Categorical Count Plot (`{target_cat}`)**")
                    fig3, ax3 = plt.subplots(figsize=(6, 4))
                    order_vals = df[target_cat].dropna().astype(str).value_counts().index[:10]
                    sns.countplot(
                        data=df,
                        x=df[target_cat].astype(str),
                        order=order_vals,
                        ax=ax3,
                        palette="Blues_r"
                    )
                    ax3.set_title(f"Category Counts for {target_cat}")
                    ax3.set_xlabel(target_cat)
                    ax3.set_ylabel("Count")
                    plt.xticks(rotation=30, ha="right")
                    st.pyplot(fig3)
                    plt.close(fig3)

                with c_right2:
                    vc_pie = df[target_cat].dropna().astype(str).value_counts()
                    if len(vc_pie) <= 8:
                        st.markdown(f"**4. Proportion Pie Chart (`{target_cat}`)**")
                        fig4, ax4 = plt.subplots(figsize=(6, 4))
                        ax4.pie(vc_pie.values, labels=vc_pie.index, autopct="%1.1f%%", startangle=90)
                        ax4.set_title(f"Share of {target_cat}")
                        st.pyplot(fig4)
                        plt.close(fig4)

            if len(plot_num_cols) >= 2:
                c_left3, c_right3 = st.columns(2)
                with c_left3:
                    x_sc, y_sc = plot_num_cols[0], plot_num_cols[1]
                    st.markdown(f"**5. Scatter Plot (`{x_sc}` vs `{y_sc}`)**")
                    fig5, ax5 = plt.subplots(figsize=(6, 4))
                    sns.scatterplot(data=df, x=x_sc, y=y_sc, ax=ax5, alpha=0.7, color="#d95f02")
                    ax5.set_title(f"{y_sc} vs {x_sc}")
                    st.pyplot(fig5)
                    plt.close(fig5)

                with c_right3:
                    st.markdown("**6. Numerical Correlation Heatmap**")
                    corr_cols = plot_num_cols[:10]
                    corr_matrix = df[corr_cols].corr()
                    fig6, ax6 = plt.subplots(figsize=(6, 4))
                    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax6)
                    ax6.set_title("Correlation Matrix")
                    st.pyplot(fig6)
                    plt.close(fig6)

            if not plot_num_cols and not plot_cat_cols:
                st.warning("Not enough valid numerical or low-cardinality categorical columns to generate automatic charts.")

# -----------------------------------------------------------------------------
# SECTION 6: CUSTOM CHARTS
# -----------------------------------------------------------------------------
elif selected_section == "6. Custom Charts":
    st.title("Create Your Own Chart")
    if check_data_loaded():
        df = st.session_state.working_df
        num_cols, cat_cols = get_column_types(df)
        all_cols = df.columns.tolist()

        st.write("Select a chart type, choose your axes, and generate custom visualizations.")

        chart_type = st.selectbox(
            "Select Chart Type:",
            ["Bar Chart", "Line Chart", "Histogram", "Scatter Plot", "Pie Chart"]
        )

        col1, col2, col3 = st.columns(3)

        if chart_type == "Bar Chart":
            with col1:
                x_col = st.selectbox("Select X-Axis Column (Category):", all_cols)
            with col2:
                y_options = ["Count (Frequency)"] + num_cols
                y_col = st.selectbox("Select Y-Axis (Value or Count):", y_options)
            with col3:
                group_options = ["None"] + cat_cols
                group_col = st.selectbox("Grouping Column (Optional):", group_options)

        elif chart_type == "Line Chart":
            with col1:
                x_col = st.selectbox("Select X-Axis Column:", all_cols)
            with col2:
                y_col = st.selectbox("Select Y-Axis Column (Numerical):", num_cols if num_cols else ["None"])
            with col3:
                group_col = st.selectbox("Grouping Column (Optional):", ["None"] + cat_cols)

        elif chart_type == "Histogram":
            with col1:
                x_col = st.selectbox("Select Numerical Column:", num_cols if num_cols else ["None"])
            with col2:
                bins = st.slider("Number of Bins:", min_value=5, max_value=60, value=20)
            with col3:
                group_col = st.selectbox("Grouping Column (Optional):", ["None"] + cat_cols)

        elif chart_type == "Scatter Plot":
            with col1:
                x_col = st.selectbox("Select X-Axis (Numerical):", num_cols if num_cols else ["None"])
            with col2:
                default_y_idx = 1 if len(num_cols) > 1 else 0
                y_col = st.selectbox("Select Y-Axis (Numerical):", num_cols if num_cols else ["None"], index=default_y_idx)
            with col3:
                group_col = st.selectbox("Grouping / Color Column (Optional):", ["None"] + cat_cols)

        elif chart_type == "Pie Chart":
            with col1:
                x_col = st.selectbox("Select Category Column:", cat_cols if cat_cols else all_cols)
            with col2:
                top_n = st.slider("Maximum Slices to Display:", min_value=3, max_value=12, value=6)

        if st.button("Generate Custom Chart"):
            try:
                fig, ax = plt.subplots(figsize=(8, 5))
                hue_arg = None if (chart_type == "Pie Chart" or group_col == "None" or group_col == x_col) else group_col

                if hue_arg and df[hue_arg].nunique(dropna=True) > 12:
                    st.warning(f"Grouping column '{hue_arg}' has more than 12 unique categories. Grouping was skipped to keep the chart readable.")
                    hue_arg = None

                if chart_type == "Bar Chart":
                    if df[x_col].dropna().empty:
                        st.error(f"Column '{x_col}' contains only missing values.")
                    else:
                        top_categories = df[x_col].dropna().astype(str).value_counts().index[:15]
                        plot_data = df[df[x_col].astype(str).isin(top_categories)].copy()
                        plot_data[x_col] = plot_data[x_col].astype(str)

                        if y_col == "Count (Frequency)":
                            sns.countplot(data=plot_data, x=x_col, hue=hue_arg, order=top_categories, ax=ax)
                            ax.set_ylabel("Count")
                            ax.set_title(f"Bar Chart: Count by {x_col}")
                        else:
                            sns.barplot(data=plot_data, x=x_col, y=y_col, hue=hue_arg, order=top_categories, errorbar=None, ax=ax)
                            ax.set_ylabel(f"Average {y_col}")
                            ax.set_title(f"Bar Chart: Average {y_col} by {x_col}")
                        plt.xticks(rotation=35, ha="right")

                elif chart_type == "Line Chart":
                    if y_col == "None":
                        st.error("This dataset has no numerical columns for a Line Chart.")
                        st.stop()
                    plot_data = df[[x_col, y_col] + ([hue_arg] if hue_arg else [])].dropna()
                    if plot_data.empty:
                        st.error("No valid non-null data points available for the selected columns.")
                        st.stop()
                    sns.lineplot(data=plot_data, x=x_col, y=y_col, hue=hue_arg, ax=ax)
                    ax.set_title(f"Line Chart: {y_col} over {x_col}")
                    plt.xticks(rotation=30, ha="right")

                elif chart_type == "Histogram":
                    if x_col == "None":
                        st.error("This dataset has no numerical columns for a Histogram.")
                        st.stop()
                    plot_data = df[[x_col] + ([hue_arg] if hue_arg else [])].dropna()
                    if plot_data.empty:
                        st.error("Selected column contains only missing values.")
                        st.stop()
                    sns.histplot(data=plot_data, x=x_col, hue=hue_arg, bins=bins, kde=True, ax=ax)
                    ax.set_title(f"Histogram of {x_col}")

                elif chart_type == "Scatter Plot":
                    if x_col == "None" or y_col == "None":
                        st.error("At least one numerical column is required to build a Scatter Plot.")
                        st.stop()
                    cols_needed = list(dict.fromkeys([x_col, y_col] + ([hue_arg] if hue_arg else [])))
                    plot_data = df[cols_needed].dropna()
                    if plot_data.empty:
                        st.error("No overlapping non-null rows exist for the selected columns.")
                        st.stop()
                    sns.scatterplot(data=plot_data, x=x_col, y=y_col, hue=hue_arg, alpha=0.75, ax=ax)
                    ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")

                elif chart_type == "Pie Chart":
                    vc = df[x_col].dropna().astype(str).value_counts().head(top_n)
                    if vc.empty:
                        st.error("Selected column has no valid values to plot.")
                        st.stop()
                    ax.pie(vc.values, labels=vc.index, autopct="%1.1f%%", startangle=90)
                    ax.set_title(f"Pie Chart of {x_col} (Top {len(vc)} Categories)")

                st.pyplot(fig)

                chart_bytes = fig_to_bytes(fig)
                st.session_state["last_custom_chart"] = chart_bytes
                st.download_button(
                    label="Download Chart as PNG",
                    data=chart_bytes,
                    file_name=f"custom_{chart_type.lower().replace(' ', '_')}.png",
                    mime="image/png"
                )
                plt.close(fig)

            except Exception as e:
                st.error(f"Could not generate chart with the selected columns. Details: {e}")

# -----------------------------------------------------------------------------
# SECTION 7: DISCOVER INSIGHTS
# -----------------------------------------------------------------------------
elif selected_section == "7. Insights":
    st.title("Discover Insights")
    if check_data_loaded():
        df = st.session_state.working_df
        orig_df = st.session_state.original_df
        num_cols, cat_cols = get_column_types(df)

        st.subheader("Automatically Calculated Dataset Insights")
        insights = []

        total_cells = max(df.shape[0] * df.shape[1], 1)
        total_missing = int(df.isnull().sum().sum())
        completeness = round(((total_cells - total_missing) / total_cells) * 100, 2)
        insights.append(
            f"The current working dataset contains **{df.shape[0]} rows** and **{df.shape[1]} columns**, "
            f"with an overall data completeness of **{completeness}%** ({total_missing} missing values)."
        )

        missing_per_col = df.isnull().sum()
        if missing_per_col.max() > 0:
            worst_col = missing_per_col.idxmax()
            worst_cnt = int(missing_per_col.max())
            worst_pct = round((worst_cnt / max(len(df), 1)) * 100, 2)
            insights.append(
                f"The column with the most missing values is **`{worst_col}`**, with **{worst_cnt}** missing entries (**{worst_pct}%** of rows)."
            )
        else:
            insights.append("Every column in the working dataset is **100% complete** with zero missing values.")

        for c in cat_cols[:3]:
            series = df[c].dropna().astype(str)
            if not series.empty:
                vc = series.value_counts()
                top_val = vc.index[0]
                top_cnt = int(vc.iloc[0])
                top_pct = round((top_cnt / len(series)) * 100, 1)
                insights.append(
                    f"In categorical column **`{c}`**, the most frequent value is **'{top_val}'**, appearing **{top_cnt} times** (**{top_pct}%** of valid records)."
                )

        meaningful_num = [c for c in num_cols if not c.lower().endswith("id") and not df[c].dropna().empty]
        if meaningful_num:
            means = {c: float(df[c].dropna().mean()) for c in meaningful_num}
            highest_avg_col = max(means, key=means.get)
            insights.append(
                f"Among numerical features, **`{highest_avg_col}`** has the highest average value at **{means[highest_avg_col]:.2f}**."
            )
            for c in meaningful_num[:3]:
                s = df[c].dropna()
                insights.append(
                    f"Column **`{c}`** ranges from a minimum of **{s.min():.2f}** to a maximum of **{s.max():.2f}**, with a median of **{s.median():.2f}**."
                )

        if len(meaningful_num) >= 2:
            corr_matrix = df[meaningful_num].corr().abs()
            np.fill_diagonal(corr_matrix.values, 0)
            max_corr = corr_matrix.max().max()
            if pd.notnull(max_corr) and max_corr > 0:
                row_c, col_c = corr_matrix.stack().idxmax()
                raw_corr = df[row_c].corr(df[col_c])
                strength = "strong" if abs(raw_corr) >= 0.6 else ("moderate" if abs(raw_corr) >= 0.3 else "weak")
                insights.append(
                    f"The strongest linear relationship is between **`{row_c}`** and **`{col_c}`** with a **{strength}** correlation coefficient of **{raw_corr:.2f}** "
                    f"*(Note: statistical correlation measures linear association and does not imply causation)*."
                )

        for idx, text in enumerate(insights, 1):
            st.markdown(f"{idx}. {text}")

        if {"Survived", "Sex", "Pclass"}.issubset(set(orig_df.columns)):
            st.markdown("---")
            st.subheader("Titanic Sample Dataset – Live Recalculated Reference Findings")
            st.caption("These figures are dynamically recalculated directly from the loaded CSV dataset (`train.csv`).")

            total_pax = len(orig_df)
            survivors = int((orig_df["Survived"] == 1).sum())
            non_survivors = int((orig_df["Survived"] == 0).sum())
            surv_pct = (survivors / max(total_pax, 1)) * 100

            females = orig_df[orig_df["Sex"] == "female"]
            female_total = len(females)
            female_surv = int((females["Survived"] == 1).sum())
            female_pct = (female_surv / max(female_total, 1)) * 100

            males = orig_df[orig_df["Sex"] == "male"]
            male_total = len(males)
            male_surv = int((males["Survived"] == 1).sum())
            male_pct = (male_surv / max(male_total, 1)) * 100

            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.markdown("**Overall Survival**")
                st.write(f"- Total Passengers: **{total_pax}**")
                st.write(f"- Survivors: **{survivors}**")
                st.write(f"- Non-Survivors: **{non_survivors}**")
                st.write(f"- Survival Percentage: **{surv_pct:.1f}%**")

            with col_t2:
                st.markdown("**Gender Breakdown**")
                st.write(f"- Female Passengers: **{female_total}** (**{female_surv}** survivors, **{female_pct:.1f}%**)")
                st.write(f"- Male Passengers: **{male_total}** (**{male_surv}** survivors, **{male_pct:.1f}%**)")

            with col_t3:
                st.markdown("**Passenger Class Breakdown**")
                for pclass, label in [(1, "First Class"), (2, "Second Class"), (3, "Third Class")]:
                    sub = orig_df[orig_df["Pclass"] == pclass]
                    p_total = len(sub)
                    p_surv = int((sub["Survived"] == 1).sum())
                    p_pct = (p_surv / max(p_total, 1)) * 100
                    st.write(f"- {label}: **{p_total}** passengers, **{p_surv}** survivors (**{p_pct:.1f}%**)")

# -----------------------------------------------------------------------------
# SECTION 8: DOWNLOAD RESULTS
# -----------------------------------------------------------------------------
elif selected_section == "8. Download Results":
    st.title("Download Results")
    if check_data_loaded():
        df_clean = st.session_state.working_df
        df_filt = st.session_state.filtered_df if st.session_state.filtered_df is not None else df_clean

        st.write("Download your processed datasets, statistical reports, and custom charts below. Original files are never overwritten.")

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("1. Cleaned Working Dataset")
            st.write(f"Rows: **{df_clean.shape[0]}** | Columns: **{df_clean.shape[1]}**")
            clean_csv = df_clean.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Cleaned Dataset (CSV)",
                data=clean_csv,
                file_name="cleaned_dataset.csv",
                mime="text/csv"
            )

            st.subheader("2. Filtered Dataset")
            st.write(f"Rows: **{df_filt.shape[0]}** | Columns: **{df_filt.shape[1]}**")
            filt_csv = df_filt.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Filtered Dataset (CSV)",
                data=filt_csv,
                file_name="filtered_dataset.csv",
                mime="text/csv"
            )

        with c2:
            st.subheader("3. Summary Statistics Report")
            st.write("Descriptive statistics (`describe()`) for all columns.")
            summary_csv = df_clean.describe(include="all").to_csv().encode("utf-8")
            st.download_button(
                label="Download Summary Statistics (CSV)",
                data=summary_csv,
                file_name="summary_statistics.csv",
                mime="text/csv"
            )

            st.subheader("4. Data Quality & Missing Value Report")
            quality_df = pd.DataFrame({
                "Column": df_clean.columns,
                "Data_Type": df_clean.dtypes.astype(str).values,
                "Missing_Count": df_clean.isnull().sum().values,
                "Unique_Values": [df_clean[c].nunique(dropna=True) for c in df_clean.columns]
            })
            quality_csv = quality_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Column Quality Report (CSV)",
                data=quality_csv,
                file_name="data_quality_report.csv",
                mime="text/csv"
            )

        if "last_custom_chart" in st.session_state:
            st.markdown("---")
            st.subheader("5. Latest Generated Custom Chart")
            st.download_button(
                label="Download Last Custom Chart (PNG)",
                data=st.session_state["last_custom_chart"],
                file_name="custom_chart.png",
                mime="image/png"
            )
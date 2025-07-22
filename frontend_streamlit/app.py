# frontend_streamlit/app.py
import streamlit as st
import requests
import pandas as pd
import datetime
import os

# --- Configuration ---
# Ensure this matches your FastAPI backend's running URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Receipt & Bill Analyzer",
    page_icon="📈",
    layout="wide", # Use wide layout for a more spacious dashboard
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Updated for black text visibility) ---
st.markdown("""
<style>
    /* Main container padding */
    .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    /* App background and general text color */
    .stApp {
        background-color: #f0f2f6; /* Light gray background */
        color: #000000; /* All general text is black */
    }
    /* Heading colors - keep purple for distinction */
    h1, h2, h3, h4, h5, h6 {
        color: #4A00B7; /* Deep purple for headings */
    }
    /* Button styling */
    .stButton>button {
        background-color: #6C2B8F; /* Purple button */
        color: white; /* White text on purple button */
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #8D4CD1;
        color: white;
    }
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #9966CC;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
        color: #000000; /* Ensure text inside uploader is black */
    }
    /* Alert styling (for st.info, st.warning, st.success, st.error) */
    .stAlert > div > div > p { /* Streamlit's internal paragraph for alert messages */
        color: #000000 !important; /* Force black text for alert messages */
    }
    .stAlert {
        border-radius: 8px;
    }
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #e6e6fa; /* Light lavender */
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: bold;
        color: #4A00B7; /* Dark text for expander header */
    }
    /* Remove default Streamlit bottom padding */
    #root > div:nth-child(1) > div > div > div > div > section > div {
        padding-bottom: 0px;
    }

    /* --- Specific rules for input fields and table text (BLACK) --- */
    /* Input fields (text, number, date) - values and labels */
    div[data-baseweb="input"] input,
    div[data-baseweb="input"] textarea,
    .stTextInput label, .stNumberInput label, .stDateInput label, /* Labels for these inputs */
    .st-bd, /* for text areas, internal text */
    .st-da, /* for date inputs' text display */
    .st-ct /* for number inputs' text display */
    {
        color: #000000 !important; /* Force black text */
        background-color: white !important; /* Ensure clear background */
        border: 1px solid #ccc; /* Subtle border */
        border-radius: 4px;
        padding: 0.5rem;
    }

    /* Selectbox options and selected value text, and labels */
    .stSelectbox label { /* Label for selectbox */
        color: #000000 !important;
    }
    .st-bx, .st-bb, .st-cg /* Selectbox display text, options, and general checkbox/radio labels */ {
        color: #000000 !important;
    }

    /* Dataframe/Data Editor cell text and headers */
    .st-ag .ag-header-cell-text, /* Table header text */
    .st-ag .ag-cell-value, /* Table cell values */
    .st-ag .ag-wrapper, /* General wrapper for table content */
    .st-ag .ag-body-viewport, /* Body of the table */
    .st-ag .ag-root-wrapper-body /* Root of the table content */
    {
        color: #000000 !important; /* Black text for all table content */
    }

    /* Placeholder text within inputs */
    ::-webkit-input-placeholder { /* Chrome, Opera, Safari */
        color: #333333 !important; /* Darker placeholder text */
    }
    ::-moz-placeholder { /* Firefox 19+ */
        color: #333333 !important;
    }
    :-ms-input-placeholder { /* IE 10+ */
        color: #333333 !important;
    }
    :-moz-placeholder { /* Firefox 18- */
        color: #333333 !important;
    }

    /* Metric values (e.g., $9.03, $178.95) */
    .stMetric > div > div:nth-child(2) > div:nth-child(1) {
        color: #000000 !important; /* Force the large metric value to black */
    }

    /* Metric labels (e.g., "Total Money Spent", "Average Spend") */
    .stMetric > div > div:nth-child(1) {
        color: #000000 !important; /* Force metric label to black */
    }
    /* Global text color for all paragraphs and markdown text */
    p, .stMarkdown, .stText {
        color: #000000 !important;
    }

    /* --- SPECIFIC FIXES FOR SIDEBAR NAVIGATION & BUTTONS (WHITE text on dark background) --- */

    /* "Select a section" label (the st.radio header) in sidebar */
    section[data-testid="stSidebar"] .stRadio label > div > p {
        color: white !important; /* Make this specific label white */
    }
    
    /* Sidebar info message: "Keep your FastAPI backend running for full functionality!" */
    section[data-testid="stSidebar"] .stAlert p {
        color: white !important; /* Make text within st.info white */
    }

    /* Individual radio button options text (e.g., Upload & View Receipts) */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span p {
        color: white !important; /* Force radio option text to white */
    }
    
    /* Fallback for other sidebar text that should be white (headers, general text) */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] .st-bv, /* Sidebar header text elements */
    section[data-testid="stSidebar"] .stText { /* General Streamlit Text in sidebar */
        color: white !important; /* Make specific sidebar elements white */
    }

    /* Buttons with text "Apply Filters", "Reset Filters", "Download Data as CSV/JSON" */
    /* This targets the actual text within the button */
    .stButton > button p {
        color: white !important;
    }
    .stDownloadButton > button p {
        color: white !important;
    }

</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---
@st.cache_data(ttl=60) # Cache data for 60 seconds to avoid excessive backend calls
def fetch_all_receipts():
    """Fetches all receipts from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/receipts")
        response.raise_for_status() # Raise an exception for HTTP errors
        receipts_data = response.json()
        # Convert date strings to datetime.date objects for Streamlit's table/charting
        for r in receipts_data:
            if r.get('transaction_date'):
                # Handle potential different date formats during parsing
                try:
                    r['transaction_date'] = datetime.date.fromisoformat(r['transaction_date'])
                except (ValueError, TypeError):
                    # Fallback for other common formats, e.g., MM/DD/YYYY
                    try:
                        r['transaction_date'] = datetime.datetime.strptime(r['transaction_date'], '%m/%d/%Y').date()
                    except (ValueError, TypeError):
                        r['transaction_date'] = None # If still unparseable, set to None
            if r.get('created_at'):
                try:
                    # The created_at field might include time, so parse as datetime first
                    r['created_at'] = datetime.datetime.fromisoformat(r['created_at'].replace("Z", "+00:00")).date()
                except (ValueError, TypeError):
                    r['created_at'] = None
        return receipts_data
    except requests.exceptions.ConnectionError:
        st.error("🚨 Cannot connect to backend. Please ensure your FastAPI server is running.", icon="‼️")
        return []
    except requests.exceptions.RequestException as e:
        error_detail = e.response.json().get('detail', str(e)) if e.response else str(e)
        st.error(f"⚠️ Error fetching receipts: {error_detail}", icon="⚠️")
        return []

# --- Main App Structure ---

st.title("📈 Receipt & Bill Analyzer")
st.markdown("### Your personal finance assistant, powered by AI.")
st.write("---")

# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
app_mode = st.sidebar.radio(
    "Select a section",
    ["Upload & View Receipts", "Spending Analytics", "Search & Filter", "Export Data"]
)
st.sidebar.write("---")
st.sidebar.info("💡 Keep your FastAPI backend running for full functionality!")

# --- Content Areas ---

if app_mode == "Upload & View Receipts":
    st.header("📤 Upload & Manage Receipts")
    st.markdown("Upload new receipts/bills, correct extracted data, and view your collection.")

    # Use session state to hold data between processing and saving
    if 'last_upload_response' not in st.session_state:
        st.session_state.last_upload_response = None

    # File Upload Section
    with st.expander("Upload New File", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose an image (.jpg, .png), PDF, or text file",
            type=["jpg", "jpeg", "png", "pdf", "txt"],
            help="Supported formats: JPG, PNG, PDF, TXT. Max file size: 25MB."
        )

        if uploaded_file is not None:
            # Button to process the file and show the correction form
            if st.button("Process File for Correction", key="process_button"):
                with st.spinner("Uploading and processing file... This may take a moment."):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    try:
                        # This endpoint saves an initial record and returns the data
                        response = requests.post(f"{BACKEND_URL}/api/upload", files=files)
                        response.raise_for_status()
                        st.session_state.last_upload_response = response.json()
                        st.toast("File processed. Correct fields below if needed.", icon="✍️")
                        st.rerun() # Rerun to show the correction form immediately
                    except requests.exceptions.ConnectionError:
                        st.error(f"❌ Could not connect to FastAPI backend. Please ensure it's running on `{BACKEND_URL}`.", icon="🔌")
                    except requests.exceptions.RequestException as e:
                        error_detail = e.response.json().get('detail', str(e)) if e.response else str(e)
                        st.error(f"🔥 Error uploading file: {error_detail}", icon="💥")
                    except Exception as e:
                        st.error(f"🚫 An unexpected error occurred: {e}", icon="⛔")

    # NEW: Manual Correction Form for the latest upload
    if st.session_state.get('last_upload_response'):
        st.write("---")
        st.subheader("✍️ Correct Parsed Fields")
        st.info("Review the extracted data below. Make any corrections and then click the button to save to the database.")
        
        response_data = st.session_state.last_upload_response
        parsed_fields = response_data.get('parsed_fields', {})
        record_id = response_data.get('db_record_id')

        if record_id:
            with st.form(key="correction_form"):
                # Prepare default values, handling None and converting date
                default_date = None
                if parsed_fields.get('transaction_date'):
                    try:
                        default_date = datetime.date.fromisoformat(parsed_fields['transaction_date'])
                    except (ValueError, TypeError):
                        default_date = None # Keep it None if format is wrong

                st.write(f"**Original Filename:** `{response_data.get('filename', 'N/A')}` | **Database ID:** `{record_id}`")
                
                # Create form fields
                corrected_vendor = st.text_input("Vendor / Biller", value=parsed_fields.get('vendor', ''))
                corrected_date = st.date_input("Transaction Date", value=default_date)
                corrected_amount = st.number_input("Amount", value=float(parsed_fields.get('amount', 0.0)), format="%.2f")
                corrected_currency = st.text_input("Currency", value=parsed_fields.get('currency', ''))
                corrected_category = st.text_input("Category", value=parsed_fields.get('category', 'Uncategorized'))

                # Submit button for the form
                submitted = st.form_submit_button("Confirm and Save to Database")
                if submitted:
                    with st.spinner("Saving corrections..."):
                        update_payload = {
                            "vendor": corrected_vendor,
                            "transaction_date": corrected_date.isoformat() if corrected_date else None,
                            "amount": corrected_amount,
                            "currency": corrected_currency,
                            "category": corrected_category
                        }
                        
                        try:
                            api_response = requests.put(f"{BACKEND_URL}/api/receipts/{record_id}", json=update_payload)
                            api_response.raise_for_status()
                            st.success(f"🎉 Receipt ID {record_id} updated successfully!", icon="✅")
                            
                            st.session_state.last_upload_response = None
                            fetch_all_receipts.clear()
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            error_detail = e.response.json().get('detail', str(e)) if e.response else str(e)
                            st.error(f"Failed to update receipt ID {record_id}: {error_detail}", icon="❌")
        else:
            st.error("Could not get a database ID for the uploaded file. Cannot save corrections.")

    st.write("---")
    st.subheader("🧾 All Uploaded Receipts")

    receipts = fetch_all_receipts()

    if receipts:
        df = pd.DataFrame(receipts)
        # Reorder columns for better presentation
        display_columns = [
            "id", "vendor", "transaction_date", "amount",
            "currency", "category", "filename", "content_type", "created_at"
        ]
        # Ensure all display columns exist in DataFrame, add missing ones as None
        for col in display_columns:
            if col not in df.columns:
                df[col] = None

        df_display = df[display_columns].copy() # Use .copy() to prevent SettingWithCopyWarning

        st.dataframe(df_display, use_container_width=True, hide_index=True)

    else: # This branch means receipts list is empty
        st.info("No receipts uploaded yet. Use the 'Upload New File' section above!")


elif app_mode == "Spending Analytics":
    st.header("📊 Spending Dashboard")
    st.markdown("Visualize your expenses by category, vendor, and over time.")

    all_receipts = fetch_all_receipts()
    if not all_receipts:
        st.warning("Please upload some receipts first to view analytics.")
    else:
        df_analytics = pd.DataFrame(all_receipts)
        # Ensure necessary columns are present and converted to correct types
        # Dropna on critical columns for analytics
        df_analytics = df_analytics.dropna(subset=['amount', 'category', 'transaction_date', 'vendor'])
        if not df_analytics.empty:
            df_analytics['transaction_date'] = pd.to_datetime(df_analytics['transaction_date'])

            st.subheader("Total Spend Overview")
            # Total Spend
            total_spend = df_analytics['amount'].sum()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Money Spent", f"${total_spend:,.2f}")

            # Mean, Median, Mode (from backend)
            try:
                stats_response = requests.get(f"{BACKEND_URL}/api/analytics/spend-statistics")
                stats_response.raise_for_status()
                stats = stats_response.json()
                col2.metric("Average Spend", f"${stats.get('mean', 0.0):,.2f}")
                col3.metric("Median Spend", f"${stats.get('median', 0.0):,.2f}")
                # Mode might be a list or single value, handle for display
                mode_display = f"${stats.get('mode', 'N/A')}" if stats.get('mode') is not None else 'N/A'
                st.write(f"**Mode Spend:** {mode_display}")

            except requests.exceptions.RequestException as e:
                st.warning(f"Could not fetch spend statistics from backend: {e.response.json().get('detail', str(e))}")


            st.subheader("Categories Distribution")
            category_spend = df_analytics.groupby('category')['amount'].sum().reset_index()
            st.bar_chart(category_spend.set_index('category'))

            st.subheader("Vendor Frequency")
            try:
                vendor_freq_response = requests.get(f"{BACKEND_URL}/api/analytics/vendor-frequency")
                vendor_freq_response.raise_for_status()
                vendor_counts = vendor_freq_response.json()
                if vendor_counts:
                    vendor_df = pd.DataFrame(list(vendor_counts.items()), columns=['Vendor', 'Count'])
                    st.bar_chart(vendor_df.set_index('Vendor'))
                else:
                    st.info("No vendor frequency data available.")
            except requests.exceptions.RequestException as e:
                st.warning(f"Could not fetch vendor frequency from backend: {e.response.json().get('detail', str(e))}")


            st.subheader("Monthly Spending Trend")
            try:
                monthly_trend_response = requests.get(f"{BACKEND_URL}/api/analytics/monthly-spend-trend")
                monthly_trend_response.raise_for_status()
                monthly_data = monthly_trend_response.json()
                if monthly_data:
                    monthly_df = pd.DataFrame(monthly_data)
                    monthly_df['month_year'] = pd.to_datetime(monthly_df['month_year'])
                    monthly_df = monthly_df.sort_values('month_year')
                    st.line_chart(monthly_df.set_index('month_year'))
                else:
                    st.info("No monthly spending trend data available.")
            except requests.exceptions.RequestException as e:
                st.warning(f"Could not fetch monthly trend from backend: {e.response.json().get('detail', str(e))}")
        else:
            st.info("Not enough valid data (amount, category, date, vendor) to generate analytics.")


elif app_mode == "Search & Filter":
    st.header("🔍 Search and Filter Receipts")
    st.markdown("Use the filters below to find specific receipts or apply sorting. "
                "Click **'Apply Filters'** to see results or **'Reset Filters'** to clear all criteria.")

    # Use a form to group filters and allow a single submit button to apply them
    with st.form("search_filter_form"):
        st.subheader("Keywords & Vendors")
        col_text1, col_text2 = st.columns(2)
        keyword = col_text1.text_input("Search Keyword (Filename, Vendor, Category)")
        vendor_pattern = col_text2.text_input("Vendor Name Pattern (e.g., Walmart%)", help="Use % as wildcard.")

        st.subheader("Amount Range")
        col_amount1, col_amount2 = st.columns(2)
        min_amount = col_amount1.number_input("Minimum Amount", min_value=0.0, value=0.0, format="%.2f")
        max_amount = col_amount2.number_input("Maximum Amount", min_value=0.0, value=999999.99, format="%.2f")

        st.subheader("Date Range")
        all_receipts_for_dates = fetch_all_receipts()
        min_db_date, max_db_date = None, None
        if all_receipts_for_dates:
            dates = [r['transaction_date'] for r in all_receipts_for_dates if isinstance(r.get('transaction_date'), datetime.date)]
            if dates:
                min_db_date, max_db_date = min(dates), max(dates)

        col_date1, col_date2 = st.columns(2)
        start_date = col_date1.date_input("Start Date", value=min_db_date, min_value=min_db_date, max_value=max_db_date)
        end_date = col_date2.date_input("End Date", value=max_db_date, min_value=min_db_date, max_value=max_db_date)

        st.subheader("Sort Results")
        col_sort1, col_sort2 = st.columns(2)
        sort_by = col_sort1.selectbox("Sort By", options=["None", "Amount", "Date", "Vendor"])
        sort_order = col_sort2.radio("Sort Order", options=["asc", "desc"], horizontal=True)

        st.write("---")
        col_buttons1, col_buttons2 = st.columns([1,1])
        apply_filters_button = col_buttons1.form_submit_button("✅ Apply Filters", use_container_width=True)
        reset_filters_button = col_buttons2.form_submit_button("🔄 Reset Filters", use_container_width=True)

    if reset_filters_button:
        st.rerun()

    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = None

    if apply_filters_button:
        search_params = {
            "keyword": keyword if keyword else None,
            "min_amount": min_amount if min_amount > 0.0 else None,
            "max_amount": max_amount if max_amount < 999999.99 else None,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "vendor_pattern": vendor_pattern if vendor_pattern else None,
            "sort_by": sort_by.lower() if sort_by != "None" else None,
            "sort_order": sort_order,
            "skip": 0, "limit": 100
        }

        query_params = {k: v for k, v in search_params.items() if v is not None}
        
        endpoint = "/api/receipts/search" # Single unified endpoint

        try:
            with st.spinner("Searching and filtering..."):
                response = requests.get(f"{BACKEND_URL}{endpoint}", params=query_params)
                response.raise_for_status()
                st.session_state['search_results'] = response.json()
        except requests.exceptions.RequestException as e:
            error_detail = e.response.json().get('detail', str(e)) if e.response else str(e)
            st.error(f"Error during search/filter: {error_detail}", icon="❌")
            st.session_state['search_results'] = []

    if st.session_state['search_results'] is not None:
        if st.session_state['search_results']:
            df_search = pd.DataFrame(st.session_state['search_results'])
            st.subheader("Search Results")
            st.dataframe(df_search, use_container_width=True, hide_index=True)
        else:
            st.info("No receipts found matching your criteria.")
    else:
        st.info("Adjust the filters and click 'Apply Filters' to see results.")


elif app_mode == "Export Data":
    st.header("⬇️ Export Your Data")
    st.markdown("Export your receipt data to CSV or JSON format.")

    receipts_to_export = fetch_all_receipts()
    if not receipts_to_export:
        st.warning("No data to export. Please upload some receipts first.")
    else:
        df_export = pd.DataFrame(receipts_to_export)
        # Ensure dates are strings for clean export
        for col in ['transaction_date', 'created_at']:
            if col in df_export.columns:
                df_export[col] = pd.to_datetime(df_export[col], errors='coerce').dt.strftime('%Y-%m-%d')
        
        col1, col2 = st.columns(2)

        with col1:
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data as CSV",
                data=csv_data,
                file_name="receipts_data.csv",
                mime="text/csv",
                key="download_csv",
                use_container_width=True
            )
        
        with col2:
            json_data = df_export.to_json(orient="records", indent=4).encode('utf-8')
            st.download_button(
                label="Download Data as JSON",
                data=json_data,
                file_name="receipts_data.json",
                mime="application/json",
                key="download_json",
                use_container_width=True
            )

st.write("---")
st.markdown("<p style='text-align: center; color: gray;'>Built with ❤️ by Mohd Irfan.</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Current Time: " + datetime.datetime.now().strftime("%I:%M:%S %p, %A, %d %B %Y") + "</p>", unsafe_allow_html=True)
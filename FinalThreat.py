import pandas as pd
import streamlit as st
import duckdb
from datetime import datetime, timedelta

# Streamlit app title
st.title("Threat Intelligence Dashboard")

# File uploader for Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Load the uploaded Excel file
    try:
        excel_data = pd.ExcelFile(uploaded_file)
        sheet_names = excel_data.sheet_names
        st.write("Available sheets:", sheet_names)

        # Date range selection
        st.header("Select Date Range for Created Field")
        start_date = st.date_input("Start date", value=datetime.today() - timedelta(days=30))
        end_date = st.date_input("End date", value=datetime.today())

        # Convert dates to string format for DuckDB query
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Function to process and display data from each sheet
        def process_sheet(sheet_name, title):
            if sheet_name in sheet_names:
                data = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')  # Convert date column

                # Filter data using DuckDB
                filtered_data = duckdb.query(f"""
                    SELECT * 
                    FROM data 
                    WHERE Date BETWEEN '{start_date_str}' AND '{end_date_str}'
                """).df()

                # Display filtered data
                if filtered_data.empty:
                    st.write(f"No data found for the selected date range in {title}.")
                else:
                    st.title(f"{title} Data")
                    st.write(filtered_data)

                # Calculate advisory counts
                advisory_count = len(filtered_data)
                applicable_advisory_count = len(filtered_data[filtered_data['Applicable to Our environment'].str.upper() == 'YES'])

                # Display counts
                st.subheader(f"{title} Advisory Count: {advisory_count}")
                st.subheader(f"{title} Applicable Advisory: {applicable_advisory_count}")
            else:
                st.write(f"{title} sheet not found in the uploaded file.")

        # Process each sheet by its specific name
        process_sheet('CERT-In Updates', 'CERT-In')
        process_sheet('Threat Intel Feeds', 'Threat Intel')
        process_sheet('CVEs', 'CVEs')
        process_sheet('Lentra Partners', 'Lentra Partners')

    except Exception as e:
        st.error(f"Error processing the file: {e}")

else:
    st.write("Please upload an Excel file to proceed.")

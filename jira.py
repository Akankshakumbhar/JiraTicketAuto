# not working properly)



from datetime import datetime, timedelta
import pandas as pd
import duckdb
import streamlit as st

st.title("Jira statistic  File")

# File upload
uploaded_file = st.file_uploader("Upload a CSV file", type=['csv'])

# Check if a file has been uploaded
if uploaded_file is not None:
    # Load the CSV file
    file1 = pd.read_csv(uploaded_file)

    # Convert 'Created' column to datetime
    try:
        file1['Created'] = pd.to_datetime(file1['Created'], errors='coerce')
    except Exception as e:
        st.error(f"Error parsing dates: {e}")

    # Filter out rows where 'Created' is Na
    file1 = file1[file1['Created'].notna()]

    st.header("Select Date Range for Created Field")
    start_date = st.date_input("Start date", value=datetime.today() - timedelta(days=30))
    end_date = st.date_input("End date", value=datetime.today())

    # Query the data with DuckDB
    short = duckdb.query(f"""
        SELECT "Issue key", Summary, Status, Reporter, Creator, Created 
        FROM file1 
        WHERE Created BETWEEN '{start_date}' AND '{end_date}'
    """).df()

    if short.empty:
        st.write(f"No tickets found for the selected date range.")
    else:
        st.write(f"Report for the period {start_date} to {end_date}")


        def highlight_status(s):
            return [
                'background-color:green' if v == 'Closed' else
                'background-color:red' if v == 'L1 Assigned' else
                '' for v in s
            ]


        styled_df = short.style.apply(highlight_status, subset=['Status'])

        # Display the styled DataFrame
        st.dataframe(styled_df)

        # Download button for the styled DataFrame as an Excel file
        excel_file = f"report_{start_date}_to_{end_date}.xlsx"

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            styled_df.to_excel(writer, sheet_name='Report', index=False)

        # Download button for the report
        with open(excel_file, "rb") as f:
            st.download_button(
                label="Download Report as Excel",
                data=f,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Ticket count
    TickCount = duckdb.query('SELECT COUNT(*) as TotalTickets FROM short').df()
    total_incident_logged = int(TickCount['TotalTickets'].iloc[0])

    # Resolved tickets
    resolved_incident = duckdb.query("SELECT COUNT(Status) as ResolvedIncident FROM short WHERE Status='Closed'").df()
    resolved_incident = int(resolved_incident['ResolvedIncident'].iloc[0])

    # Incidents under investigation
    incident_under_invest = duckdb.query(
        "SELECT COUNT(Status) as incidentinvest FROM short WHERE Status='L1 Assigned'").df()
    incident_under_invest = int(incident_under_invest['incidentinvest'].iloc[0])

    # Calculate the current week from the start date
    current_week = start_date.isocalendar()[1]
    detailed_statistics = f"Week {current_week} SOC Review Report Ticket Status"

    st.title('JIRA Ticket Statistics')
    st.subheader(f"Total Incident Logged: {total_incident_logged}")
    st.subheader(f"Resolved Incidents: {resolved_incident}")
    st.subheader(f"Incidents Under Investigation: {incident_under_invest}")
    st.subheader(f"Detailed Statistic: {detailed_statistics}")
else:
    st.info("Please upload a CSV file to get started.")

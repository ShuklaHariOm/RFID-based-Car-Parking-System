import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Define a function to get the parking data (latest 5 entries)
def get_parking_data():
    conn = sqlite3.connect('parking.db')
    query = "SELECT * FROM parking_data ORDER BY id DESC LIMIT 5"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Define a function to get all parking data (for viewing the entire table)
def get_all_parking_data():
    conn = sqlite3.connect('parking.db')
    query = "SELECT * FROM parking_data"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Define a function to generate the slot usage chart
def generate_slot_usage_chart():
    conn = sqlite3.connect('parking.db')
    query = "SELECT slot_number, COUNT(*) as count FROM parking_data GROUP BY slot_number"
    df = pd.read_sql(query, conn)
    conn.close()

    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(df['count'], labels=df['slot_number'].astype(str), autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
    ax.set_title('Number of Cars Parked in Each Slot')
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)


# Define a function to get the busiest time
def get_busiest_time():
    conn = sqlite3.connect('parking.db')
    query = "SELECT strftime('%H', in_time) as hour, COUNT(*) as count FROM parking_data GROUP BY hour ORDER BY count DESC LIMIT 1"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['hour'][0] if not df.empty else "N/A"


def generate_daily_traffic_chart():
    conn = sqlite3.connect('parking.db')
    query = """
        SELECT DATE(in_time) as date, 
               COUNT(in_time) as entries,
               COUNT(out_time) as exits
        FROM parking_data
        GROUP BY date
        ORDER BY date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Plotting the daily entries and exits using line plot
    fig, ax = plt.subplots()
    ax.plot(df['date'], df['entries'], label='Entries', marker='o', linestyle='-', color='green')
    ax.plot(df['date'], df['exits'], label='Exits', marker='o', linestyle='-', color='red')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Cars')
    ax.set_title('Daily Entries and Exits')
    ax.legend()
    st.pyplot(fig)


def generate_avg_parking_duration_chart():
    conn = sqlite3.connect('parking.db')
    query = """
        SELECT slot_number, 
               AVG(strftime('%s', out_time) - strftime('%s', in_time)) / 60.0 AS avg_duration_minutes
        FROM parking_data
        WHERE out_time IS NOT NULL
        GROUP BY slot_number
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Plotting the average duration per slot using area plot
    fig, ax = plt.subplots()
    ax.fill_between(df['slot_number'].astype(str), df['avg_duration_minutes'], color='green', alpha=0.5)
    ax.set_xlabel('Slot Number')
    ax.set_ylabel('Average Duration (minutes)')
    ax.set_title('Average Parking Duration per Slot')
    st.pyplot(fig)


def generate_peak_hours_chart():
    conn = sqlite3.connect('parking.db')
    query = """
        SELECT strftime('%H', in_time) as hour, COUNT(*) as count
        FROM parking_data
        GROUP BY hour
        ORDER BY hour
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Plotting the peak hours using line plot
    fig, ax = plt.subplots()
    ax.plot(df['hour'], df['count'], marker='o', linestyle='-', color='orange')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Number of Cars')
    ax.set_title('Peak Hours for Car Entries')
    st.pyplot(fig)


# Streamlit UI
st.title("Mall Parking Insights")

# Display latest 5 parking data entries
st.header("Latest Parking Data Entries")
latest_data = get_parking_data()
st.dataframe(latest_data)

# Button to toggle the visibility of the entire parking data
if 'show_table' not in st.session_state:
    st.session_state.show_table = False  # Initialize the session state variable

# Toggle button for viewing the entire parking data
if st.button("View All Data" if not st.session_state.show_table else "Hide Table"):
    st.session_state.show_table = not st.session_state.show_table  # Toggle the state

# Display the table if the toggle state is True
if st.session_state.show_table:
    st.header("All Parking Data")
    all_data = get_all_parking_data()
    st.dataframe(all_data)

# Display busiest time
st.header("Busiest Time")
busiest_time = get_busiest_time()
st.write(f"The busiest time is around {busiest_time}:00 hours.")

# Streamlit section for daily traffic analysis
st.header("Daily Traffic Analysis")
generate_daily_traffic_chart()

# Streamlit section for average parking duration per slot
st.header("Average Parking Duration per Slot")
generate_avg_parking_duration_chart()

# Streamlit section for peak hours analysis
st.header("Peak Hours Analysis")
generate_peak_hours_chart()

# Display the slot usage chart
st.header("Slot Usage")
generate_slot_usage_chart()

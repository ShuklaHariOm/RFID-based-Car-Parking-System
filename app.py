from flask import Flask, render_template
import sqlite3
import matplotlib.pyplot as plt

app = Flask(__name__)


def get_parking_data():
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parking_data ORDER BY id DESC LIMIT 5")
    data = cursor.fetchall()
    generate_slot_usage_chart()
    conn.close()
    return data


@app.route('/view_all')
def view_all():
    # Connect to the database and retrieve all entries
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parking_data")
    all_data = cursor.fetchall()  # Get all records

    conn.close()
    return render_template('view_all.html', all_data=all_data)


def get_busiest_time():
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT strftime('%H', in_time) AS hour, COUNT(*) FROM parking_data GROUP BY hour ORDER BY COUNT(*) DESC LIMIT 1")
    busiest_time = cursor.fetchone()
    conn.close()
    return busiest_time[0] if busiest_time else "N/A"


def generate_slot_usage_chart():
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # Fetch the count of cars parked in each slot
    cursor.execute("SELECT slot_number, COUNT(*) FROM parking_data GROUP BY slot_number")
    slot_data = cursor.fetchall()

    # Close the connection
    conn.close()

    # Prepare data for plotting
    slots = [str(slot[0]) for slot in slot_data]  # Extract slot numbers
    counts = [slot[1] for slot in slot_data]      # Extract counts

    # Create a bar chart
    plt.figure(figsize=(10, 5))
    plt.bar(slots, counts, color='blue')
    plt.xlabel('Slot Number')
    plt.ylabel('Number of Cars Parked')
    plt.title('Number of Cars Parked in Each Slot')
    plt.xticks(slots)
    plt.grid(axis='y')

    # Save the plot to a file
    chart_path = 'static/slot_usage.png'
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path  # Return the path to the saved image


@app.route('/')
def index():
    data = get_parking_data()
    busiest_time = get_busiest_time()
    return render_template('dashboard.html', data=data, busiest_time=busiest_time)

if __name__ == '__main__':
    app.run(debug=True)

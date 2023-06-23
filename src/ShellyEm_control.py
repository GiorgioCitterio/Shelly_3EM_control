import requests
import schedule
import time
import json
import psycopg2
import config
import tkinter as tk
from tkinter import messagebox
import threading
from classes.Em import Em
from classes.Sensor import Sensor
from datetime import datetime
import pytz

#define variables
measurement_list = []
sensor_list = []
cur = None
conn = None
url = 'your_server_uri'
body_data = {
    'id': 'your_device_id',
    'auth_key': 'your_auth_key'
}
window = tk.Tk()
entry_shelly_id = None

def connect():
    global cur, conn
    """Connect to the PostgreSQL database server"""
    try:
        # read connection parameters
        params = config.config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)   

def disconnect():
    global cur, conn
    try:
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
def create_tables():
    #create a table with commands
    commands = (
        """
        CREATE TABLE IF NOT EXISTS measurements (
                shelly_id VARCHAR(12) NOT NULL,
                phase INTEGER NOT NULL CHECK (phase IN (0, 1, 2)),
                sensor_id INTEGER NOT NULL,
                sensor_value NUMERIC (5, 2),
                measurement_date TIMESTAMPTZ,
                duration INTEGER
                )
        """,
        """CREATE TABLE IF NOT EXISTS sensor (
                shelly_id VARCHAR(12) NOT NULL,
                phase INTEGER NOT NULL CHECK (phase IN (0, 1, 2)),
                sensor_id INTEGER NOT NULL,
                sensor_description VARCHAR(14) NOT NULL,
                checked BOOLEAN NOT NULL DEFAULT 'true'
                )
        """)
    #create table one by one
    for command in commands:
        cur.execute(command)
        
def insert_lists():
    # Insert sensor data
    for sensor in sensor_list:
        # Check if the sensor already exists in the table for the specific phase
        cur.execute("SELECT EXISTS(SELECT 1 FROM sensor WHERE shelly_id = %s AND phase = %s AND sensor_id = %s)",
                    (sensor.shelly_id, sensor.phase, sensor.sensor_id))
        exists = cur.fetchone()[0]

        if not exists:
            # Insert the sensor only if it doesn't exist
            cur.execute("INSERT INTO sensor(shelly_id, phase, sensor_id, sensor_description) VALUES(%s, %s, %s, %s)",
                        sensor.to_tuple())

    # Insert measurement data
    for measurement in measurement_list:
        # Check if the sensor is set to true in the sensor table
        cur.execute("SELECT checked FROM sensor WHERE shelly_id = %s AND phase = %s AND sensor_id = %s",
                    (measurement.shelly_id, measurement.phase, measurement.sensor_id))
        sensor_checked = cur.fetchone()[0]

        if sensor_checked:
            # If the sensor is set to true, insert the measurement data
            cur.execute("INSERT INTO measurements(shelly_id, phase, sensor_id, sensor_value, measurement_date, duration) VALUES(%s, %s, %s, %s, %s, %s)",
                        measurement.to_tuple())

    print("Data added")
    conn.commit()

def send_request():
    global measurement_list, sensor_list
    sensor_list.clear()
    measurement_list.clear()
    try:
        response = requests.post(url, data=body_data)
    except Exception as error:
        print('Error:', error)
        return

    if response.status_code != 200:
        print(f"Error in the request: {response.status_code} - {response.text}")
        return
    
    jsondata = json.loads(response.text)
    
    # Retrieve the relevant part of the string
    shelly_id = jsondata['data']['device_status']['mac']
    emeters = jsondata['data']['device_status']['emeters']
    measurement_date = datetime.strptime(jsondata['data']['device_status']['_updated'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
    keyOfJson = ''
    # TODO: capire quanto dura la rilevazione di un dato e cambiare duration
    duration = 0
    
    #for che scorre tutti gli energy meters e per ognuno prende tutti i parametri e li aggiunge alla lista
    for phase in range(len(emeters)):
        for sensor in range(len(emeters[phase])):
            match sensor:
                case 0:
                    keyOfJson = 'power'
                case 1:
                    keyOfJson = 'pf'
                case 2:
                    keyOfJson = 'current'
                case 3:
                    keyOfJson = 'voltage'
                case 4:
                    keyOfJson = 'is_valid'
                case 5:
                    keyOfJson = 'total'
                case 6:
                    keyOfJson = 'total_returned'
            if(emeters[phase][keyOfJson] == True):
                emeters[phase][keyOfJson] = 1
            elif(emeters[phase][keyOfJson] == False):
                emeters[phase][keyOfJson] = 0
            measurement_list.append(Em(shelly_id, phase, sensor, emeters[phase][keyOfJson], measurement_date, duration))
            sensor_list.append(Sensor(shelly_id, phase, sensor, keyOfJson))
    insert_lists()

def tkinter_init():
    global window, entry_shelly_id
    window.geometry("300x100")
    window.title("Energy meter control")
    
    # Create labels and entry fields
    label_shelly_id = tk.Label(window, text="Shelly ID:")
    label_shelly_id.pack()

    entry_shelly_id = tk.Entry(window)
    entry_shelly_id.pack()
    
    # Create buttons
    button_search = tk.Button(window, text="Search", command=search)
    button_search.pack()

    button_close = tk.Button(window, text="Close", command=close_window)
    button_close.pack()

def search():
    shelly_id = entry_shelly_id.get()

    # Check if the Shelly ID exists in the database
    cur.execute("SELECT EXISTS(SELECT 1 FROM measurements WHERE shelly_id = %s)", (shelly_id,))
    exists = cur.fetchone()[0]

    if exists:
        # If the Shelly ID exists, create a new window to display the data
        open_sensor_table_window(shelly_id)
    else:
        # If the Shelly ID does not exist, check for similar or matching IDs
        cur.execute("SELECT DISTINCT shelly_id FROM measurements WHERE shelly_id ILIKE %s", (f"%{shelly_id}%",))
        similar_ids = cur.fetchall()
        if similar_ids:
            messagebox.showinfo("Similar Shelly IDs", f"No matching Shelly ID found. Here are some similar IDs:\n{', '.join(id[0] for id in similar_ids)}")
        else:
            messagebox.showerror("Error", "Shelly ID does not exist in the database.")

def close_window():
    global window
    window.destroy()

def open_sensor_table_window(shelly_id):
    
    # Create window and objects
    sensor_table_window = tk.Toplevel(window)
    sensor_table_window.title(f"Sensor Table - Shelly ID: {shelly_id}")

    # Create Phase Frames
    phase_frames = []
    for phase in range(3):
        phase_frame = tk.Frame(sensor_table_window)
        phase_frame.grid(row=0, column=phase, padx=10, pady=10)
        phase_frames.append(phase_frame)

    # Retrieve the sensor IDs, descriptions, and checked values corresponding to the Shelly ID from the database
    cur.execute("SELECT sensor.phase, sensor.sensor_id, sensor.sensor_description, sensor.checked FROM sensor JOIN measurements ON sensor.sensor_id = measurements.sensor_id WHERE measurements.shelly_id = %s GROUP BY sensor.phase, sensor.sensor_id, sensor.sensor_description, sensor.checked ORDER BY sensor.sensor_id ASC", (shelly_id,))
    sensors = cur.fetchall()

    # Create a dictionary to store the checkbox variables
    checkboxes = []
    checkbox_vars = {0: {}, 1: {}, 2: {}}
    initial_checkbox_states = {0: {}, 1: {}, 2: {}}

    # Iterate through the sensors and create checkboxes in the corresponding phase frame
    for phase, sensor_id, sensor_description, checked in sensors:
        frame = phase_frames[phase]

        # Create checkbox and label in the current phase frame
        checkbox_bool_var = tk.BooleanVar(value=checked)
        checkbox_vars[phase][sensor_id] = checkbox_bool_var
        checkbox = tk.Checkbutton(frame, text=f"{sensor_id}: {sensor_description}", variable=checkbox_bool_var,
                                  command=lambda v=checkbox_bool_var, sid=sensor_id, p=phase: get_checkboxes_values(v, sid, p))
        checkbox.grid(row=sensor_id, column=0, sticky="w")
        checkboxes.append(checkbox)
            
        # Store the initial checkbox state
        initial_checkbox_states[phase][sensor_id] = checked

    def get_checkboxes_values(checkbox_bool_var, sensor_id, phase):
        is_checked = checkbox_bool_var.get()

        # Update the bool value in the db
        cur.execute("UPDATE sensor SET checked = %s WHERE shelly_id = %s AND phase = %s AND sensor_id = %s",
                    (is_checked, shelly_id, phase, sensor_id))
        conn.commit()

    def apply_changes():
        messagebox.showinfo("Changes Applied", "Changes have been applied and the database has been updated.")
    
    def discard_changes():
        # Revert the checkbox states to the initial values
        for phase, checkbox in zip(checkbox_vars.keys(), checkboxes):
            checkbox_bool_var = checkbox_vars[phase]
            checkbox_bool_var.set(initial_checkbox_states[phase])

        # Update the database with the initial checkbox states
        for phase, initial_states in initial_checkbox_states.items():
            for sensor_id, initial_state in initial_states.items():
                cur.execute("UPDATE sensor SET checked = %s WHERE shelly_id = %s AND phase = %s AND sensor_id = %s", (initial_state, shelly_id, phase, sensor_id))
        conn.commit()

        messagebox.showinfo("Changes Discarded", "Changes have been discarded and the database has been reverted to the initial state.")

    # Create the Apply Changes button
    button_apply_changes = tk.Button(sensor_table_window, text="Apply Changes", command=apply_changes)
    button_apply_changes.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Create the Discard Changes button
    #button_discard_changes = tk.Button(sensor_table_window, text="Discard Changes", command=discard_changes)
    #button_discard_changes.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Define the function to be executed every 30 seconds
def run_cron_job():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(5).seconds.do(send_request)

def main():
    connect()
    create_tables()
    tkinter_init()

    # Start the cron job in a separate thread
    cron_thread = threading.Thread(target=run_cron_job)
    cron_thread.start()
    
    window.mainloop()
    cron_thread.join()
    
    disconnect()

if __name__ == '__main__':
    main()
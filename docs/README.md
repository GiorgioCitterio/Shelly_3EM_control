# Shelly 3 EM Control Documentation

![GitHub all releases](https://img.shields.io/github/downloads/GiorgioCitterio/Shelly_3EM_control/total)
![GitHub](https://img.shields.io/github/license/GiorgioCitterio/Shelly_3EM_control)
![GitHub deployments](https://img.shields.io/github/deployments/GiorgioCitterio/Shelly_3EM_control/github-pages)
![GitHub repo size](https://img.shields.io/github/repo-size/GiorgioCitterio/Shelly_3EM_control)
![GitHub Repo stars](https://img.shields.io/github/stars/GiorgioCitterio/Shelly_3EM_control)

<p align="left">
  <a href="https://www.python.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40" style="margin: 5px;" />
  </a>
  <a href="https://www.postgresql.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="40" height="40" style="margin: 5px;" />
  </a>
</p>

<a href="https://github.com/GiorgioCitterio/Shelly_3EM_control/blob/master/docs/README.it.md">README it</a>

---

This documentation explains how to use a Python program called Shelly 3 EM Control (`ShellyEm_control.py`) that utilizes the cloud APIs of a Shelly 3 EM device to make periodic requests and process measured data. The program stores the data in a PostgreSQL database and includes a graphical interface built with Tkinter, which allows users to search for the Shelly ID and view activated sensors for data measurement.

## Python Program Documentation for Interacting with Shelly 3EM APIs and Using PostgreSQL Database via Python

The following Python code is designed to interact with the cloud APIs of a Shelly 3EM device, make periodic requests to retrieve sensor data, and save that data in a PostgreSQL database. The program also includes a Tkinter-based graphical interface to search for the Shelly ID and view activated sensors for data measurement.

### Dependencies
The program requires the installation of the following Python modules:
- `requests`: Used for making HTTP requests to the Shelly APIs.
- `schedule`: Used for scheduling and executing periodic requests to the APIs.
- `json`: Used for manipulating data in JSON format.
- `psycopg2`: Used for connecting to the PostgreSQL database.
- `config`: Custom module for configuring the database connection parameters.
- `tkinter`: Module for creating the graphical interface.
- `threading`: Used to run the cron job in a separate thread.
- `classes.Em` and `classes.Sensor`: Custom modules defining the `Em` and `Sensor` classes used in the program.

### Configuration
Before running the program, some configurations need to be made:
- Modify the Shelly 3EM API URL within the `url` variable in the code.
- Set the values of the `body_data` variable correctly to authenticate and identify the correct Shelly device.
- Configure the connection parameters for the PostgreSQL database. To do this, create a `database.ini` file in the `Shelly_3em` directory with the following fields:
```
[postgresql]
host=localhost
database=db_name
user=username
password=password
```

### Program Functionality
The program is divided into several functions to handle different phases of interacting with the Shelly APIs and managing data in the database. Here is an overview of the main functions and their purposes:

1. `connect()`: Function to connect to the PostgreSQL database using the configured connection parameters. It creates a `conn` object for the connection and a `cur` object for the database cursor.
2. `disconnect()`: Function to disconnect from the database. It closes the cursor and the database connection.
3. `create_tables()`: Function to create the `measurements` and `sensor` tables in the database if they don't already exist. These tables are used to store sensor data and information about activated sensors for each Shelly ID and phase.
4. `insert_lists()`: Function to insert sensor and measurement data into the database. It uses the `sensor_list` and `measurement_list` lists to retrieve the data to be inserted. It also checks if the sensors already exist in the database before performing the insertion.
5. `send_request()`: Function to send a request to the Shelly APIs to retrieve sensor data. It uses the `requests` library to send a POST request to the URL specified in the `url` variable, along with the authentication and Shelly device identification parameters. The response is then converted to JSON format and parsed to extract sensor data and corresponding measurements.

6. `tkinter_init()`: Function to initialize the graphical interface using the Tkinter library. It creates a main window and adds labels, input fields, and buttons for user interaction.

7. `search()`: Function to search for a Shelly device in the database using the ID specified by the user in the graphical interface. It executes a query to check if the ID exists in the database and displays a dialog window with the search result.

8. `open_sensor_table_window()`: Function to open a separate window displaying the sensor table for a specific Shelly device. It retrieves sensor data from the database and creates checkboxes corresponding to the sensors in the window. It allows the user to modify the state of the checkboxes and apply or cancel the changes.

9. `run_cron_job()`: Function that is cyclically executed every 5 seconds using the `schedule` library. It invokes the `send_request()` function to retrieve sensor data from the Shelly APIs.

10. `main()`: Main function of the program. It handles establishing the database connection, creating tables, initializing the graphical interface, starting the cron job in a separate thread, and managing program exit.

These are the main functions that make up the program and perform various operations such as database management, interaction with the Shelly APIs, and handling the graphical interface. This is an overview, and you can extend or modify the code to fit your specific needs.

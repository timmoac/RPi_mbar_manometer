from tkinter import *
from tkinter import ttk, filedialog
import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas

# --------------
# global vars
# --------------
pressure_mbar_str = []
pressure_mbar = []
time_measurement = []
recording_in_prog = False
# fig_2 = plt.figure(figsize=(15, 7))

# --------------
# func def
# --------------


def open_port(index, values, op):
    global status_report
    try:
        serial.Serial(COM_Port.get(), 9600)
        time.sleep(1)
        status_report.set('Connection established')
        com_select.configure(state=DISABLED)
        start_recording.configure(state=NORMAL)

    except serial.SerialException:
        status_report.set('Raspberry Pi not found')


def start_recording():
    global pressure_mbar_str
    global pressure_mbar
    global recording_in_prog
    global time_measurement

    recording_in_prog = True
    stop_recording.configure(state=NORMAL)
    start_recording.configure(state=DISABLED)
    export_image.configure(state=DISABLED)
    export_csv.configure(state=DISABLED)
    live_monitor.configure(state=NORMAL)
    status_report.set('Recording Vacuum')
    pressure_mbar = []
    pressure_mbar_str = []
    time_measurement = []


def recording():
    global pressure_mbar_str

    if recording_in_prog:
        data = serial.Serial(COM_Port.get(), 9600).readline()
        pressure_mbar_str.append(str(data, 'UTF-8'))

    root.after(10, recording)


def stop_recording():
    global recording_in_prog
    global pressure_mbar_str
    global pressure_mbar
    global time_measurement
    time_incremental = 0

    recording_in_prog = False

    for i in pressure_mbar_str:
        i = i[:-4]
        pressure_mbar.append(float(i))
        time_incremental += 50
        time_measurement.append(time_incremental)

    time_measurement = [i / 1000 for i in time_measurement]

    print(pressure_mbar)
    print(time_measurement)
    print(len(pressure_mbar))

    stop_recording.configure(state=DISABLED)
    start_recording.configure(state=NORMAL)
    export_image.configure(state=NORMAL)
    export_csv.configure(state=NORMAL)
    status_report.set(f'{len(pressure_mbar)} Values recorded.')


def export_image():
    global pressure_mbar
    global time_measurement

    fig_1 = plt.figure(figsize=(15, 7))
    plt.plot(time_measurement, pressure_mbar)
    plt.ylabel('pressure [mbar]')
    plt.xlabel('time [s]')
    plt.show()


def export_csv():
    global pressure_mbar
    global time_measurement

    df_entries = {'Pressure': pressure_mbar, 'Time': time_measurement}
    df = pandas.DataFrame(data=df_entries)

    try:
        with filedialog.asksaveasfile(mode='w', defaultextension=".xlsx") as file:
            df.to_excel(file.name)
            status_report.set('File saved')

    except AttributeError:
        status_report.set('Export Cancelled')

    print(df)


def live_monitor():
    pass

# --------------
# GUI
# --------------

root = Tk()
root.title('Manometer 1.0')

# COM_Port Selection
COM_Port = StringVar()
COM_Port.set('COM1')
COM_Port.trace('w', open_port)
com_select = ttk.Combobox(root, textvariable=COM_Port)
com_select['values'] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10', 'COM11',
                        'COM12', 'COM13', 'COM14', 'COM15')
com_select.grid(column=0, row=0)

# Pressure Widget showing current pressure after COM connection is established
# com_select.bind('<<ComboboxSelected>>', get_pressure)

# Start Recording Button
start_recording = Button(root, text='Start Recording', command=start_recording, state=DISABLED)
start_recording.grid(column=0, row=2)

stop_recording = Button(root, text='Stop Recording', command=stop_recording)
stop_recording.grid(column=1, row=2)
stop_recording.configure(state=DISABLED)

# Recording Status
status_report = StringVar()
status_report.set('Select COM_Port')
status = Label(root, textvariable=status_report)
status.grid(column=1, row=0, padx=40)

# Data Export Image
export_image = Button(root, text='Export Image', command=export_image, state=DISABLED)
export_image.grid(column=0, row=3)

# Data Export CSV
export_csv = Button(root, text='Export Excel', command=export_csv, state=DISABLED)
export_csv.grid(column=1, row=3)

# Live Monitor
live_monitor = Button(root, text='Live Monitor', command=live_monitor, state=DISABLED)
live_monitor.grid(column=3, row=2)

root.after(1000, recording)
root.mainloop()

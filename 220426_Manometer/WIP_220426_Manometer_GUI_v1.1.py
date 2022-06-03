from tkinter import *
from tkinter import ttk, filedialog
import serial
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas
from timeit import default_timer as timer
import matplotlib.animation as animation
from threading import *

# --------------
# global vars
# --------------
pressure_mbar_str = []
pressure_mbar = []
time_measurement = []
recording_in_prog = False
start_timer = 0
end_timer = 0


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
    global start_timer

    recording_in_prog = True
    time_measurement = []
    start_timer = timer()
    stop_recording.configure(state=NORMAL)
    start_recording.configure(state=DISABLED)
    export_image.configure(state=DISABLED)
    export_csv.configure(state=DISABLED)
    status_report.set('Recording Vacuum')
    pressure_mbar = []
    pressure_mbar_str = []

    # print(start_timer)


def recording():
    global pressure_mbar_str
    global time_measurement
    global end_timer
    global start_timer

    if recording_in_prog:
        end_timer = timer()
        time_measurement.append(end_timer - start_timer)
        data = serial.Serial(COM_Port.get(), 9600).readline()
        pressure_mbar_str.append(str(data, 'UTF-8'))

    root.after(10, recording)


def stop_recording():
    global recording_in_prog
    global pressure_mbar_str
    global pressure_mbar
    global time_measurement

    recording_in_prog = False

    for i in pressure_mbar_str:
        i = i[:-4]
        pressure_mbar.append(float(i))

    # print(pressure_mbar)
    # print(time_measurement)

    stop_recording.configure(state=DISABLED)
    start_recording.configure(state=NORMAL)
    export_image.configure(state=NORMAL)
    export_csv.configure(state=NORMAL)
    status_report.set(f'{len(pressure_mbar)} Values recorded.')


def export_image():
    global pressure_mbar
    global time_measurement

    plt.figure(figsize=(15, 7))
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


def live_plot(i):
    global recording_in_prog
    global pressure_mbar_str
    global time_measurement
    global end_timer
    global start_timer

    if recording_in_prog:
        try:
            serial.Serial(COM_Port.get(), 9600)
            live_data = serial.Serial(COM_Port.get(), 9600).readline().decode('UTF-8')
            yar.append(float(live_data[:4]))
            xar.append(end_timer - start_timer)
            line.set_data(xar, yar)
            live_plot1.set_xlim(0, max(xar))
            live_plot1.set_ylim(min(yar) - 2, max(yar) + 2)

        except serial.SerialException:
            print('Serial Exception')


# --------------
# GUI
# --------------

root = Tk()
root.title('Manometer 1.06')

# COM_Port Selection
COM_Port = StringVar()
COM_Port.set('COM1')
COM_Port.trace('w', open_port)
com_select = ttk.Combobox(root, textvariable=COM_Port, width=56)
com_select['values'] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10', 'COM11',
                        'COM12', 'COM13', 'COM14', 'COM15')
com_select.grid(column=0, row=0, sticky=W, padx=5, pady=5)

# Start Recording Button
start_recording = Button(root, text='Start Recording', command=start_recording, state=DISABLED, width=50)
start_recording.grid(column=0, row=1, padx=5, sticky=W, pady=5)

# Stop Recording Button
stop_recording = Button(root, text='Stop Recording', command=stop_recording, width=50)
stop_recording.grid(column=1, row=1, padx=5, pady=5)
stop_recording.configure(state=DISABLED)

# Recording Status
status_report = StringVar()
status_report.set('Select COM_Port')
status = Label(root, textvariable=status_report)
status.grid(row=0, column=1, sticky=W)

# Data Export Image
export_image = Button(root, text='Export Image', command=export_image, state=DISABLED, width=50)
export_image.grid(column=2, row=1, padx=5, pady=5)

# Data Export CSV
export_csv = Button(root, text='Export Excel', command=export_csv, state=DISABLED, width=50)
export_csv.grid(column=3, row=1, sticky=E, padx=5, pady=5)

# Plotting Live Data
xar = []
yar = []

live_fig = plt.figure(figsize=(15, 7))
live_plot1 = live_fig.add_subplot(1, 1, 1)

line, = live_plot1.plot(xar, yar, 'b')

live_plot_root = FigureCanvasTkAgg(live_fig, master=root)
live_plot_root.get_tk_widget().grid(row=4, sticky=S, columnspan=4)
live_ani = animation.FuncAnimation(live_fig, live_plot, frames=100, interval=20, blit=False)

root.after(1000, recording)
root.mainloop()

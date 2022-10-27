from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import tkinter as tk
import webbrowser
import pandas as pd
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from tkinter import font
import matplotlib
import numpy

# Basic window configuration
root = Tk()
root.title('ChampSim - Simulation Results')
icon = PhotoImage(file='icons/4.png')
root.iconphoto(False, icon)
width, height = root.winfo_screenwidth(), root.winfo_screenheight()

scalingFactor = 1.5 * (width * height) / (1920 * 1080)
if scalingFactor < 1.28:
    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=7)
    root.option_add("*Font", default_font)

root.geometry("%dx%d+0+0" % (width, height))

# Font Control
desired_font = tk.font.Font(size=11, weight='normal')
button_font = tk.font.Font(size=10, weight='bold')
if scalingFactor < 1.28:
    desired_font = default_font
    button_font = default_font

# Global variables

default_filename = "../results/results.csv"
root.filename = default_filename

global valid_data


# # # # # # #
# Functions #
# # # # # # #


def hola():
    print('Hola')


def open_webpage(args):
    url = args
    webbrowser.open(url, new=1)


def checked_default_csv():
    if use_default_CSV_state.get():
        filename_CSV_entry.configure(state='readonly')
        browse_btn.configure(state='disabled')
        load_btn.configure(state='disabled')
        load_hint.set(default_filename)
    else:
        filename_CSV_entry.configure(state='normal')
        browse_btn.configure(state='normal')
        load_btn.configure(state='normal')


def open_file():
    # Define support for CSV files
    filetype = (
        ('CSV Files', '*.csv'),
        ('All files', '*.*')
    )

    root.filename = fd.askopenfilename(
        title='Load Simulation Results',
        initialdir='../',
        filetypes=filetype
    )

    load_hint.set(root.filename)


def reset_gui():
    print("GUI resets")


def load_file():
    global valid_data
    try:
        results_dataframe = pd.read_csv(root.filename)
        reset_gui()
        print(results_dataframe)
    except:
        valid_data = False
        mb.showerror(message="An error occurred while processing this data. Please try again later.",
                     title="Invalid data")
    else:
        valid_data = True


# Main menu.
menubar = tk.Menu(root)

# File menu
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label='Run', command=hola, accelerator="F5")
file_menu.add_separator()
file_menu.add_command(label='Exit', command=hola, accelerator="Alt+F4")
menubar.add_cascade(label='File', menu=file_menu, underline=0)

# About menu
repo_ChampSim = "https://github.com/ChampSim/ChampSim"
repo_ChampSim_GUI = "https://github.com/alexcato5/ChampSim_GUI"
Help = tk.Menu(menubar, tearoff=0)
Help.add_command(label="ChampSim's Official Repository", command=lambda: open_webpage(repo_ChampSim))
Help.add_command(label="ChampSim Results GUI Repository", command=lambda: open_webpage(repo_ChampSim_GUI))
Help.add_separator()
Help.add_command(label="About me...", command=hola)
menubar.add_cascade(label='Help', menu=Help, underline=0)

# # # # # # # # # # #
# Root LabelFrames #
# # # # # # # # # #

# Load File LabelFrame
load_file_lbl = LabelFrame(root, text='Current results file', font=desired_font, labelanchor='n', pady=20)
load_file_lbl.grid(column=1, sticky="NSEW", row=1, columnspan=1)

use_default_CSV_state = tk.BooleanVar(root)
use_default_CSV_state.set(True)
use_default_CSV_text = tk.StringVar()
use_default_CSV_text.set("Use ChampSim's default output CSV file")
use_default_CSV_chkbtn = tk.Checkbutton(load_file_lbl,
                                        textvariable=use_default_CSV_text,
                                        variable=use_default_CSV_state,
                                        command=checked_default_csv,
                                        font=desired_font)

use_default_CSV_chkbtn.grid(row=1,
                            column=2,
                            sticky=tk.W,
                            padx=70)

load_hint = tk.StringVar(root, root.filename)
filename_CSV_entry = tk.Entry(load_file_lbl, textvariable=load_hint, justify='center')
filename_CSV_entry.grid(row=2, column=2, ipadx=150, padx=10, pady=5)
filename_CSV_entry.configure(state='readonly')
tk.Label(load_file_lbl, text='File path:', font=desired_font).grid(row=2, column=1, pady=20, sticky=tk.W)

browse_btn = tk.Button(load_file_lbl, text='Browse', font=button_font, width=5, command=open_file)
browse_btn.configure(state='disabled')
browse_btn.grid(row=2, column=3, padx=10, ipady=5)

load_btn = tk.Button(load_file_lbl, text='Load results', font=button_font, width=10, command=load_file)
load_btn.configure(state='disabled')
load_btn.grid(row=3, column=2, pady=30)

# Basic system data LabelFrame
system_data_lbl = LabelFrame(root, text='Basic System Data', font=desired_font, labelanchor='n')
system_data_lbl.grid(column=1, sticky="NSEW", row=2, columnspan=1)
new_btn = tk.Button(system_data_lbl, text='New', font=button_font, width=5, command=open_file)
new_btn.grid(row=2, column=3, padx=10, ipady=5)

# Imported data LabelFrame
imported_data_lbl = LabelFrame(root, text='Imported ChampSim Results', font=desired_font, labelanchor='n')
imported_data_lbl.grid(column=1, sticky="NSEW", row=3, columnspan=1)
new_btn2 = tk.Button(imported_data_lbl, text='New', font=button_font, width=5, command=open_file)
new_btn2.grid(row=2, column=3, padx=10, ipady=5)

# Plots LabelFrame
plots_lbl = LabelFrame(root, text='Simulation results plots', font=desired_font, labelanchor='n')
plots_lbl.grid(column=2, sticky="NSEW", row=1, columnspan=1)
new_btn3 = tk.Button(plots_lbl, text='New', font=button_font, width=5, command=open_file)
new_btn3.grid(row=2, column=3, padx=10, ipady=5)

'''
# Figures.
fig1 = Figure(figsize=(5,5),dpi=100)
fig1, ax1 = plt.subplots()
canvas1 = FigureCanvasTkAgg(fig1,master=frameNW)
canvas1.get_tk_widget().config(width=330,height=310)

# Pop-up window Figures.
time_figure = Figure(figsize=(5,5), dpi=100)
time_figure, time_axis = plt.subplots()
time_axis.set_xlabel('Time (s)')
time_axis.set_ylabel('Amplitude')
versus_figure = Figure(figsize=(5,5),dpi=100)
versus_figure, versus_axis = plt.subplots()
versus_axis.set_xlabel('Time (s)')
versus_axis.set_ylabel('Amplitude')

time_figure_window = tk.Toplevel(root)
time_figure_window.geometry('700x550')
time_figure_window.resizable(False,False)
canvasI = FigureCanvasTkAgg(time_figure, master=time_figure_window)
canvasI.get_tk_widget()
toolbarI = NavigationToolbar2Tk(canvasI, time_figure_window)
toolbarI.update()
canvasI.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
'''

root.config(menu=menubar)
root.mainloop()

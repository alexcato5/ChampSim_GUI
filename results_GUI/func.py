from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import tkinter as tk
import webbrowser
import pandas as pd
from tkinter import font
# from tkinter import ttk
import matplotlib
import numpy

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


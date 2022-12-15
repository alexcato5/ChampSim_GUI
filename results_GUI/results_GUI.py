from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import webbrowser
import pandas as pd
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np


# # # # # # # # # # # # # # # #
# Basic window configuration #
# # # # # # # # # # # # # # #

root = Tk()
root.title('ChampSim - Simulation Results')
icon = PhotoImage(file='icons/4.png')
root.iconphoto(False, icon)
width, height = root.winfo_screenwidth(), root.winfo_screenheight()

# Scaling control
scalingFactor = 1.5 * (width * height) / (1920 * 1080)

# Font control
desired_font = tk.font.Font(size=11, weight='normal')
button_font = tk.font.Font(size=10, weight='bold')
if scalingFactor < 1.28:
    default_font = tk.font.nametofont("TkDefaultFont")
    default_font.configure(size=7)
    root.option_add("*Font", default_font)
    desired_font = default_font
    button_font = default_font

root.geometry("%dx%d+0+0" % (width, height))

# Global variables
default_filename = "../results/results.csv"
root.filename = default_filename
warmup_instructions = 0
simulation_instructions = 0
dram_size = 0
dram_number_of_channels = 0
dram_channel_width = 0
dram_data_rate = 0
vmem_capacity = 0
vmem_num_pages = 0
vmem_page_size = 0
vmem_log2_page_size = 0
current_cpu = tk.StringVar()
current_cpu_first_source = tk.StringVar()
current_cpu_second_source = tk.StringVar()
current_cpu_time_source = tk.StringVar()
cpu_trace = []
cpu_branch_prediction = []
cpu_basic_btb_sets = []
cpu_basic_btb_ways = []
cpu_ibuffer_size = []
cpu_ras_size = []
number_of_cpus = 0
cpu_options = ['CPU X']
valid_data = False
dram_variables = ["first", "second"]
type_of_results_first_source = tk.IntVar()
type_of_results_second_source = tk.IntVar()
type_of_results_time = tk.IntVar()


global results_dataframe
global results_dataframe_parameters
global time_combobox_options
global counter_first_combobox_options
global counter_second_combobox_options
global x_axis_counter
global x_axis_time
global y_axis_counter
global y_axis_time
global time_labels
time_labels = []
y_axis_time = []

# # # # # #
# Classes #
# # # # # #


class CreateToolTip(object):
    """
    create a tooltip for a given widget. Source:
    https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 150
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left', background="#ffffff", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


# # # # # # #
# Functions #
# # # # # # #

# For debugging purposes
def hola():
    print('Hola')


def open_webpage(args):
    url = args
    webbrowser.open(url, new=1)


def checked_default_csv():
    if use_default_CSV_state.get():
        filename_CSV_entry.configure(state='readonly')
        browse_btn.configure(state='disabled')
        load_btn.configure(state='normal')
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
    global warmup_instructions
    warmup_instructions = 0
    global simulation_instructions
    simulation_instructions = 0
    global dram_size
    dram_size = 0
    global dram_number_of_channels
    dram_number_of_channels = 0
    global dram_channel_width
    dram_channel_width = 0
    global dram_data_rate
    dram_data_rate = 0
    global vmem_capacity
    vmem_capacity = 0
    global vmem_num_pages
    vmem_num_pages = 0
    global vmem_page_size
    vmem_page_size = 0
    global vmem_log2_page_size
    vmem_log2_page_size = 0
    global current_cpu
    current_cpu = tk.StringVar()
    global cpu_trace
    cpu_trace = []
    global cpu_branch_prediction
    cpu_branch_prediction = []
    global cpu_basic_btb_sets
    cpu_basic_btb_sets = []
    global cpu_basic_btb_ways
    cpu_basic_btb_ways = []
    global cpu_ibuffer_size
    cpu_ibuffer_size = []
    global cpu_ras_size
    cpu_ras_size = []
    global number_of_cpus
    number_of_cpus = 0


def fill_system_info():
    global number_of_cpus
    number_of_cpus = results_dataframe.loc['system_info_number_of_cpus'][-1]
    number_of_cpus_hint = tk.IntVar(root, number_of_cpus)
    number_of_cpus_entry = tk.Entry(system_data_lblfr, textvariable=number_of_cpus_hint, justify='center')
    number_of_cpus_entry.grid(row=1, column=3, columnspan=1, pady=10, sticky=W)
    number_of_cpus_entry.configure(state='readonly')

    global warmup_instructions
    warmup_instructions = results_dataframe.loc['system_info_warmup_instructions'][-1]
    warmup_instructions_hint = tk.StringVar(root, warmup_instructions)
    warmup_instructions_entry = tk.Entry(system_data_lblfr, textvariable=warmup_instructions_hint, justify='center')
    warmup_instructions_entry.grid(row=2, column=2, columnspan=1, padx=10, pady=5)
    warmup_instructions_entry.configure(state='readonly')

    global simulation_instructions
    simulation_instructions = results_dataframe.loc['system_info_simulation_instructions'][-1]
    simulation_instructions_hint = tk.StringVar(root, simulation_instructions)
    simulation_instructions_entry = tk.Entry(system_data_lblfr, textvariable=simulation_instructions_hint, justify='center')
    simulation_instructions_entry.grid(row=2, column=4, columnspan=1, padx=10, pady=5)
    simulation_instructions_entry.configure(state='readonly')

    global dram_size
    dram_size = results_dataframe.loc['system_info_off_chip_dram_size'][-1]
    dram_size_hint = tk.StringVar(root, dram_size)
    dram_size_entry = tk.Entry(system_data_lblfr, textvariable=dram_size_hint, justify='center')
    dram_size_entry.grid(row=4, column=2, columnspan=1, padx=10, pady=5)
    dram_size_entry.configure(state='readonly')

    global dram_number_of_channels
    dram_number_of_channels = results_dataframe.loc['system_info_gib_channels'][-1]
    dram_number_of_channels_hint = tk.StringVar(root, dram_number_of_channels)
    dram_number_of_channels_entry = tk.Entry(system_data_lblfr, textvariable=dram_number_of_channels_hint, justify='center')
    dram_number_of_channels_entry.grid(row=4, column=4, columnspan=1, padx=10, pady=5)
    dram_number_of_channels_entry.configure(state='readonly')

    global dram_channel_width
    dram_channel_width = results_dataframe.loc['system_info_width'][-1]
    dram_channel_width_hint = tk.StringVar(root, dram_channel_width)
    dram_channel_width_entry = tk.Entry(system_data_lblfr, textvariable=dram_channel_width_hint, justify='center')
    dram_channel_width_entry.grid(row=5, column=2, columnspan=1, padx=10, pady=5)
    dram_channel_width_entry.configure(state='readonly')

    global dram_data_rate
    dram_data_rate = results_dataframe.loc['system_info_data_rate'][-1]
    dram_data_rate_hint = tk.StringVar(root, dram_data_rate)
    dram_data_rate_entry = tk.Entry(system_data_lblfr, textvariable=dram_data_rate_hint, justify='center')
    dram_data_rate_entry.grid(row=5, column=4, columnspan=1, padx=10, pady=5)
    dram_data_rate_entry.configure(state='readonly')

    global vmem_capacity
    vmem_capacity = results_dataframe.loc['system_info_virtualmemory_physical_capacity'][-1]
    vmem_capacity_hint = tk.StringVar(root, vmem_capacity)
    vmem_capacity_entry = tk.Entry(system_data_lblfr, textvariable=vmem_capacity_hint, justify='center')
    vmem_capacity_entry.grid(row=6, column=2, columnspan=1, padx=10, pady=5)
    vmem_capacity_entry.configure(state='readonly')

    global vmem_num_pages
    vmem_num_pages = results_dataframe.loc['system_info_num_ppages'][-1]
    vmem_num_pages_hint = tk.StringVar(root, vmem_num_pages)
    vmem_num_pages_entry = tk.Entry(system_data_lblfr, textvariable=vmem_num_pages_hint, justify='center')
    vmem_num_pages_entry.grid(row=6, column=4, columnspan=1, padx=10, pady=5)
    vmem_num_pages_entry.configure(state='readonly')

    global vmem_page_size
    vmem_page_size = results_dataframe.loc['system_info_virtualmemory_page_size'][-1]
    vmem_page_size_hint = tk.StringVar(root, vmem_page_size)
    vmem_page_size_entry = tk.Entry(system_data_lblfr, textvariable=vmem_page_size_hint, justify='center')
    vmem_page_size_entry.grid(row=7, column=2, columnspan=1, padx=10, pady=5)
    vmem_page_size_entry.configure(state='readonly')

    global vmem_log2_page_size
    vmem_log2_page_size = results_dataframe.loc['system_info_log2_page_size'][-1]
    vmem_log2_page_size_hint = tk.StringVar(root, vmem_log2_page_size)
    vmem_log2_page_size_entry = tk.Entry(system_data_lblfr, textvariable=vmem_log2_page_size_hint, justify='center')
    vmem_log2_page_size_entry.grid(row=7, column=4, columnspan=1, padx=10, pady=5)
    vmem_log2_page_size_entry.configure(state='readonly')

    global cpu_options
    cpu_options = []
    for i in range(0, int(number_of_cpus)):
        cpu_options.append('CPU ' + str(i))
        cpu_trace.append(results_dataframe.loc['system_info_cpu_' + str(i) + '_runs'][-1])
        cpu_branch_prediction.append(results_dataframe.loc['cpu_' + str(i) + '_branch_predictor'][-1])
        cpu_basic_btb_sets.append(results_dataframe.loc['system_info_cpu' + str(i) + '_basic_btb_sets'][-1])
        cpu_basic_btb_ways.append(results_dataframe.loc['system_info_cpu' + str(i) + '_ways'][-1])
        cpu_ibuffer_size.append(results_dataframe.loc['system_info_cpu' + str(i) + '_indirect_buffer_size'][-1])
        cpu_ras_size.append(results_dataframe.loc['system_info_cpu' + str(i) + '_ras_size'][-1])

    current_cpu.set('CPU X')
    cpu_drop = tk.OptionMenu(system_data_lblfr, current_cpu, *cpu_options, command=lambda e: refresh_current_cpu_info())
    cpu_drop.grid(row=9, column=3, sticky=W)


def refresh_current_cpu_info():
    cpu_trace_hint = tk.StringVar(root, cpu_trace[int(current_cpu.get()[-1])])
    cpu_trace_entry = tk.Entry(system_data_lblfr, textvariable=cpu_trace_hint, justify='center')
    cpu_trace_entry.grid(row=10, column=2, columnspan=3, padx=10, pady=5, ipadx=150)
    cpu_trace_entry.configure(state='readonly')
    cpu_branch_prediction_hint = tk.StringVar(root, cpu_branch_prediction[int(current_cpu.get()[-1])])
    cpu_branch_prediction_entry = tk.Entry(system_data_lblfr, textvariable=cpu_branch_prediction_hint, justify='center')
    cpu_branch_prediction_entry.grid(row=11, column=2, columnspan=3, padx=10, pady=5, ipadx=75)
    cpu_branch_prediction_entry.configure(state='readonly')
    cpu_basic_btb_sets_hint = tk.StringVar(root, cpu_basic_btb_sets[int(current_cpu.get()[-1])])
    cpu_basic_btb_sets_entry = tk.Entry(system_data_lblfr, textvariable=cpu_basic_btb_sets_hint, justify='center')
    cpu_basic_btb_sets_entry.grid(row=12, column=2, columnspan=1, padx=10, pady=5)
    cpu_basic_btb_sets_entry.configure(state='readonly')
    cpu_basic_btb_ways_hint = tk.StringVar(root, cpu_basic_btb_ways[int(current_cpu.get()[-1])])
    cpu_basic_btb_ways_entry = tk.Entry(system_data_lblfr, textvariable=cpu_basic_btb_ways_hint, justify='center')
    cpu_basic_btb_ways_entry.grid(row=12, column=4, columnspan=1, padx=10, pady=5)
    cpu_basic_btb_ways_entry.configure(state='readonly')
    cpu_ibuffer_size_hint = tk.StringVar(root, cpu_ibuffer_size[int(current_cpu.get()[-1])])
    cpu_ibuffer_size_entry = tk.Entry(system_data_lblfr, textvariable=cpu_ibuffer_size_hint, justify='center')
    cpu_ibuffer_size_entry.grid(row=14, column=2, columnspan=1, padx=10, pady=5)
    cpu_ibuffer_size_entry.configure(state='readonly')
    cpu_ras_size_hint = tk.StringVar(root, cpu_ras_size[int(current_cpu.get()[-1])])
    cpu_ras_size_entry = tk.Entry(system_data_lblfr, textvariable=cpu_ras_size_hint, justify='center')
    cpu_ras_size_entry.grid(row=14, column=4, columnspan=1, padx=10, pady=5)
    cpu_ras_size_entry.configure(state='readonly')
    tk.Label(system_data_lblfr, text= current_cpu.get() + ' ran:', font=desired_font).grid(row=10, column=1,
                                                                                         pady=10, sticky=tk.N)


def load_file():
    global valid_data
    try:
        global results_dataframe
        results_dataframe = pd.read_csv(root.filename)
        mb.showinfo("Success", "Simulation results have been loaded successfully")
    except:
        valid_data = False
        mb.showerror(message="An error occurred while processing this data. Please try again later.",
                     title="Invalid data")
    else:
        global results_dataframe_parameters
        results_dataframe_parameters = results_dataframe['Parameter'].tolist()
        global time_combobox_options
        time_combobox_options = results_dataframe_parameters
        global counter_first_combobox_options
        counter_first_combobox_options = results_dataframe_parameters
        global counter_second_combobox_options
        counter_second_combobox_options = results_dataframe_parameters
        results_dataframe.set_index('Parameter', inplace=True)
        reset_gui()
        fill_system_info()
        valid_data = True


def combo_search(event):
    value = event.widget.get()
    if value == '' or value == ' ':
        event.widget['values'] = dram_variables
    else:
        matching_data = []
        for item in dram_variables:
            if value.lower() in item .lower():
                matching_data.append(item)
        event.widget['values'] = matching_data

def cpus_as_first_source():
    # Forget all previous widgets
    y_axis_lbl.grid_forget()
    combobox_selector_first_source.grid_forget()

    if valid_data:
        # Show all widgets
        generate_counter_graph_btn.configure(state='normal')
        cpu_as_first_source_lbl.grid(row=2, column=1, sticky=N)
        drop_first_source['menu'].delete(0, 'end')
        for opt in cpu_options:
            drop_first_source['menu'].add_command(label=opt, command=lambda value=opt: current_cpu_first_source.set(value))
        current_cpu_first_source.set('CPU X')
        drop_first_source.grid(row=2, column=2, sticky=N, padx=15)
        type_of_results_first_lbl.grid(row=2, column=1, sticky=S)
        total_first_source_rb.grid(ipadx=50, row=3, column=1, columnspan=2, sticky=N)
        interest_first_source_rb.grid(ipadx=50, row=3, column=1, columnspan=2, sticky=S)
        y_axis_lbl.grid(row=4, column=1, columnspan=2, sticky=tk.N, pady=10)
        combobox_selector_first_source.configure(state='normal')
        combobox_selector_first_source.grid(row=4, column=1, columnspan=2, ipadx=100, padx=20, sticky=S, pady=20)
        combobox_selector_first_source.set("Select or find parameter")
        combobox_selector_first_source.bind("<1>", lambda e: combobox_selector_first_source.set(''))
        combobox_selector_first_source.bind("<KeyRelease>", combo_search)
    else:
        results_first_source_counter.set(0)


def cpus_as_second_source():
    # Forget all previous widgets
    x_axis_lbl.grid_forget()
    combobox_selector_second_source.grid_forget()

    if valid_data:
        # Show all widgets
        generate_counter_graph_btn.configure(state='normal')
        cpu_as_second_source_lbl.grid(row=2, column=4, sticky=N)
        drop_second_source['menu'].delete(0, 'end')
        for opt in cpu_options:
            drop_second_source['menu'].add_command(label=opt, command=lambda value=opt: current_cpu_second_source.set(value))
        current_cpu_second_source.set('CPU X')
        drop_second_source.grid(row=2, column=5, sticky=N, padx=15)
        type_of_results_second_lbl.grid(row=2, column=4, sticky=S)
        total_second_source_rb.grid(ipadx=50, row=3, column=4, columnspan=2, sticky=N)
        interest_second_source_rb.grid(ipadx=50, row=3, column=4, columnspan=2, sticky=S)
        x_axis_lbl.grid(row=4, column=4, columnspan=2, sticky=tk.N, pady=10)
        combobox_selector_second_source.configure(state='normal')
        combobox_selector_second_source.grid(row=4, column=4, columnspan=2, ipadx=100, padx=20, sticky=S, pady=20)
        combobox_selector_second_source.set("Select or find parameter")
        combobox_selector_second_source.bind("<1>", lambda e: combobox_selector_second_source.set(''))
        combobox_selector_second_source.bind("<KeyRelease>", combo_search)
    else:
        results_second_source_counter.set(0)

def cpu_as_source_time():
    # Forget all previous widgets
    choose_time_lbl.grid_forget()
    combobox_selector_time.grid_forget()

    if valid_data:
        # Show all widgets
        add_to_time_graph_btn.configure(state='normal')
        cpu_as_time_source_lbl.grid(row=2, column=1+1, sticky=N)
        drop_time_source['menu'].delete(0, 'end')
        for opt in cpu_options:
            drop_time_source['menu'].add_command(label=opt, command=lambda value=opt: current_cpu_time_source.set(value))
        current_cpu_time_source.set('CPU X')
        drop_time_source.grid(row=2, column=2+1, sticky=N, padx=15)
        type_of_results_time_lbl.grid(row=3, column=1+1, sticky=N)
        total_time_rb.grid(ipadx=50, row=3, column=1+1, columnspan=2, sticky=SE)
        interest_time_rb.grid(ipadx=50, row=4, column=1+1, columnspan=2, sticky=NE)
        choose_time_lbl.grid(row=5, column=1+1, columnspan=2, sticky=N)
        combobox_selector_time.configure(state='normal')
        combobox_selector_time.grid(row=5, column=1+1, columnspan=2, ipadx=100, padx=20, sticky=S, pady=30)
        combobox_selector_time.set("Select or find parameter")
        combobox_selector_time.bind("<1>", lambda e: combobox_selector_time.set(''))
        combobox_selector_time.bind("<KeyRelease>", combo_search)
    else:
        results_source_time.set(0)


def dram_as_source_counter_first():
    # Forget all previous widgets
    cpu_as_first_source_lbl.grid_forget()
    drop_first_source.grid_forget()
    type_of_results_first_lbl.grid_forget()
    total_first_source_rb.grid_forget()
    interest_first_source_rb.grid_forget()
    y_axis_lbl.grid_forget()
    combobox_selector_first_source.grid_forget()
    if valid_data:
        generate_counter_graph_btn.configure(state='normal')
        y_axis_lbl.grid(row=2, column=1, columnspan=2, pady=0, sticky=N)
        combobox_selector_first_source.configure(state='normal')
        combobox_selector_first_source.grid(row=2, column=1, columnspan=2, ipadx=100, padx=20, sticky=S)
        combobox_selector_first_source.set("Select or find parameter")
        combobox_selector_first_source.bind("<1>", lambda e: combobox_selector_first_source.set(''))
        combobox_selector_first_source.bind("<KeyRelease>", combo_search)
    else:
        results_first_source_counter.set(0)


def dram_as_source_counter_second():
    # Forget all previous widgets
    cpu_as_second_source_lbl.grid_forget()
    drop_second_source.grid_forget()
    type_of_results_second_lbl.grid_forget()
    total_second_source_rb.grid_forget()
    interest_second_source_rb.grid_forget()
    x_axis_lbl.grid_forget()
    combobox_selector_second_source.grid_forget()

    if valid_data:
        generate_counter_graph_btn.configure(state='normal')
        x_axis_lbl.grid(row=2, column=4, columnspan=2, pady=0, sticky=N)
        combobox_selector_second_source.configure(state='normal')
        combobox_selector_second_source.grid(row=2, column=4, columnspan=2, ipadx=100, padx=20, sticky=S)
        combobox_selector_second_source.set("Select or find parameter")
        combobox_selector_second_source.bind("<1>", lambda e: combobox_selector_second_source.set(''))
        combobox_selector_second_source.bind("<KeyRelease>", combo_search)
    else:
        results_second_source_counter.set(0)


def dram_as_source_time():
    # Forget all previous widgets
    cpu_as_time_source_lbl.grid_forget()
    drop_time_source.grid_forget()
    type_of_results_time_lbl.grid_forget()
    total_time_rb.grid_forget()
    interest_time_rb.grid_forget()
    choose_time_lbl.grid_forget()
    combobox_selector_time.grid_forget()

    if valid_data:
        add_to_time_graph_btn.configure(state='normal')
        choose_time_lbl.grid(row=3, column=1+1, columnspan=2, pady=20, sticky=N)
        combobox_selector_time.configure(state='normal')
        combobox_selector_time.grid(row=4, column=1+1, columnspan=2, ipadx=100, padx=20, sticky=N, pady=20)
        combobox_selector_time.set("Select or find parameter")
        combobox_selector_time.bind("<1>", lambda e: combobox_selector_time.set(''))
        combobox_selector_time.bind("<KeyRelease>", combo_search)
    else:
        results_source_time.set(0)


def open_counter_plot():
    global x_axis_counter
    global y_axis_counter
    axI.clear()
    axI.scatter(x_axis_counter, y_axis_counter,label='Parameter vs. Parameter')
    axI.legend()
    axI.set_xlabel(f'{combobox_selector_second_source.get()}')
    axI.set_ylabel(f'{combobox_selector_first_source.get()}')
    plot_vs_full = tk.Toplevel(root)
    plot_vs_full.geometry('700x550')
    plot_vs_full.resizable(False, False)
    plot_vs_full.iconphoto(False, icon)
    canvas_vs_full = FigureCanvasTkAgg(figI, master=plot_vs_full)
    canvas_vs_full.get_tk_widget()
    toolbar_vs_full = NavigationToolbar2Tk(canvas_vs_full, plot_vs_full)
    toolbar_vs_full.update()
    canvas_vs_full.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def open_time_plot():
    axII.clear()
    for i in range(0, len(y_axis_time)):
        axII.plot(x_axis_time, y_axis_time[i])
    axII.legend(time_labels)
    axII.set_xlabel('Time ({})'.format('Multiples of execution cycles'))
    axII.set_ylabel(f'{combobox_selector_time.get()}')
    plot_time_full = tk.Toplevel(root)
    plot_time_full.geometry('700x550')
    plot_time_full.resizable(False, False)
    plot_time_full.iconphoto(False, icon)
    canvas_time_full = FigureCanvasTkAgg(figII, master=plot_time_full)
    canvas_time_full.get_tk_widget()
    toolbar_time_full = NavigationToolbar2Tk(canvas_time_full, plot_time_full)
    toolbar_time_full.update()
    canvas_time_full.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def update_cbox_counter_first():
    global counter_first_combobox_options
    counter_first_combobox_options = results_dataframe_parameters
    counter_first_combobox_options = [i for i in counter_first_combobox_options if 'system_info' not in str(i)]
    if results_first_source_counter.get() == 1:
        counter_first_combobox_options = [i for i in counter_first_combobox_options if 'dram' not in str(i)]
        counter_first_combobox_options = [i for i in counter_first_combobox_options if 'cpu' + current_cpu_first_source.get()[-1] in str(i)]
        if type_of_results_first_source.get() == 1:
            counter_first_combobox_options = [i for i in counter_first_combobox_options if 'roi' not in str(i)]
        else:
            counter_first_combobox_options = [i for i in counter_first_combobox_options if 'roi' in str(i)]
    else:
        counter_first_combobox_options = [i for i in counter_first_combobox_options if 'cpu' not in str(i)]
        counter_first_combobox_options = [i for i in counter_first_combobox_options if 'time' not in str(i)]

    combobox_selector_first_source['values'] = counter_first_combobox_options



def update_cbox_counter_second():
    global counter_second_combobox_options
    counter_second_combobox_options = results_dataframe_parameters
    counter_second_combobox_options = [i for i in counter_second_combobox_options if 'system_info' not in str(i)]
    if results_second_source_counter.get() == 1:
        counter_second_combobox_options = [i for i in counter_second_combobox_options if 'dram' not in str(i)]
        counter_second_combobox_options = [i for i in counter_second_combobox_options if 'cpu' + current_cpu_second_source.get()[-1] in str(i)]
        if type_of_results_second_source.get() == 1:
            counter_second_combobox_options = [i for i in counter_second_combobox_options if 'roi' not in str(i)]
        else:
            counter_second_combobox_options = [i for i in counter_second_combobox_options if 'roi' in str(i)]
    else:
        counter_second_combobox_options = [i for i in counter_second_combobox_options if 'cpu' not in str(i)]
        counter_second_combobox_options = [i for i in counter_second_combobox_options if 'time' not in str(i)]

    combobox_selector_second_source['values'] = counter_second_combobox_options


def update_cbox_time():
    global time_combobox_options
    time_combobox_options = results_dataframe_parameters
    time_combobox_options = [i for i in time_combobox_options if 'system_info' not in str(i)]
    if results_source_time.get() == 1:
        time_combobox_options = [i for i in time_combobox_options if 'dram' not in str(i)]
        time_combobox_options = [i for i in time_combobox_options if 'cpu' + current_cpu_time_source.get()[-1] in str(i)]
        if type_of_results_time.get() == 1:
            time_combobox_options = [i for i in time_combobox_options if 'roi' not in str(i)]
        else:
            time_combobox_options = [i for i in time_combobox_options if 'roi' in str(i)]
    else:
        time_combobox_options = [i for i in time_combobox_options if 'cpu' not in str(i)]
        time_combobox_options = [i for i in time_combobox_options if 'time' not in str(i)]

    combobox_selector_time['values'] = time_combobox_options


def plot_counter():
    ax1.clear()
    if combobox_selector_first_source.get().strip() == '' or 'Select' in combobox_selector_first_source.get().strip():
        mb.showerror(message="Please, choose the Y-axis parameter to plot",
                     title="Y-axis missing")
    elif combobox_selector_second_source.get().strip() == '' or 'Select' in combobox_selector_second_source.get().strip():
        mb.showerror(message="Please, choose the X-axis parameter to plot",
                     title="X-axis missing")
    else:
        plots_separator.grid(row=1, column=3, rowspan=1, pady=35, ipady=150)
        axI.set_xlabel(combobox_selector_second_source.get())
        axI.set_ylabel(combobox_selector_first_source.get())
        global x_axis_counter
        global y_axis_counter
        x_axis_counter = []
        y_axis_counter = []
        try:
            x_axis_counter = results_dataframe.loc[combobox_selector_second_source.get()].tolist()
            y_axis_counter = results_dataframe.loc[combobox_selector_first_source.get()].tolist()
            axis_len = len(x_axis_counter)
            m = 0
            while m < axis_len:
                if '-' in x_axis_counter[m]\
                or 'n' in x_axis_counter[m]\
                or '-' in y_axis_counter[m]\
                or 'n' in y_axis_counter[m]:
                    del x_axis_counter[m]
                    del y_axis_counter[m]
                    axis_len = axis_len - 1
                    mb.showwarning(message='Some datapoints were removed while plotting because they contained NaN values', title='NaN values detected')
                m = m + 1
            x_axis_counter = [float(x) for x in x_axis_counter]
            y_axis_counter = [float(y) for y in y_axis_counter]
        except:
            mb.showerror(message='An error occurred while plotting. Please try again', title='Plotting error')
        ax1.scatter(x_axis_counter, y_axis_counter)

        if scalingFactor < 1.28:
            plt.rcParams.update({'font.size': 7})
            ax1.set_xlabel(f'{combobox_selector_second_source.get()}', fontsize=7)
            ax1.set_ylabel('combobox', fontsize=7)
            ax1.set_title('Parameter vs. parameter function', fontsize=7)
            ax1.tick_params(axis='both', which='major', labelsize=7)
        else:
            plt.rcParams.update({'font.size': 10})
            ax1.set_xlabel(f'{combobox_selector_second_source.get()}', fontsize=8)
            ax1.set_ylabel(f'{combobox_selector_first_source.get()}', fontsize=8)
            ax1.set_title('Parameter vs parameter', fontsize=8)

        canvas_vs_tiny.draw()
        canvas_vs_tiny.get_tk_widget().grid(row=1, column=1, padx=20, pady=10)
        view_first_btn.grid(row=1, column=2, ipadx=10, ipady=5, padx=15)
        generate_counter_graph_btn.configure(state='disabled')
        results_first_source_counter.set(0)
        results_second_source_counter.set(0)
        combobox_selector_first_source.configure(state='disabled')
        combobox_selector_second_source.configure(state='disabled')


def plot_time():
    ax2.clear()
    if combobox_selector_time.get().strip() == '' or 'Select' in combobox_selector_time.get().strip():
        mb.showerror(message="Please, choose a parameter to plot as a time function",
                     title="Y-axis missing")
    else:
        axII.set_xlabel('Time (multiples of execution cycles)')
        axII.set_ylabel(combobox_selector_time.get())
        global x_axis_time
        global time_labels
        global y_axis_time
        x_axis_time = []
        nan_found = False
        try:
            y_axis_time_temp = results_dataframe.loc[combobox_selector_time.get()].tolist()
            x_axis_time = list(np.arange(0, len(y_axis_time_temp)))
            axis_len = len(x_axis_time)
            j = 0
            while j < axis_len:
                if '-' in y_axis_time_temp[j] or 'n' in y_axis_time_temp[j]:
                    del x_axis_time[j]
                    del y_axis_time_temp[j]
                    for i in range(0, len(y_axis_time)):
                        del y_axis_time[i][j]
                    axis_len = axis_len - 1
                    j = j - 1
                    nan_found = True
                j = j + 1
            if nan_found:
                mb.showwarning(message='Some datapoints were removed while plotting because they contained NaN values', title='NaN values detected')
            x_axis_time = [float(x) for x in x_axis_time]
            y_axis_time.append([float(y) for y in y_axis_time_temp])
        except:
            mb.showerror(message='An error occurred while plotting. Please try again', title='Plotting error')
        for i in range(0, len(y_axis_time)):
            ax2.plot(x_axis_time, y_axis_time[i])
            time_labels.append(combobox_selector_time.get())
        ax2.legend(labels=time_labels)
        if scalingFactor < 1.28:
            plt.rcParams.update({'font.size': 7})
            ax2.set_xlabel('Time ({})'.format('multiples of execution cycles'), fontsize=7)
            ax2.set_ylabel(f'{combobox_selector_time.get()}', fontsize=7)
            ax2.set_title('Parameter as a function of time', fontsize=7)
            ax2.tick_params(axis='both', which='major', labelsize=7)
        else:
            plt.rcParams.update({'font.size': 10})
            ax2.set_xlabel('Time ({})'.format('multiples of execution cycles'), fontsize=8)
            ax2.set_ylabel(f'{combobox_selector_time.get()}', fontsize=8)
            ax2.set_title('Parameter as a function of time', fontsize=8)

        canvas_time_tiny.draw()
        canvas_time_tiny.get_tk_widget().grid(row=1, column=4, padx=20, pady=10)
        view_second_btn.grid(row=1, column=5, ipadx=10, ipady=5, padx=15)
        add_to_time_graph_btn.configure(state='disabled')
        results_source_time.set(0)
        combobox_selector_time.configure(state='disabled')


# Main menu.
menubar = tk.Menu(root)

# File menu
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label='Run', command=hola, accelerator="F5")
file_menu.add_separator()
file_menu.add_command(label='Exit', accelerator="Alt+F4")
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

# # # # # # # #
# Root Frames #
# # # # # # # #

left_frame = Frame(root)
left_frame.grid(row=1, column=1, sticky=NSEW)

right_frame = Frame(root)
right_frame.grid(row=1, column=2, sticky=NSEW)

# # # # # # # # # # # # #
# Load File LabelFrame #
# # # # # # # # # # # #

load_file_lblfr = LabelFrame(left_frame, height=250, width=730, text='Current results file', font=desired_font,
                           labelanchor='n', pady=20)
load_file_lblfr.grid(column=1, sticky="NSEW", row=1, columnspan=1)
load_file_lblfr.grid_propagate(False)

use_default_CSV_state = tk.BooleanVar(root)
use_default_CSV_state.set(True)
use_default_CSV_text = tk.StringVar()
use_default_CSV_text.set("Use ChampSim's default output CSV file")
use_default_CSV_chkbtn = tk.Checkbutton(load_file_lblfr,
                                        textvariable=use_default_CSV_text,
                                        variable=use_default_CSV_state,
                                        command=checked_default_csv,
                                        font=desired_font)
use_default_CSV_chkbtn.grid(row=1, column=2, sticky=tk.N, padx=70)
load_hint = tk.StringVar(root, root.filename)
filename_CSV_entry = tk.Entry(load_file_lblfr, textvariable=load_hint, justify='center')
filename_CSV_entry.grid(row=2, column=2, ipadx=200, padx=10, pady=5)
filename_CSV_entry.configure(state='readonly')
tk.Label(load_file_lblfr, text='File path:', font=desired_font).grid(row=2, column=1, pady=20, sticky=tk.W)

browse_btn = tk.Button(load_file_lblfr, text='Browse', font=button_font, width=5, command=open_file)
browse_btn.configure(state='disabled')
browse_btn.grid(row=2, column=3, padx=10, ipady=5)

load_btn = tk.Button(load_file_lblfr, text='Load results', font=button_font, width=10, command=load_file)
load_btn.configure(state='normal')
load_btn.grid(row=3, column=2, pady=30)

# # # # # # # # # # # # # # # # #
# Basic system data LabelFrame #
# # # # # # # # # # # # # # # #

system_data_lblfr = LabelFrame(left_frame, height=100, width=900, text='Basic System Data', font=desired_font, labelanchor='n')
system_data_lblfr.grid(column=1, sticky="NSEW", row=2, columnspan=1, rowspan=2)
system_data_lblfr.propagate(False)
tk.Label(system_data_lblfr, text='Number of CPUs:', font=desired_font).grid(row=1, column=1, columnspan=3, pady=10, sticky=N)
tk.Label(system_data_lblfr, text='Warmup Instructions:', font=desired_font).grid(row=2, column=1, pady=10, sticky=N)
tk.Label(system_data_lblfr, text='Simulation Instructions:', font=desired_font).grid(row=2, column=3, pady=10, sticky=N)
ttk.Separator(system_data_lblfr,
              orient='horizontal',
              style='TSeparator'
              ).grid(row=3, column=1, columnspan=4, ipadx=275, padx=25)
tk.Label(system_data_lblfr, text='DRAM Specifications', font=desired_font).grid(row=3, columnspan=4, column=1, pady=10, sticky=tk.N)
tk.Label(system_data_lblfr, text='Size:', font=desired_font).grid(row=4, column=1, pady=20, sticky=tk.N)
tk.Label(system_data_lblfr, text='Number of Channels:', font=desired_font).grid(row=4, column=3, pady=20, sticky=tk.N)
tk.Label(system_data_lblfr, text='Width (GiB):', font=desired_font).grid(row=5, column=1, pady=20, padx=0, sticky=tk.N)
tk.Label(system_data_lblfr, text='Data Rate:', font=desired_font).grid(row=5, column=3, pady=20, padx=0, sticky=tk.N)
tk.Label(system_data_lblfr, text='Virtual Memory Physical\nCapacity:', font=desired_font).grid(row=6, column=1, pady=20,
                                                                                            sticky=tk.N)
tk.Label(system_data_lblfr, text='num_pages:', font=desired_font).grid(row=6, column=3, pady=20, sticky=tk.NSEW)
tk.Label(system_data_lblfr, text='Virtual memory Page Size:', font=desired_font).grid(row=7, column=1, pady=20,
                                                                                    sticky=tk.N)
tk.Label(system_data_lblfr, text='log2_page_size:', font=desired_font).grid(row=7, column=3, pady=20, sticky=tk.N)
ttk.Separator(system_data_lblfr,
              orient='horizontal',
              style='TSeparator'
              ).grid(row=8, column=1, columnspan=4, padx=25, ipadx=275)
tk.Label(system_data_lblfr, text='CPU Specifications', font=desired_font).grid(row=8, columnspan=4, column=1, pady=10, sticky=tk.N)
tk.Label(system_data_lblfr, text='Choose a CPU:', font=desired_font).grid(row=9, column=2, pady=10, sticky=tk.N)
tk.Label(system_data_lblfr, text='Branch predictor used:', font=desired_font).grid(row=11, column=1, pady=10, sticky=tk.N)
tk.Label(system_data_lblfr, text='Basic BTB sets:', font=desired_font).grid(row=12, column=1, pady=10, sticky=tk.N)
tk.Label(system_data_lblfr, text='Ways:', font=desired_font).grid(row=12, column=3, pady=10, sticky=tk.N)
tk.Label(system_data_lblfr, text='Indirect buffer size:', font=desired_font).grid(row=14, column=1, pady=10, sticky=tk.N)
tk.Label(system_data_lblfr, text='RAS size:', font=desired_font).grid(row=14, column=3, pady=10, sticky=tk.N)

# # # # # # # # # # # # # # # # # # # #
# Counter x counter graph LabelFrame #
# # # # # # # # # # # # # # # # # # #

counter_x_counter_data_lblfr = LabelFrame(right_frame, text='Counter vs. counter graph parameter selection', font=desired_font, labelanchor='n')
counter_x_counter_data_lblfr.grid(column=2, sticky="NSEW", row=1, columnspan=1)
tk.Label(counter_x_counter_data_lblfr, text='Source of the first parameter:', font=desired_font).grid(row=1, column=1, columnspan=2, sticky=tk.N, pady=10)

cpu_as_first_source_lbl = tk.Label(counter_x_counter_data_lblfr, text='Choose a CPU core:', font=desired_font)
drop_first_source = tk.OptionMenu(counter_x_counter_data_lblfr, current_cpu_first_source, *cpu_options)
total_first_source_rb = tk.Radiobutton(counter_x_counter_data_lblfr, text="Total simulation", variable=type_of_results_first_source, value=1, font=desired_font)
interest_first_source_rb = tk.Radiobutton(counter_x_counter_data_lblfr, text="Region of interest", variable=type_of_results_first_source, value=2, font=desired_font)
y_axis_lbl = tk.Label(counter_x_counter_data_lblfr, text='Choose the Y-axis parameter to plot:', font=desired_font)

type_of_results_first_lbl = tk.Label(counter_x_counter_data_lblfr, text='Type of results:', font=desired_font)
combobox_selector_first_source = ttk.Combobox(counter_x_counter_data_lblfr, values=dram_variables, font=desired_font, postcommand=update_cbox_counter_first)

results_first_source_counter = tk.IntVar()
cpu_first_source_rb = tk.Radiobutton(counter_x_counter_data_lblfr, text="CPUs", variable=results_first_source_counter,
                value=1, indicatoron=False, command=cpus_as_first_source, font=desired_font)
cpu_first_source_rb.grid(ipadx=50, row=1, column=1, sticky=S, padx=5, pady=15)
tk.Radiobutton(counter_x_counter_data_lblfr, text="DRAM", variable=results_first_source_counter,
                value=2, indicatoron=False, command=dram_as_source_counter_first, font=desired_font).grid(ipadx=50, row=1, column=2, sticky=S, padx=5, pady=15)

ttk.Separator(counter_x_counter_data_lblfr,
              orient='vertical',
              style='TSeparator'
              ).grid(row=1, column=3, rowspan=4, pady=35, ipady=100)

tk.Label(counter_x_counter_data_lblfr, text='Source of the second parameter:', font=desired_font).grid(row=1, column=4, columnspan=2, sticky=N, pady=10)
results_second_source_counter = tk.IntVar()

cpu_as_second_source_lbl = tk.Label(counter_x_counter_data_lblfr, text='Choose a CPU core:', font=desired_font)
drop_second_source = tk.OptionMenu(counter_x_counter_data_lblfr, current_cpu_second_source, *cpu_options)
total_second_source_rb = tk.Radiobutton(counter_x_counter_data_lblfr, text="Total simulation", variable=type_of_results_second_source, value=1, font=desired_font)
interest_second_source_rb = tk.Radiobutton(counter_x_counter_data_lblfr, text="Region of interest", variable=type_of_results_second_source, value=2, font=desired_font)
x_axis_lbl = tk.Label(counter_x_counter_data_lblfr, text='Choose the X-axis parameter to plot:', font=desired_font)
type_of_results_second_lbl = tk.Label(counter_x_counter_data_lblfr, text='Type of results:', font=desired_font)


combobox_selector_second_source = ttk.Combobox(counter_x_counter_data_lblfr, values=dram_variables, font=desired_font, postcommand=update_cbox_counter_second)

tk.Radiobutton(counter_x_counter_data_lblfr, text="CPUs", variable=results_second_source_counter,
                value=1, indicatoron=False, command=cpus_as_second_source, font=desired_font).grid(ipadx=50, row=1, column=4, sticky=S, padx=5, pady=15)
tk.Radiobutton(counter_x_counter_data_lblfr, text="DRAM", variable=results_second_source_counter,
                value=2, indicatoron=False, command=dram_as_source_counter_second, font=desired_font).grid(ipadx=50, row=1, column=5, sticky=S, padx=5, pady=15)

generate_counter_graph_btn = tk.Button(counter_x_counter_data_lblfr, text='Generate plot', font=button_font, width=15, command=plot_counter)
generate_counter_graph_btn.configure(state='disabled')
generate_counter_graph_btn.grid(row=1, column=6, rowspan=6, padx=30, ipadx=0, pady=10)

# # # # # # # # # # # # #
# Time graph LabelFrame #
# # # # # # # # # # # # #

time_graph_data_lblfr = LabelFrame(right_frame, text='Time graph parameter selection', font=desired_font, labelanchor='n')
time_graph_data_lblfr.grid(column=2, sticky="NSEW", row=2, columnspan=1)
tk.Label(time_graph_data_lblfr, text='Source:', font=desired_font).grid(row=1, column=2, columnspan=2, sticky=N)
ttk.Separator(time_graph_data_lblfr,
              orient='horizontal',
              style='TSeparator'
              ).grid(row=1, column=1, rowspan=6, padx=35, ipadx=100)
ttk.Separator(time_graph_data_lblfr,
              orient='horizontal',
              style='TSeparator'
              ).grid(row=1, column=5, rowspan=7, padx=35, ipadx=100)

cpu_as_time_source_lbl = tk.Label(time_graph_data_lblfr, text='Choose a CPU core:', font=desired_font)
drop_time_source = tk.OptionMenu(time_graph_data_lblfr, current_cpu_time_source, *cpu_options)
type_of_results_time_lbl = tk.Label(time_graph_data_lblfr, text='Type of results:', font=desired_font)
total_time_rb = tk.Radiobutton(time_graph_data_lblfr, text="Total simulation", variable=type_of_results_time, value=1, font=desired_font)
interest_time_rb = tk.Radiobutton(time_graph_data_lblfr, text="Region of interest", variable=type_of_results_time, value=2, font=desired_font)
choose_time_lbl = tk.Label(time_graph_data_lblfr, text='Choose a parameter to add to the time plot:', font=desired_font)
combobox_selector_time = ttk.Combobox(time_graph_data_lblfr, values=dram_variables, font=desired_font, postcommand=update_cbox_time)

results_source_time = tk.IntVar()

tk.Radiobutton(time_graph_data_lblfr, text="CPUs", variable=results_source_time,
                value=1, indicatoron=False, command=cpu_as_source_time, font=desired_font).grid(ipadx=50, row=1, column=1+1, sticky=S, padx=5,pady=20)
tk.Radiobutton(time_graph_data_lblfr, text="DRAM", variable=results_source_time,
                value=2, indicatoron=False, command=dram_as_source_time, font=desired_font).grid(ipadx=50, row=1, column=2+1, sticky=S, padx=5,pady=20)

add_to_time_graph_btn = tk.Button(time_graph_data_lblfr, text='Add to time graph', font=button_font, width=15, command=plot_time)
add_to_time_graph_btn.configure(state='disabled')
add_to_time_graph_btn.grid(row=1, column=3+1, padx=10, ipady=5, pady=20, rowspan=6)
add_to_time_graph_tip = CreateToolTip(add_to_time_graph_btn, 'You can add multiple parameters to the time plot')


# # # # # # # # # # #
# Plots LabelFrame #
# # # # # # # # # #

plots_lblfr = LabelFrame(right_frame, text='Simulation results plots', font=desired_font, labelanchor='n')
plots_lblfr.grid(column=2, sticky="NSEW", row=3, columnspan=1)

# Figures
fig_vs, ax1 = plt.subplots()
fig_time, ax2 = plt.subplots()

# Figure Canvases
if scalingFactor < 1.28:
    canvas_vs_tiny = FigureCanvasTkAgg(fig_vs, master=plots_lblfr)
    canvas_vs_tiny.get_tk_widget().config(width=scalingFactor*350*0.7, height=scalingFactor*310*0.7)

    canvas_time_tiny = FigureCanvasTkAgg(fig_time, master=plots_lblfr)
    canvas_time_tiny.get_tk_widget().config(width=scalingFactor*350*0.7, height=scalingFactor*310*0.7)
else:
    canvas_vs_tiny = FigureCanvasTkAgg(fig_vs, master=plots_lblfr)
    canvas_vs_tiny.get_tk_widget().config(width=400, height=375)

    canvas_time_tiny = FigureCanvasTkAgg(fig_time, master=plots_lblfr)
    canvas_time_tiny.get_tk_widget().config(width=400, height=375)

# Pop-up window Figures
figI, axI = plt.subplots()
figII, axII = plt.subplots()

timeUnits = tk.StringVar()
units = timeUnits.get()

if scalingFactor < 1.28:
    ax2.set_xlabel('Time ({})'.format('Multiples of execution cycles'), fontsize=7)
    ax2.set_ylabel('Value', fontsize=7)
    ax2.set_title('Parameter as a time function', fontsize=7)
    ax2.tick_params(axis='both', which='major', labelsize=7)
else:
    ax2.set_xlabel('Time ({})'.format('Multiples of execution cycles'), fontsize=8)
    ax2.set_ylabel('Value', fontsize=8)
    ax2.set_title('Parameter as a time function', fontsize=8)

view_first_btn = tk.Button(plots_lblfr, text='Open', font=button_font, width=5, command=open_counter_plot)
view_second_btn = tk.Button(plots_lblfr, text='Open', font=button_font, width=5, command=open_time_plot)

plots_separator = ttk.Separator(plots_lblfr, orient='vertical', style='TSeparator')

root.config(menu=menubar)
root.mainloop()

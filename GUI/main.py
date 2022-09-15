from tkinter import *
import matplotlib
import numpy

# Basic window configuration
root = Tk()
root.title('ChampSim - Simulation Results')
icon = PhotoImage(file='icons/4.png')
root.iconphoto(False, icon)
width, height = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (width, height))




root.mainloop()
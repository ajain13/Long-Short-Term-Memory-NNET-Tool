from Tkinter import *
import tkMessageBox
import tkFileDialog
from ScrolledText import ScrolledText
import os
import StringIO
import numpy
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfile
from Queue import Queue, Empty
from threading import Thread
import time
import sys
from itertools import islice
from subprocess import Popen, PIPE


'''browserwindow = None
text = None
cancel_id = None
#training_file = None
input_file_var = None
output_file_var=  None
optimizer_variable = None
#output_file = None'''

def define_globals():

    global browserwindow
    global text
    global cancel_id
    #training_file = None
    global input_file_var
    global output_file_var
    global optimizer_variable

    global training_percent_entry
    global n_layers_entry
    global dropout_fraction_ru_entry
    global dropout_fraction_rw_entry
    global optimizer_variable
    global layer_dimension_entry
    global learning_rate_entry
    global momentum_entry
    global check_marked
    global config_file_var

    browserwindow = None
    text = None
    cancel_id = None
    #training_file = None
    input_file_var = None
    output_file_var=  None
    optimizer_variable = None


    training_percent_entry = None
    n_layers_entry = None
    dropout_fraction_ru_entry = None
    dropout_fraction_rw_entry = None
    optimizer_variable = None
    layer_dimension_entry = None
    learning_rate_entry = None
    momentum_entry = None
    check_marked = None
    config_file_var = None


def iter_except(function, exception):
    """Works like builtin 2-argument `iter()`, but stops on `exception`."""
    try:
        while True:
            yield function()
    except exception:
        return

class DisplaySubprocessOutputDemo:
    def __init__(self, root, command_list):
        self.root = root
        self.command_list = command_list


        self.process = Popen(self.command_list, stderr=PIPE, stdout=PIPE)

        # launch thread to read the subprocess output
        #   (put the subprocess output into the queue in a background thread,
        #    get output from the queue in the GUI thread.
        #    Output chain: process.readline -> queue -> label)
        q = Queue()  # limit output buffering (may stall subprocess)
        t = Thread(target=self.reader_thread, args=[q])
        t.daemon = True # close pipe if GUI process exits
        t.start()

        #self.root.pack()
        self.update(q) # start update loop

    def reader_thread(self, q):
        """Read subprocess output and put it into the queue."""
        try:
            for line1 in iter(self.process.stderr.readline, b''):
                q.put(line1)
                #q.put(line2)
        finally:
            q.put(None)

    def update(self, q):
        """Update GUI with items from the queue."""
        for line in iter_except(q.get_nowait, Empty): # display all content
            if line is None:
                #time.sleep(5)
                #self.root.delete(1.0, END)
                #self.quit()
                return
            else:
                #self.label['text'] = line # update GUI
                self.root.insert(END, line)
                self.root.see(END)
                break # display no more than one line per 40 milliseconds
        self.root.after(40, self.update, q) # schedule next update

    def quit(self):
        self.process.kill() # exit subprocess if GUI is closed (zombie!)
        self.root.destroy()


def clear():
    global text
    text.delete(1.0, END)

def close_window():
    global browserwindow
    browserwindow.destroy()
    sys.exit()

def fetch_training_file():
    #global training_file
    global input_file_var
    file_path = askopenfilename()
    print(file_path)
    input_file_var.set(file_path)

def fetch_output_file():
    global output_file_var
    file_path = asksaveasfile()
    print(file_path.name)
    file_path.close()
    output_file_var.set(file_path.name)
    os.system("rm "+file_path.name)


def fetch_config_file():
    #global training_file
    global config_file_var
    file_path = askopenfilename()
    print(file_path)
    config_file_var.set(file_path)


def parameter_packer(frame,label,entry):
    frame.pack(side=TOP)
    label.pack(side=LEFT)
    entry.pack(side=RIGHT)

def fetch_execute(is_config):
    global training_percent_entry
    global n_layers_entry
    global dropout_fraction_ru_entry
    global dropout_fraction_rw_entry
    global optimizer_variable
    global layer_dimension_entry
    global learning_rate_entry
    global momentum_entry
    global check_marked
    global text
    global input_file_var
    global output_file_var
    global config_file_var

    print("training percent",training_percent_entry.get())
    print("n_layers :",n_layers_entry.get())
    print("drop_fraction_ru",dropout_fraction_ru_entry.get())
    print("drop_fraction_rw",dropout_fraction_rw_entry.get())
    print("optimizer",optimizer_variable.get())
    print("layer dimension", layer_dimension_entry.get().strip())
    print("learning rate", learning_rate_entry.get())
    print("momentum", momentum_entry.get())
    print("append",check_marked.get())
    print("input file",input_file_var.get())
    print("output_file",output_file_var.get())
    print("config_file",config_file_var.get())

    params = {}

    if training_percent_entry.get() !="":
        training_percent = training_percent_entry.get()
        params["-trp"] = str(training_percent)

    if n_layers_entry.get() != "":    
        n_layers = n_layers_entry.get()
        params["-nl"] = str(n_layers)
    
    if dropout_fraction_ru_entry.get() != "":
        dropout_fraction_ru = dropout_fraction_ru_entry.get()
        params["-dfu"] = dropout_fraction_ru
    
    if dropout_fraction_rw_entry.get() != "":
        dropout_fraction_rw = dropout_fraction_rw_entry.get()
        params["-dfW"] = dropout_fraction_rw

    optimizer = str(optimizer_variable.get())
    params["-opt"] = optimizer


    if learning_rate_entry.get() != "":
        learning_rate = learning_rate_entry.get()
        params["-lr"] = learning_rate

    if momentum_entry.get() != "":
        momentum = momentum_entry.get()
        params["-m"] = momentum

    append = str(check_marked.get())

    if input_file_var.get() != "":
        input_file = input_file_var.get()
        params["-i"] = input_file

    if output_file_var.get() != "": 
        output_file = output_file_var.get()
        params["-o"] = output_file

    if config_file_var.get() != "":
        config_file = config_file_var.get()
        params["-c"] = config_file


    print params

    command_list = []
    command_list.append(sys.executable)
    command_list.append("run.py")
    for i in params:
        command_list.append(i)
        command_list.append(params[i])


    if layer_dimension_entry.get() != "":
        command_list.append("-ld")
        layer_dimension = layer_dimension_entry.get().strip()
        dimension_list = layer_dimension.split(",")
        layer_dimension_string = ""
        for dim in range(len(dimension_list)):
            d = dimension_list[dim].strip()
            command_list.append(str(d))

    if append == "1":
        command_list.append("-a")

    print command_list

    if is_config == 1:
        command_list = []
        command_list.append(sys.executable)
        command_list.append("run.py")
        command_list.append("-i")
        command_list.append(input_file)
        command_list.append("-o")
        command_list.append(output_file)
        command_list.append("--config")
        command_list.append(config_file_var.get())
        if append == "1":
            command_list.append("-a")
        print command_list
        text.configure(state="normal")
        DisplaySubprocessOutputDemo(text,command_list)
    else:
        text.configure(state="normal")
        DisplaySubprocessOutputDemo(text,command_list)

    '''print("training percent :",training_percent)
    print("n_layers :",n_layers)
    print("drop_fraction_ru :",dropout_fraction_ru)
    print("drop_fraction_rw :",dropout_fraction_rw)
    print("optimizer :",optimizer)
    print("layer dimension :", layer_dimension)
    print("learning rate :", learning_rate)
    print("momentum :",momentum)
    print("append :",append)
    print("input file",input_file_var.get())
    print("output_file",output_file_var.get())
    print("config_file",config_file_var.get())'''






   # command_list = [sys.executable,"nnet/run.py","-i",input_file_var.get(),"-o",output_file_var.get()]

    



def validate_execute():
    global training_percent_entry
    global n_layers_entry
    global dropout_fraction_ru_entry
    global dropout_fraction_rw_entry
    global optimizer_variable
    global layer_dimension_entry
    global learning_rate_entry
    global momentum_entry
    global check_marked
    global text
    global input_file_var
    global output_file_var
    global config_file_var

    if config_file_var.get() != "":
        if input_file_var.get() == "":
            tkMessageBox.showerror("Missing parameters","Input training file is required")
        elif output_file_var.get() == "":
            tkMessageBox.showerror("Missing parameters","Output file is required")
        else:
            fetch_execute(1)
    else:
        if input_file_var.get() == "":
            tkMessageBox.showerror("Missing parameters","Input training file is required")
        elif output_file_var.get() == "":
            tkMessageBox.showerror("Missing parameters","Output file is required")
        elif learning_rate_entry.get() == "":
            tkMessageBox.showerror("Missing parameters","Learning rate is required")
        else:
            fetch_execute(0)


def load_gui():
    global browserwindow
    global text
    global input_file_var
    global output_file_var
    global config_file_var

    global training_percent_entry
    global n_layers_entry
    global dropout_fraction_ru_entry
    global dropout_fraction_rw_entry
    global optimizer_variable
    global layer_dimension_entry
    global learning_rate_entry
    global momentum_entry
    global check_marked

    browserwindow = Tk()
    browserwindow.wm_title("LSTM tool v0.1.1")
    browserwindow.resizable(width=True, height=True)

    #FRAMES
    parameters_frame = Frame(browserwindow,width=700,height=600)
    output_frame = Frame(browserwindow)
    parameters_frame.pack_propagate(False)
    #output_frame.pack_propagate(False)


    #Packing containing FRAMES

    parameters_frame.pack(side=LEFT)
    output_frame.pack(side=TOP)
    #output text in output_frame

    text = ScrolledText(output_frame,width=100,height=45,insertborderwidth=3,background="black",fg="lightgreen")
    text.configure(state="disabled")
    text.pack()

    utility_button_frame = Frame(output_frame)
    clear_button = Button(utility_button_frame,text="Delete Result Buffer",width="15",command=clear)

    utility_button_frame.pack(side=TOP)
    clear_button.grid(row=0)

    #parameters input frames and Packing

    heading_frame  = Frame(parameters_frame)
    heading_label = Label(heading_frame,text = "PARAMETER(S) :")
    sub_heading_label = Label(heading_frame,text = "All fields marked with (*) are required :",fg="red")


    filename_frame = Frame(parameters_frame)
    filename_label = Label(filename_frame, text = "Load input filename (*) :")
    filename_load_button = Button(filename_frame,text= "Browse",width="10",command=fetch_training_file)

    input_file_var = StringVar()
    input_file_var.set("")
    file_frame = Frame(parameters_frame)
    file_label = Label(file_frame,textvariable=input_file_var,fg="blue")

    output_filename_frame = Frame(parameters_frame)
    ouput_filename_label = Label(output_filename_frame, text = "Save output filename as (*):")
    output_filename_load_button = Button(output_filename_frame,text= "Browse",width="10",command=fetch_output_file)

    output_file_var = StringVar()
    output_file_var.set("")
    output_file_frame = Frame(parameters_frame)
    output_file_label = Label(output_file_frame,textvariable=output_file_var,fg="blue")

    sub_parameter_frame = Frame(parameters_frame)


    training_percent = DoubleVar()
    training_percent_label = Label(sub_parameter_frame, text = "Training percentage : ")
    training_percent_entry = Entry(sub_parameter_frame,width=10,textvariable=training_percent)
    training_percent.set(0.7)

    layers = IntVar()
    n_layers_label = Label(sub_parameter_frame, text = "Number of layers : ")
    n_layers_entry = Entry(sub_parameter_frame,width=10,textvariable=layers)
    layers.set(3)


    output_ru_layers = DoubleVar()
    dropout_fraction_ru_label = Label(sub_parameter_frame, text = "Fraction of R_Units to be dropped [0.0, 1.0) : ")
    dropout_fraction_ru_entry = Entry(sub_parameter_frame,width=10,textvariable=output_ru_layers)
    output_ru_layers.set(0.0)

    output_rw_layers = DoubleVar()
    dropout_fraction_rw_label = Label(sub_parameter_frame, text = "Fraction of input units to be dropped [0.0, 1.0) : ")
    dropout_fraction_rw_entry = Entry(sub_parameter_frame,width=10,textvariable=output_rw_layers)
    output_rw_layers.set(0.0)


    optimizer_label = Label(sub_parameter_frame,text = "Optimizer type :")
    OPTIMIZER_OPTIONS = ["adam","SGD","RMSprop","nadam"]
    optimizer_variable = StringVar(sub_parameter_frame)
    optimizer_variable.set(OPTIMIZER_OPTIONS[0])
    optimizer_dropdown = apply(OptionMenu,(sub_parameter_frame,optimizer_variable)+tuple(OPTIMIZER_OPTIONS))
    optimizer_dropdown.config(width=10)


    dimension = StringVar()
    layer_dimension_label = Label(sub_parameter_frame, text = "Layer dimensions [LAYERDIM1,LAYERDIM2,...] : ")
    layer_dimension_entry = Entry(sub_parameter_frame,width=10,textvariable=dimension)
    dimension.set("1,4,1")


    learning_rate_label = Label(sub_parameter_frame, text = "Learning rate (*) :")
    learning_rate_entry = Entry(sub_parameter_frame,width=10)

    momentum = DoubleVar()
    momentum_label = Label(sub_parameter_frame, text = "Momentum :")
    momentum_entry = Entry(sub_parameter_frame,width=10,textvariable=momentum)
    momentum.set(0.0)

    append_label = Label(sub_parameter_frame,text = "Append run configuration to logfile")
    check_marked = IntVar()
    append_check_button = Checkbutton(sub_parameter_frame,variable=check_marked,onvalue=1,offvalue=0)

    config_cover_frame = Frame(parameters_frame)
    config_cover_frame.configure(pady=8)


    config_filename_frame = Frame(config_cover_frame)
    config_filename_label = Label(config_filename_frame, text = "Use config file :")
    config_filename_load_button = Button(config_filename_frame,text= "Browse",width="10",command=fetch_config_file)

    config_file_var = StringVar()
    config_file_var.set("")
    config_file_frame = Frame(config_cover_frame)
    config_file_label = Label(config_file_frame,textvariable=config_file_var,fg="blue")

    buttons_frame = Frame(parameters_frame)
    run_button = Button(parameters_frame,text= "Run",width="10",command=validate_execute)

    masthead_label = Label(parameters_frame,text="Developed by Abhishek Jain, Pradyumna Kaushik and Sreedhar Kumar")




    #packing inner frames,entries and buttons

    heading_frame.pack(side=TOP)
    heading_label.pack()
    sub_heading_label.pack()

    filename_frame.pack(side=TOP)
    #filename_label.pack()
    #filename_load_button.pack()

    filename_label.grid(row=2)
    filename_load_button.grid(row=2,column=1)

    file_frame.pack(side=TOP)
    file_label.pack(side=LEFT)

    output_filename_frame.pack(side=TOP)
    #ouput_filename_label.pack()
    #output_filename_load_button.pack()
    ouput_filename_label.grid(row=3)
    output_filename_load_button.grid(row=3,column=1)

    output_file_frame.pack(side=TOP)
    output_file_label.pack(side=LEFT)



    sub_parameter_frame.pack()

    training_percent_label.grid(row=4)
    training_percent_entry.grid(row=4,column=1)

    n_layers_label.grid(row=5)
    n_layers_entry.grid(row=5,column=1)

    dropout_fraction_ru_label.grid(row=6)
    dropout_fraction_ru_entry.grid(row=6,column=1)

    dropout_fraction_rw_label.grid(row=7)
    dropout_fraction_rw_entry.grid(row=7,column=1)

    optimizer_label.grid(row=8)
    optimizer_dropdown.grid(row=8,column=1)

    layer_dimension_label.grid(row=9)
    layer_dimension_entry.grid(row=9,column=1)


    learning_rate_label.grid(row=10)
    learning_rate_entry.grid(row=10,column=1)

    momentum_label.grid(row=11)
    momentum_entry.grid(row=11,column=1)

    append_label.grid(row=12)
    append_check_button.grid(row=12,column=1)

    '''config_filename_frame.pack(side=TOP)
    config_filename_label.pack()
    config_filename_load_button.pack()

    config_file_frame.pack(side=TOP)
    config_file_label.pack(side=LEFT)'''

    config_cover_frame.pack(side=TOP)

    config_filename_frame.pack(side=TOP)
    config_filename_label.grid(row=13)
    config_filename_load_button.grid(row=13,column=1)

    config_file_frame.pack(side=TOP)
    config_file_label.pack(side=LEFT)


    buttons_frame.pack(side=TOP)
    run_button.pack()

    masthead_label.pack(side=BOTTOM)



    #Run the GUI browserwindow mainloop

    browserwindow.mainloop()









if __name__ == "__main__":
    define_globals()
    load_gui()

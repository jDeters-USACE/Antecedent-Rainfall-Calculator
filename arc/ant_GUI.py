# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

######################################
##  ------------------------------- ##
##            ant_GUI.py            ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-27   ##
##  ------------------------------- ##
######################################

"""
Graphical user interface for the Antecedent Precipitation Tool
"""

# Import Standard Libraries
import tkinter
import tkinter.ttk
import tkinter.filedialog
import os
import sys
import shutil
import subprocess
import traceback
import datetime
import time

# Import 3rd-Party Libraries
import PyPDF2
import requests

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Import Custom Libraries
try:
    from . import windowsScaling
    from . import huc_query
    from . import custom_watershed_query
    from . import check_usa
    from . import watershed_summary
    from . import help_window
    from . import get_all
    from .utilities import JLog
except Exception:
    import windowsScaling
    import huc_query
    import custom_watershed_query
    import check_usa
    import watershed_summary
    import help_window
    import get_all
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts'.format(ROOT))
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc'.format(ROOT))
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
    import JLog


def click_help_button():
    help_app = help_window.Main()
    help_app.run()

class Main(object):
    """GUI for the Antecedent Precipitation Tool"""

    def __init__(self):
        self.row = 0
        self.separators = []
        self.date_separators = []
        self.date_labels = []
        self.date_entry_boxes = []
        self.custom_watershed_fields_active = False
        # Define class attributes
        self.rain_instance = None
        self.snow_instance = None
        self.snow_depth_instance = None
        self.input_list_list_prcp = []
        self.input_list_list_snow = []
        self.input_list_list_snwd = []
        self.show = False
        self.ncdc_working = False
        # Define Local Variables
        root_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        # Create PrintLog
        self.L = JLog.PrintLog(Delete=True)
        # Announce GUI
        self.L.Wrap("Launching Graphical User Interface...")

        # Create UI Object
        self.master = tkinter.Tk()
        # Add Title
        self.master.title('Antecedent Precipitation Tool')

        # Set GUI Window Icon and Create Folder Image Object
        try:
            graph_icon_file = root_folder + '/GUI Images/Graph.ico'
            self.master.wm_iconbitmap(graph_icon_file)
            folder_icon_path = root_folder + '/GUI Images/folder.gif'
            self.folder_image = tkinter.PhotoImage(file=folder_icon_path)
            plus_icon_path = root_folder + '/GUI Images/Plus.gif'
            self.PLUS_IMAGE = tkinter.PhotoImage(file=plus_icon_path)
            minus_icon_path = root_folder + '/GUI Images/Minus.gif'
            self.minus_image = tkinter.PhotoImage(file=minus_icon_path)
            question_icon_path = root_folder + '/GUI Images/Question.gif'
            self.question_image = tkinter.PhotoImage(file=question_icon_path)
            waterfall_path = root_folder + '/GUI Images/Traverse_80%_503.gif'
            waterfall_path = root_folder + '/GUI Images/Traverse_67%_1000.gif'
            waterfall_path = root_folder + '/GUI Images/Traverse_40%_503.gif'
            self.waterfall = tkinter.PhotoImage(file=waterfall_path)
        except Exception:
            graph_icon_file = os.path.join(sys.prefix, 'images\\Graph.ico')
            self.master.wm_iconbitmap(graph_icon_file)
            folder_icon_path = os.path.join(sys.prefix, 'images\\folder.gif')
            self.folder_image = tkinter.PhotoImage(file=folder_icon_path)
            plus_icon_path = os.path.join(sys.prefix, 'images\\Plus.gif')
            self.PLUS_IMAGE = tkinter.PhotoImage(file=plus_icon_path)
            minus_icon_path = os.path.join(sys.prefix, 'images\\Minus.gif')
            self.minus_image = tkinter.PhotoImage(file=minus_icon_path)
            question_icon_path = os.path.join(sys.prefix, 'images\\Question.gif')
            self.question_image = tkinter.PhotoImage(file=question_icon_path)
            waterfall_path = os.path.join(sys.prefix, 'images\\Traverse_40%_503.gif')
            self.waterfall = tkinter.PhotoImage(file=waterfall_path)

        self.background_label = tkinter.Label(self.master, image=self.waterfall)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #---HELP BUTTON---#
        self.help_button = tkinter.ttk.Button(self.master, text='Help / More Info', image=self.question_image, command=click_help_button)
        #self.help_button = tkinter.Button(self.master, text='?', command=click_help_button, font='Helvetica 12 bold', fg="orange")
        self.help_button.grid(row=self.row, column=2, sticky='ne', columnspan=1)
        self.row += 1

        #---SEPARATOR---#
        self.line_style = tkinter.ttk.Style()
        self.line_style.configure("Line.TSeparator", background="#000000")
        separator = tkinter.ttk.Separator(self.master, orient="horizontal", style="Line.TSeparator")
        separator.grid(row=self.row, sticky='ew', columnspan=3, pady=3, padx=4)
        self.separators.append(separator)
        self.row += 1

        #---LAT, LON, SCOPE LABELS---#
        self.label_latitude = tkinter.ttk.Label(self.master, text="Latitude (DD):")
        self.label_longitude = tkinter.ttk.Label(self.master, text="Longitude (-DD):")
#        self.label_watershed_scope = tkinter.ttk.Label(self.master, text="Geographic Scope")
        self.label_watershed_scope = tkinter.ttk.Label(self.master, text="Scope")
        self.label_latitude.grid(row=self.row, column=0, sticky='ws', padx=4, pady=0)
        self.label_longitude.grid(row=self.row, column=1, sticky='ws', padx=3, pady=0)
        self.label_watershed_scope.grid(row=self.row, column=2, sticky='ws', padx=3, pady=1)
        self.row += 1

        #---LAT, LON, SCOPE ENTRIES---#
        self.ENTRY_LATITUDE = tkinter.ttk.Entry(self.master, width=15)
        self.ENTRY_LONGITUDE = tkinter.ttk.Entry(self.master, width=15)
        self.watershed_scope_string_var = tkinter.StringVar()
        self.watershed_scope_string_var.set('Single Point')
        options = ['Single Point',
                   'Single Point', # It was not showing up in the list, but did when duplicated for some reason
                   'HUC12',
                   'HUC10',
                   'HUC8',
                   'Custom Polygon']
        self.watershed_scope_menu = tkinter.ttk.OptionMenu(self.master,
                                                           self.watershed_scope_string_var,
                                                           *(options),
                                                           command=self.watershed_selection)
        self.ENTRY_LATITUDE.grid(row=self.row, column=0, padx=3, sticky='w')
        self.ENTRY_LONGITUDE.grid(row=self.row, column=1, padx=3, sticky='w')
        self.watershed_scope_menu.grid(row=self.row, column=2, sticky='w', padx=3)
        self.row += 1

        #---SEPARATOR---#
        separator = tkinter.ttk.Separator(self.master, orient="horizontal", style="Line.TSeparator")
        separator.grid(row=self.row, sticky='ew', columnspan=3, pady=3, padx=4)
        self.separators.append(separator)
        self.row += 1

        #---DATES FRAME---#
        self.dates_frame = tkinter.ttk.Frame(self.master)
        self.dates_frame.grid(row=self.row, column=0, sticky="nsew", padx=0, pady=0, columnspan=3)
        self.background_label2 = tkinter.Label(self.dates_frame, image=self.waterfall)
        self.background_label2.place(x=0, y=0, relwidth=1, relheight=1)
        self.row += 1
        self.plus_button = tkinter.ttk.Button(self.dates_frame, command=self.add_date, image=self.PLUS_IMAGE)
        self.minus_button = tkinter.ttk.Button(self.dates_frame, image=self.minus_image, command=self.minus_function)

        #---SEPARATOR---#
        separator = tkinter.ttk.Separator(self.master, orient="horizontal", style="Line.TSeparator")
        separator.grid(row=98, sticky='ew', columnspan=3, pady=0, padx=0)
        self.separators.append(separator)
        self.row += 1

        #---BOTTOM ROW BUTTONS---#
        self.BUTTON_CALCULATE = tkinter.ttk.Button(self.master, text='Calculate', command=self.calculate_and_graph)
        self.batch_style_string_var = tkinter.StringVar()
        self.batch_style_string_var.set('Switch to Date Range')
        self.BUTTON_BATCH = tkinter.ttk.Button(self.master, textvariable=self.batch_style_string_var, command=self.switch_batch_style)
        self.BUTTON_QUIT = tkinter.ttk.Button(self.master, text='Quit', command=self.quit_command)
        self.BUTTON_CALCULATE.grid(row=99, column=0, padx=5, pady=5, columnspan=2, sticky='w')
        self.BUTTON_BATCH.grid(row=99, column=1, padx=1, pady=5, sticky='w')
        self.BUTTON_QUIT.grid(row=99, column=2, padx=1, pady=5, sticky='e')

        # Create Watershed Label/Buttons
        self.LABEL_CUSTOM_WATERSHED_NAME = tkinter.ttk.Label(self.master, text='Custom Watershed Name:')
        self.ENTRY_CUSTOM_WATERSHED_NAME = tkinter.ttk.Entry(self.master)
        self.LABEL_CUSTOM_WATERSHED_FILE = tkinter.ttk.Label(self.master, text='Custom Watershed Shapefile:')
        self.ENTRY_CUSTOM_WATERSHED_FILE = tkinter.ttk.Entry(self.master)
        self.BUTTON_BROWSE_SHAPEFILE = tkinter.ttk.Button(self.master, text='Browse', command=self.ask_shapefile, image=self.folder_image)

# REVERSE COMPATABILITY ITEMS (For the non-compiled version)
        self.BUTTON_BROWSE_DIR = tkinter.ttk.Button(self.master, text='Browse', command=self.ask_directory, image=self.folder_image)
        self.ENTRY_OUTPUT_FOLDER = tkinter.ttk.Entry(self.master)
        default_save_folder = '{}\\Outputs'.format(ROOT) 
        self.ENTRY_OUTPUT_FOLDER.insert(0, default_save_folder)
        self.ENTRY_IMAGE_NAME = tkinter.ttk.Entry(self.master)
        self.ENTRY_IMAGE_SOURCE = tkinter.ttk.Entry(self.master)
        self.RADIO_VARIABLE_PARAMETER = tkinter.StringVar()
        self.RADIO_VARIABLE_PARAMETER.set('Rain')  # initialize
        self.RADIO_BUTTON_PARAMETER_RAIN = tkinter.ttk.Radiobutton(self.master, text='Rain', variable=self.RADIO_VARIABLE_PARAMETER, value='Rain')
        self.RADIO_BUTTON_PARAMETER_SNOW = tkinter.ttk.Radiobutton(self.master, text='Snow', variable=self.RADIO_VARIABLE_PARAMETER, value='Snow')
        self.RADIO_BUTTON_PARAMETER_SNOW_DEPTH = tkinter.ttk.Radiobutton(self.master, text='Snow Depth', variable=self.RADIO_VARIABLE_PARAMETER, value='Snow Depth')
        self.RADIO_VARIABLE_Y_AXIS = tkinter.StringVar()
        self.RADIO_VARIABLE_Y_AXIS.set(False)  # initialize
        self.RADIO_BUTTON_Y_AXIS_VARIABLE = tkinter.ttk.Radiobutton(self.master, text='Variable', variable=self.RADIO_VARIABLE_Y_AXIS, value=False)
        self.RADIO_BUTTON_Y_AXIS_CONSTANT = tkinter.ttk.Radiobutton(self.master, text='Constant', variable=self.RADIO_VARIABLE_Y_AXIS, value=True)
        self.RADIO_VARIABLE_FORECAST = tkinter.StringVar()
        self.RADIO_VARIABLE_FORECAST.set(False)  # initialize
        self.RADIO_BUTTON_FORECAST_INCLUDE = tkinter.ttk.Radiobutton(self.master, text='Include Forecast', variable=self.RADIO_VARIABLE_FORECAST, value=True)
        self.RADIO_BUTTON_FORECAST_EXCLUDE = tkinter.ttk.Radiobutton(self.master, text="Don't Include Forecast", variable=self.RADIO_VARIABLE_FORECAST, value=False)
        self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON = tkinter.StringVar()
        self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON.set('Show Options')
# REVERSE COMPATABILITY ITEMS (For the non-compiled version)

        # Create all elements and grid_forget then recreate starting style
        self.setup_unique_dates()
        self.setup_date_range()
        self.setup_csv_input()
        self.wipe_date_elements()
        self.setup_unique_dates()

        # Configure rows/columns
        self.master.geometry("+800+400")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        # a trick to activate the window (on Windows 7 & 10)
        self.master.deiconify()
    # End of __init__ method

    def run(self):
        """Starts the GUI's TKinter mainloop"""
        # start mainloop
        self.master.mainloop()
    # End of run method

    def switch_batch_style(self):
        current_style = self.batch_style_string_var.get()
        if current_style == 'Switch to Date Range':
            self.wipe_date_elements()
            self.setup_date_range()
            self.batch_style_string_var.set('Switch to CSV Input')
        elif current_style == 'Switch to CSV Input':
            self.wipe_date_elements()
            self.setup_csv_input()
            self.batch_style_string_var.set('Switch to Unique Dates')
        elif current_style == 'Switch to Unique Dates':
            self.wipe_date_elements()
            self.setup_unique_dates()
            self.batch_style_string_var.set('Switch to Date Range')
        # Configure rows/columns
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def setup_unique_dates(self):
        # Add Upper Label
        self.upper_label_unique = tkinter.ttk.Label(self.dates_frame, text='Run a single date or click "+" to add more')
        self.upper_label_unique.grid(row=0, column=0, columnspan=7, sticky='ew', padx=60)
        self.upper_label_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        self.upper_label_separator.grid(row=1, sticky='ew', columnspan=7, pady=3)
        # Add Format labels
        self.date_format_label = tkinter.ttk.Label(self.dates_frame, text='YYYY-MM-DD')
        self.date_format_label.grid(row=2, column=1, sticky='e')
        self.day_format_label = tkinter.ttk.Label(self.dates_frame, text='#')
        self.day_format_label.grid(row=2, column=0, sticky='w', padx=35)
        self.top_row_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        self.top_row_separator.grid(row=3, sticky='ew', columnspan=7, pady=3)
        # Add first day
        self.add_date()

    def add_date(self):
        # Calc Rows
        obs_num = len(self.date_labels)
        if obs_num == 0:
            # Calc spacing
            obs_num_str = ' YYYY-MM-DD:'
            obs_row = obs_num + 4
        else:
            obs_row = (obs_num * 2) + 4
            # Minus Button
            self.minus_button.grid_forget()
            self.minus_button.grid(row=obs_row, column=4, sticky='e', padx=1)
        obs_num_str = '{}'.format((obs_num + 1))
        sep_row = obs_row + 1
        # Label
#        date_label = tkinter.ttk.Label(self.dates_frame, text='Observation Date{}(YYYY-MM-DD):  '.format(obs_num_str))
        date_label = tkinter.ttk.Label(self.dates_frame, text='{}'.format(obs_num_str))
        date_label.grid(row=obs_row, column=0, sticky='w', padx=35)
        self.date_labels.append(date_label)
        # Entry
        date_entry = DateEntry(self.dates_frame, font=('Helvetica', 10, 'normal'), border=0)
        date_entry.grid(row=obs_row, column=1, sticky='e')
        self.date_entry_boxes.append(date_entry)
        # Plus Button
        self.plus_button.grid_forget()
        self.plus_button.grid(row=obs_row, column=5, sticky='e', padx=1)
        #---SEPARATOR---#
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=sep_row, sticky='ew', columnspan=7, pady=3)
        self.date_separators.append(date_separator)

    def minus_function(self):
        num_rows = len(self.date_entry_boxes)
        if num_rows < 2:
            print('Cannot remove the only Date Entry Box!')
            print('')
            return
        else:
            # Get elements
            date_label = self.date_labels[-1]
            date_entry = self.date_entry_boxes[-1]
            date_separator = self.date_separators[-1]
            # Forget Positions
            date_label.grid_forget()
            date_entry.grid_forget()
            date_separator.grid_forget()
            # Remove from lists
            self.date_labels.remove(date_label)
            self.date_entry_boxes.remove(date_entry)
            self.date_separators.remove(date_separator)
            # Plus Button
            obs_num = len(self.date_entry_boxes)
            if obs_num == 0:
                obs_row = obs_num + 2
            else:
                obs_row = (obs_num * 2) + 2
            sep_row = obs_row + 1
            self.plus_button.grid_forget()
            self.plus_button.grid(row=obs_row, column=5, sticky='e', padx=1)
            if obs_num > 1:
                # Minus Button
                self.minus_button.grid_forget()
                self.minus_button.grid(row=obs_row, column=4, sticky='e', padx=1)
            else:
                self.minus_button.grid_forget()

    def setup_date_range(self):
        # Upper Label
        self.upper_label_range = tkinter.ttk.Label(self.dates_frame, text='Get daily results between a Start Date and End Date')
        self.upper_label_range.grid(row=0, column=0, columnspan=3, sticky='nesw', padx=20)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)
        #---START DATE---#
        date_label = tkinter.ttk.Label(self.dates_frame, text='Start Date (YYYY-MM-DD):')
        date_label.grid(row=2, column=0, sticky='e')
        self.date_labels.append(date_label)
        date_entry = DateEntry(self.dates_frame, font=('Helvetica', 10, 'normal'), border=0)
        date_entry.grid(row=2, column=1, sticky='w')
        self.date_entry_boxes.append(date_entry)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)
        #---END DATE---#
        date_label = tkinter.ttk.Label(self.dates_frame, text='End Date (YYYY-MM-DD):')
        date_label.grid(row=4, column=0, sticky='e')
        self.date_labels.append(date_label)
        date_entry = DateEntry(self.dates_frame, font=('Helvetica', 10, 'normal'), border=0)
        date_entry.grid(row=4, column=1, sticky='w')
        self.date_entry_boxes.append(date_entry)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)

    def setup_csv_input(self):
        # Create/Grid 
        self.upper_label_csv = tkinter.ttk.Label(self.dates_frame, text='Use a CSV file to run many dates at once')
        self.upper_label_csv.grid(row=0, column=0, columnspan=5, sticky='nesw', padx=45)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)
        # Create CSV Label/Entry/Button
        self.label_csv_file_path = tkinter.ttk.Label(self.dates_frame, text='CSV File Path:')
        self.entry_csv_file_path = tkinter.ttk.Entry(self.dates_frame)
        self.button_browse_csv_file_path = tkinter.ttk.Button(self.dates_frame, text='Browse', command=self.ask_csv_file, image=self.folder_image)
        # Grid CSV Label/Entry/Button
        self.label_csv_file_path.grid(row=2, sticky='sw', padx=5, pady=3, columnspan=5)
        self.entry_csv_file_path.grid(row=3, padx=5, sticky='ew', columnspan=6)
        self.button_browse_csv_file_path.grid(row=3, column=6, padx=4, pady=1)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=4, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)

    def wipe_date_elements(self):
        # Unique Elements
        self.upper_label_unique.grid_forget()
        self.plus_button.grid_forget()
        self.minus_button.grid_forget()
        self.upper_label_separator.grid_forget()
        self.date_format_label.grid_forget()
        self.day_format_label.grid_forget()
        self.top_row_separator.grid_forget()
        # Range Elements
        self.upper_label_range.grid_forget()
        # CSV Elements
        self.upper_label_csv.grid_forget()
        self.label_csv_file_path.grid_forget()
        self.entry_csv_file_path.grid_forget()
        self.button_browse_csv_file_path.grid_forget()
        # Sweep through Date Elements and Remove (Hopefully separately helps)
        to_remove = []
        for date_label in self.date_labels:
            date_label.grid_forget()
            to_remove.append(date_label)
        for item in to_remove:
            try:
                self.date_labels.remove(item)
            except Exception:
                pass
        to_remove = []
        for date_entry in self.date_entry_boxes:
            date_entry.grid_forget()
            to_remove.append(date_entry)
        for item in to_remove:
            try:
                self.date_entry_boxes.remove(item)
            except Exception:
                pass
        to_remove = []
        for date_separator in self.date_separators:
            date_separator.grid_forget()
            to_remove.append(date_separator)
        for item in to_remove:
            try:
                self.date_separators.remove(item)
            except Exception:
                pass            

    def watershed_selection(self, event):
        """Acts on the self.watershed_scope_menu drop-down selection"""
        watershed_scale = self.watershed_scope_string_var.get()
        if watershed_scale == 'Custom Polygon':
            # Grid Custom Watershed Entry Box
            self.LABEL_CUSTOM_WATERSHED_NAME.grid(row=94, sticky='sw', padx=5, pady=3, columnspan=3)
            self.ENTRY_CUSTOM_WATERSHED_NAME.grid(row=95, padx=5, sticky='ew', columnspan=3)
            self.LABEL_CUSTOM_WATERSHED_FILE.grid(row=96, sticky='sw', padx=5, pady=3, columnspan=3)
            self.ENTRY_CUSTOM_WATERSHED_FILE.grid(row=97, padx=5, sticky='ew', columnspan=3)
            self.BUTTON_BROWSE_SHAPEFILE.grid(row=97, column=2, padx=4, pady=1, sticky='e')
        else:
            # Remove Custom Watershed Label and Entry Box
            self.LABEL_CUSTOM_WATERSHED_NAME.grid_forget()
            self.ENTRY_CUSTOM_WATERSHED_NAME.grid_forget()
            self.LABEL_CUSTOM_WATERSHED_FILE.grid_forget()
            self.ENTRY_CUSTOM_WATERSHED_FILE.grid_forget()
            self.BUTTON_BROWSE_SHAPEFILE.grid_forget()
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def send_log(self):
        """
        Drafts and email with the current error log as an attachment directed to me
        """
        self.L.send_log()
    # End of send_log method

    def quit_command(self):
        """
        Closes the program.
        """
        self.master.destroy()
    # End of quit_command method

    def ask_directory(self):
        """Returns a selected directoryname."""
        # defining options for opening a directory
        dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Select a folder within which PDFs will be exported'
        selected_directory = tkinter.filedialog.askdirectory(**dir_opt)
        self.ENTRY_OUTPUT_FOLDER.delete(0, 'end')
        self.ENTRY_OUTPUT_FOLDER.insert(10, selected_directory)
        return
    # End ask_directory method

    def ask_csv_file(self):
        """Returns a selected CSV file."""
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        batch_folder = '{}\\Batch'.format(root)
        default_template_path = '{}\\APT Batch Template.csv'.format(batch_folder)
        # Test for presence of Batch Template CSV
        template_exists = os.path.exists(default_template_path)
        if not template_exists:
            try:
                # Ensure Batch Folder Exists
                try:
                    os.makedirs(batch_folder)
                except Exception:
                    pass
                with open(default_template_path, 'w') as CSV:
                    CSV.write('Year (yyyy),Month (m or mm),Day (d or dd)\n')
            except Exception:
                pass
#        initial_folder = os.path.join(sys.prefix, 'Batch_Files')
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        batch_folder = '{}\\Batch'.format(root)
        default_template_path = '{}\\APT Batch Template.csv'.format(batch_folder)
        # define options for opening a file
        file_opt = options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('CSV file', '.csv'), ('all files', '.*')]
        options['initialdir'] = batch_folder
        options['initialfile'] = 'APT Batch Template.csv'
        options['parent'] = self.master
        options['title'] = "Locate the batch CSV file for this project"
        # get filename
        filename = tkinter.filedialog.askopenfilename(**file_opt)
        self.entry_csv_file_path.delete(0, 'end')
        self.entry_csv_file_path.insert(0, filename)
    # End askfile method

    def ask_shapefile(self):
        """Returns a selected Shapefile"""
#        initial_folder = os.path.join(sys.prefix, 'Batch_Files')
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        # define options for opening a file
        file_opt = options = {}
        options['defaultextension'] = '.shp'
        options['filetypes'] = [('Shapefile', '.shp')]
        options['initialdir'] = 'C:\\'
        options['parent'] = self.master
        options['title'] = "Locate the Custom Watershed Shapefile you want to analyze"
        # get filename
        filename = tkinter.filedialog.askopenfilename(**file_opt)
        self.ENTRY_CUSTOM_WATERSHED_FILE.delete(0, 'end')
        self.ENTRY_CUSTOM_WATERSHED_FILE.insert(10, filename)
        return
    # End askfile method

    def test_noaa_server(self):
        # Test whether https://www1.ncdc.noaa.gov/pub/data/ghcn/daily is accessible
        if self.ncdc_working is False:
            try:
                self.L.print_title("NOAA Server Status Check")
                self.L.Wrap('Server Base URL = https://www1.ncdc.noaa.gov/pub/data/ghcn/daily')
                self.L.Wrap("Testing if NOAA's Server is currently accessible...")
                test_connection = requests.get("https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt")
                if test_connection.status_code > 299:
                    self.ncdc_working = False
                else:
                    self.ncdc_working = True
                del test_connection
            except Exception:
                self.ncdc_working = False
        if self.ncdc_working is False:
            self.L.Wrap('                   ###################')
            self.L.Wrap("  NOAA's Server is ###---OFFLINE---###")
            self.L.Wrap('                   ###################')
            self.L.Wrap('  Request terminated, as weather data is currently inaccessbile.')
            self.L.Wrap('NOTE: If you continue to receive this error, please click the "Report Issue" button to submit an error report.')
            self.L.print_separator_line()
            self.L.Wrap('')
            self.L.Wrap('Click "Calculate" to retry, or click the "?" in the top right and then "Report Issue" to send an error log to the developer.')
        else:
            self.L.Wrap("  NOAA's Servers ONLINE.  Proceeding with request...")
            self.L.print_separator_line()
            self.L.Wrap('')
    # End test_noaa_server method


    def calculate_and_graph(self):
        """
        Runs the main function with currently selected values.
            -Will run as batch if batch processes have already been entered
        """
        # Test whether NOAA's servers are online and accessible
        self.test_noaa_server()
        if self.ncdc_working:
            try:
                current_style = self.batch_style_string_var.get()
                if current_style == 'Switch to Date Range': # Means it is currently on Unique
                    self.get_inputs_unique()
                elif current_style == 'Switch to CSV Input': # Means it is currently on Range
                    self.get_inputs_range()
                elif current_style == 'Switch to Unique Dates': #Means it is currently on CSV
                    self.get_inputs_csv()
            except Exception:
                self.L.Wrap(traceback.format_exc())
                raise
    # End of calculate_and_graph method


    def get_inputs_unique(self):
        latitude = self.ENTRY_LATITUDE.get()
        longitude = self.ENTRY_LONGITUDE.get()
        image_name = self.ENTRY_IMAGE_NAME.get() # DISABLED
        image_source = self.ENTRY_IMAGE_SOURCE.get() # DISABLED
        save_folder = self.ENTRY_OUTPUT_FOLDER.get() # DISABLED
        watershed_scale = self.watershed_scope_string_var.get()
        custom_watershed_name = self.ENTRY_CUSTOM_WATERSHED_NAME.get()
        custom_watershed_file = self.ENTRY_CUSTOM_WATERSHED_FILE.get()
        radio = self.RADIO_VARIABLE_PARAMETER.get() # DISABLED
        fixed_y_max = self.RADIO_VARIABLE_Y_AXIS.get() # DISABLED
        forecast_enabled = self.RADIO_VARIABLE_FORECAST.get() # DISABLED
        # Iterate through dates list
        for date_entry in self.date_entry_boxes:
            params = []
            observation_year, observation_month, observation_day = date_entry.get()
            params.append(latitude)
            params.append(longitude)
            params.append(observation_year)
            params.append(observation_month)
            params.append(observation_day)
            params.append(image_name)
            params.append(image_source)
            params.append(save_folder)
            params.append(custom_watershed_name)
            params.append(custom_watershed_file)
            params.append(watershed_scale)
            params.append(radio)
            params.append(fixed_y_max)
            params.append(forecast_enabled)
            if watershed_scale == 'Single Point':
                self.calculate_or_add_batch(True, params)
            else:
                self.calculate_or_add_batch(False, params)
        if watershed_scale == 'Single Point':
            self.calculate_or_add_batch(False, params)
    # End get_inputs_unique method

    def get_inputs_range(self):
        latitude = self.ENTRY_LATITUDE.get()
        longitude = self.ENTRY_LONGITUDE.get()
        image_name = self.ENTRY_IMAGE_NAME.get() # DISABLED
        image_source = self.ENTRY_IMAGE_SOURCE.get() # DISABLED
        save_folder = self.ENTRY_OUTPUT_FOLDER.get() # DISABLED
        watershed_scale = self.watershed_scope_string_var.get()
        custom_watershed_name = self.ENTRY_CUSTOM_WATERSHED_NAME.get()
        custom_watershed_file = self.ENTRY_CUSTOM_WATERSHED_FILE.get()
        radio = self.RADIO_VARIABLE_PARAMETER.get() # DISABLED
        fixed_y_max = self.RADIO_VARIABLE_Y_AXIS.get() # DISABLED
        forecast_enabled = self.RADIO_VARIABLE_FORECAST.get() # DISABLED
        # Get Start and End dates
        start_year, start_month, start_day = self.date_entry_boxes[0].get()
        end_year, end_month, end_day = self.date_entry_boxes[1].get()
        # Convert to Datetimes
        try:
            # Get start_datetime
            if len(str(start_day)) == 1:
                start_day = '0'+str(start_day)
            else:
                start_day = str(start_day)
            if len(str(start_month)) == 1:
                start_month = '0'+str(start_month)
            else:
                start_month = str(start_month)
            start_date = str(start_year)+'-'+start_month+'-'+start_day
            start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            # Get end_datetime
            if len(str(end_day)) == 1:
                end_day = '0'+str(end_day)
            else:
                end_day = str(end_day)
            if len(str(end_month)) == 1:
                end_month = '0'+str(end_month)
            else:
                end_month = str(end_month)
            end_date = str(end_year)+'-'+end_month+'-'+end_day
            end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except Exception as error:
            self.L.Wrap('')
            self.L.Wrap('{}!'.format(str(error).upper()))
            self.L.Wrap('')
            return
        test_datetime = start_datetime
        while test_datetime <= end_datetime:
            params = []
            # Get date values
            observation_day = test_datetime.strftime('%d')
            observation_month = test_datetime.strftime('%m')
            observation_year = test_datetime.strftime('%Y')            
            params.append(latitude)
            params.append(longitude)
            params.append(observation_year)
            params.append(observation_month)
            params.append(observation_day)
            params.append(image_name)
            params.append(image_source)
            params.append(save_folder)
            params.append(custom_watershed_name)
            params.append(custom_watershed_file)
            params.append(watershed_scale)
            params.append(radio)
            params.append(fixed_y_max)
            params.append(forecast_enabled)
            if watershed_scale == 'Single Point':
                self.calculate_or_add_batch(True, params)
            else:
                self.calculate_or_add_batch(False, params)

            self.calculate_or_add_batch(True, params)
            # Advance 1 day
            test_datetime = test_datetime + datetime.timedelta(days=1)
        # Submit final request
        if watershed_scale == 'Single Point':
            self.calculate_or_add_batch(False, params)

    def get_inputs_csv(self):
        """Reads batch inputs from CSV and runs them"""
        # Get Non-CSV inputs
        latitude = self.ENTRY_LATITUDE.get()
        longitude = self.ENTRY_LONGITUDE.get()
        image_name = self.ENTRY_IMAGE_NAME.get() # DISABLED
        image_source = self.ENTRY_IMAGE_SOURCE.get() # DISABLED
        save_folder = self.ENTRY_OUTPUT_FOLDER.get() # DISABLED
        radio = self.RADIO_VARIABLE_PARAMETER.get() # DISABLED
        fixed_y_max = self.RADIO_VARIABLE_Y_AXIS.get() # DISABLED
        forecast_enabled = self.RADIO_VARIABLE_FORECAST.get() # DISABLED
        watershed_scale = self.watershed_scope_string_var.get()
        custom_watershed_name = self.ENTRY_CUSTOM_WATERSHED_NAME.get()
        custom_watershed_file = self.ENTRY_CUSTOM_WATERSHED_FILE.get()
        # Get CSV file Path
        batch_csv_file = self.entry_csv_file_path.get()
        if batch_csv_file == '':
            self.L.Wrap('')
            self.L.Wrap('No CSV file provided!')
            self.L.Wrap('')
            return
        extension = os.path.splitext(batch_csv_file)[1].lower()
        if not extension == '.csv':
            self.L.Wrap('')
            self.L.Wrap('Selected file must be in CSV format!')
            self.L.Wrap('')
            return
        exists = os.path.exists(batch_csv_file)
        if not exists:
            self.L.Wrap('')
            self.L.Wrap('Selected CSV file does not exist!')
            self.L.Wrap('')
            return
        # Collect CSV Lines as Lists
        first_line = True
        self.L.Wrap('Reading CSV File...')
        csv_lines_list = []
        with open(batch_csv_file, 'r') as lines:
            for line in lines:
                self.L.Write('{}  '.format(line.replace('\n', '')))
                if first_line:
                    first_line = False
                else:
                    # Parse CSV Line Values
                    csv_inputs = line.replace('\n', '').split(',')
                    # Append to CSV Lines List
                    csv_lines_list.append(csv_inputs)
        for line in csv_lines_list:
            params = []
            observation_year = line[0]
            observation_month = line[1]
            observation_day = line[2]
            # Process parameters list
            params.append(latitude)
            params.append(longitude)
            params.append(observation_year)
            params.append(observation_month)
            params.append(observation_day)
            params.append(image_name)
            params.append(image_source)
            params.append(save_folder)
            params.append(custom_watershed_name)
            params.append(custom_watershed_file)
            params.append(watershed_scale)
            params.append(radio)
            params.append(fixed_y_max)
            params.append(forecast_enabled)
            if watershed_scale == 'Single Point':
                self.calculate_or_add_batch(True, params)
            else:
                self.calculate_or_add_batch(False, params)
        if watershed_scale == 'Single Point':
            self.calculate_or_add_batch(False, params)    
    # End batch_from_csv method



    def test_parameters(self,
                        latitude,
                        longitude,
                        observation_year,
                        observation_month,
                        observation_day,
                        image_name,
                        image_source,
                        save_folder,
                        custom_watershed_name,
                        custom_watershed_file,
                        fixed_y_max,
                        forecast_enabled):
        """Test whether or not all parameters are valid"""
        parameters_valid = True
        try:
            float(latitude)
        except Exception:
            self.L.Wrap('Latitude must be in decimal degree format!')
            parameters_valid = False
        try:
            float(longitude)
        except Exception:
            self.L.Wrap('Longitude must be in decimal degree format!')
            parameters_valid = False
        # Ensure location is within USA boundary
        in_usa = check_usa.main(latitude, longitude)
        if not in_usa:
            self.L.Wrap('Coordinates must be within the United States!')
            parameters_valid = False
        try:
            observation_year = int(observation_year)
            if observation_year < 1900:
                if str(observation_year) != '50' and str(observation_year) != '30':
                    self.L.Wrap('Year must be greater than 1900!')
                    parameters_valid = False
        except Exception:
            self.L.Wrap('Year must be a number!')
            parameters_valid = False
        try:
            observation_month = int(observation_month)
            if observation_month > 12:
                self.L.Wrap('Month cannot exceed 12!')
                parameters_valid = False
            if observation_month < 1:
                self.L.Wrap('Month cannot be less than 1!')
                parameters_valid = False
        except Exception:
            self.L.Wrap('Month must be a number!')
            parameters_valid = False
        try:
            observation_day = int(observation_day)
            if observation_day > 31:
                self.L.Wrap('Day cannot exceed 31')
                parameters_valid = False
            if observation_day < 1:
                self.L.Wrap('Day cannot be less than 1!')
        except Exception:
            self.L.Wrap('Day must be a number!')
            parameters_valid = False
        # Discern Watershed Scale
        watershed_scale = self.watershed_scope_string_var.get()
        # Test if shapefile exists
        if custom_watershed_file != '':
            watershed_file_exists = os.path.exists(custom_watershed_file)
            if not watershed_file_exists:
                self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE NOT FOUND!')
                parameters_valid = False
            watershed_extension = os.path.splitext(custom_watershed_file)[1]
            if watershed_extension.lower() == '.shp':
                prj_file = custom_watershed_file[:-4] + '.prj'
                prj_exists = os.path.exists(prj_file)
                if not prj_exists:
                    self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE LACKS REQUIRED PROJECTION (.prj) FILE!')
                    parameters_valid = False
            if custom_watershed_name == '':
                custom_watershed_name = os.path.splitext(os.path.split(custom_watershed_file)[1])[0]
        else:
            custom_watershed_file = None
            if watershed_scale == 'Custom Polygon':
                self.L.Wrap('"CUSTOM POLYGON" SELECTED BY NOT PROVIDED!')
                parameters_valid = False
        # Test for actual date
        if parameters_valid:
            try:
                # RECTIFY INPUTS
                if len(str(observation_day)) == 1:
                    observation_day = '0'+str(observation_day)
                else:
                    observation_day = str(observation_day)
                if len(str(observation_month)) == 1:
                    observation_month = '0'+str(observation_month)
                else:
                    observation_month = str(observation_month)
                observation_date = str(observation_year)+'-'+observation_month+'-'+observation_day
                observation_datetime = datetime.datetime.strptime(observation_date, '%Y-%m-%d')
            except Exception as error:
                self.L.Wrap('')
                self.L.Wrap('{}!'.format(str(error).upper()))
                parameters_valid = False
        if parameters_valid:
            # Ensure date is no later than 2 days prior to current date
            two_days_prior_datetime = datetime.datetime.today()- datetime.timedelta(days=2)
            if observation_datetime > two_days_prior_datetime:
                observation_date = two_days_prior_datetime.strftime('%Y-%m-%d')
                self.L.Wrap('Date cannot exceed two days ago due to data availability')
                self.L.Wrap('  Observation date updated to: {}'.format(observation_date))
                observation_day = two_days_prior_datetime.strftime('%d')
                observation_month = two_days_prior_datetime.strftime('%m')
                observation_year = int(two_days_prior_datetime.strftime('%Y'))
                observation_datetime = two_days_prior_datetime
        return parameters_valid




    def calculate_or_add_batch(self, batch, params):
        """
        If batch is False
        --Executes main business logic of the Antecedent Precipitation Tool
        If batch is True
        --Adds current field values to batch list
        """
        start_time = time.clock()
        # Get Paramaters
        latitude = params[0]
        longitude = params[1]
        observation_year = params[2]
        observation_month = params[3]
        observation_day = params[4]
        image_name = params[5]
        image_source = params[6]
        save_folder = params[7]
        custom_watershed_name = params[8]
        custom_watershed_file = params[9]
        watershed_scale = params[10]
        radio = params[11]
        fixed_y_max = params[12]
        forecast_enabled = params[13]
        # Test for all fields empty
        if batch is True:
            empty = True
            fields = [latitude,
                      longitude,
                      observation_year,
                      observation_month,
                      observation_day,
                      image_name,
                      image_source,
                      custom_watershed_file]
            for field in fields:
                if not field == '':
                    empty = False
            if empty is True:
                self.batch_from_csv()
                return
        # Remove Spaces and Line Breaks from numeric fields (They were showing up when copying from Excel for some reason)
        latitude = latitude.replace(' ', '').replace('\n', '')
        longitude = longitude.replace(' ', '').replace('\n', '')
        observation_year = observation_year.replace(' ', '').replace('\n', '')
        observation_month = observation_month.replace(' ', '').replace('\n', '')
        observation_day = observation_day.replace(' ', '').replace('\n', '')
        # Test whether or not all parameters are valid
        parameters_valid = True
        try:
            float(latitude)
        except Exception:
            self.L.Wrap('Latitude must be in decimal degree format!')
            parameters_valid = False
        try:
            float(longitude)
        except Exception:
            self.L.Wrap('Longitude must be in decimal degree format!')
            parameters_valid = False
        # Ensure location is within USA boundary
        in_usa = check_usa.main(latitude, longitude)
        if not in_usa:
            self.L.Wrap('Coordinates must be within the United States!')
            parameters_valid = False
        try:
            observation_year = int(observation_year)
            if observation_year < 1900:
                if str(observation_year) != '50' and str(observation_year) != '30':
                    self.L.Wrap('Year must be greater than 1900!')
                    parameters_valid = False
        except Exception:
            self.L.Wrap('Year must be a number!')
            parameters_valid = False
        try:
            observation_month = int(observation_month)
            if observation_month > 12:
                self.L.Wrap('Month cannot exceed 12!')
                parameters_valid = False
            if observation_month < 1:
                self.L.Wrap('Month cannot be less than 1!')
                parameters_valid = False
        except Exception:
            self.L.Wrap('Month must be a number!')
            parameters_valid = False
        try:
            observation_day = int(observation_day)
            if observation_day > 31:
                self.L.Wrap('Day cannot exceed 31')
                parameters_valid = False
            if observation_day < 1:
                self.L.Wrap('Day cannot be less than 1!')
        except Exception:
            self.L.Wrap('Day must be a number!')
            parameters_valid = False
        # Test if shapefile exists
        if custom_watershed_file != '':
            watershed_file_exists = os.path.exists(custom_watershed_file)
            if not watershed_file_exists:
                self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE NOT FOUND!')
                parameters_valid = False
            watershed_extension = os.path.splitext(custom_watershed_file)[1]
            if watershed_extension.lower() == '.shp':
                prj_file = custom_watershed_file[:-4] + '.prj'
                prj_exists = os.path.exists(prj_file)
                if not prj_exists:
                    self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE LACKS REQUIRED PROJECTION (.prj) FILE!')
                    parameters_valid = False
            if custom_watershed_name == '':
                custom_watershed_name = os.path.splitext(os.path.split(custom_watershed_file)[1])[0]
        else:
            custom_watershed_file = None
            if watershed_scale == 'Custom Polygon':
                self.L.Wrap('"CUSTOM POLYGON" SELECTED BY NOT PROVIDED!')
                parameters_valid = False
        # Test for actual date
        if parameters_valid:
            try:
                # RECTIFY INPUTS
                if len(str(observation_day)) == 1:
                    observation_day = '0'+str(observation_day)
                else:
                    observation_day = str(observation_day)
                if len(str(observation_month)) == 1:
                    observation_month = '0'+str(observation_month)
                else:
                    observation_month = str(observation_month)
                observation_date = str(observation_year)+'-'+observation_month+'-'+observation_day
                observation_datetime = datetime.datetime.strptime(observation_date, '%Y-%m-%d')
            except Exception as error:
                self.L.Wrap('')
                self.L.Wrap('{}!'.format(str(error).upper()))
                parameters_valid = False
        # Ensure date is no later than 2 days prior to current date
        if parameters_valid:
            two_days_prior_datetime = datetime.datetime.today()- datetime.timedelta(days=2)
            if observation_datetime > two_days_prior_datetime:
                observation_date = two_days_prior_datetime.strftime('%Y-%m-%d')
                self.L.Wrap('Date cannot exceed two days ago due to data availability')
                self.L.Wrap('  Observation date updated to: {}'.format(observation_date))
                observation_day = two_days_prior_datetime.strftime('%d')
                observation_month = two_days_prior_datetime.strftime('%m')
                observation_year = int(two_days_prior_datetime.strftime('%Y'))
                observation_datetime = two_days_prior_datetime
        # Terminate function of parameters invalid
        if not parameters_valid:
            return
        if image_name == '':
            image_name = None
        if image_source == '':
            image_source = None
        if save_folder == "":
            save_folder = None
        if fixed_y_max == "1":
            fixed_y_max = True
        if forecast_enabled == "1":
            forecast_enabled = True
        # Import anteProcess
        try:
            from . import anteProcess
        except Exception:
            import anteProcess
        # Set data_variable specific variables
        if radio == 'Rain':
            if self.rain_instance is None:
                self.L.Wrap("Creating Rain anteProcess.Main() instance...")
                self.rain_instance = anteProcess.Main()
            input_list_list = self.input_list_list_prcp
            ante_instance = self.rain_instance
            data_variable = 'PRCP'
        elif radio == 'Snow':
            if self.snow_instance is None:
                self.L.Wrap("Creating Snow anteProcess.Main() instance...")
                self.snow_instance = anteProcess.Main()
            input_list_list = self.input_list_list_snow
            ante_instance = self.snow_instance
            data_variable = 'SNOW'
        elif radio == 'Snow Depth':
            if self.snow_depth_instance is None:
                self.L.Wrap("Creating Snow Depth anteProcess.Main() instance...")
                self.snow_depth_instance = anteProcess.Main()
            input_list_list = self.input_list_list_snwd
            ante_instance = self.snow_depth_instance
            data_variable = 'SNWD'
        # Create Batch or Execute Function
        input_list = [data_variable,
                      latitude,
                      longitude,
                      observation_year,
                      observation_month,
                      observation_day,
                      image_name,
                      image_source]
        test = input_list in input_list_list
        if test is False:
            if batch is True or input_list_list:
                input_list_list.append(input_list)
                self.L.Wrap(radio+' Batch '+str(len(input_list_list))+' - '+str(input_list))
        else:
            if batch is True:
                self.L.Wrap('The selected inputs have already been added to the batch list.')
            self.L.Wrap("")
        if batch is False:
#-WATERSHED START
            if radio == 'Rain':
##### DEV NOTE ######
                    # NEED TO IMPLEMENT CUSTOM WATERSHED DIGESTION / SAMPLING
##### DEV NOTE ######
                # WATERSHED PROCESSING SECTION
                if watershed_scale != 'Single Point':
                    # Announce Watershed Processing
                    self.L.print_title('WATERSHED IDENTIFICATION AND RANDOM SAMPLING')
                    # Clear the Batch Queue (If necessary) [We currently don't support batch watershed runs]
                    if len(input_list_list) > 1:
                        # Let user know the batch processes are being cleared
                        self.L.Wrap('Manual batch processing lists are not supported for Watershed Scales other than "Single Point"')
                        self.L.Wrap('  Clearing Batch Process Queue to prepare for Watershed Random Sampling Points...')
                        input_list_list = []
                    self.L.Wrap('Selected Watershed Scale: {}'.format(watershed_scale))
                    self.L.Wrap('Identifying and sampling watershed...')
                    if watershed_scale != 'Custom Polygon':
                        # Get HUC & Random Sampling Points
                        huc, sampling_points, huc_square_miles = huc_query.id_and_sample(lat=latitude,
                                                                                         lon=longitude,
                                                                                         watershed_scale=watershed_scale)
                    else:
                        # Get Random Sampling points and square miles
                        sampling_points, huc_square_miles = custom_watershed_query.shapefile_sample(lat=latitude,
                                                                                                    lon=longitude,
                                                                                                    shapefile=custom_watershed_file)
                    # Add each sampling point to batch process
                    self.L.print_section('Batch Process Queueing')
                    self.L.Wrap('Adding Random Sampling Points for the watershed to the Batch Process Queue...')
                    if watershed_scale != 'Custom Polygon':
                        self.L.Wrap('{} ({}) - Watershed Sampling Points:'.format(watershed_scale, huc))
                    else:
                        self.L.Wrap('{} ({}) - Watershed Sampling Points:'.format(watershed_scale, custom_watershed_name))
                    for sampling_point in sampling_points:
                        # Create input list for sampling point
                        input_list = [data_variable,
                                      sampling_point[0],
                                      sampling_point[1],
                                      observation_year,
                                      observation_month,
                                      observation_day,
                                      image_name,
                                      image_source]
                        # Add sampling point to input_list_list
                        input_list_list.append(input_list)
                        # Announce the addition of this sampling point
                        self.L.Wrap(' Sampling Point {} - {}'.format(str(len(input_list_list)),
                                                                     str(input_list)))
                    self.L.print_separator_line()
#-WATERSHED END
            ### - INDIVIDUAL PROCESS OR BATCH ITERATION - ###
            current_input_list_list = list(input_list_list)
            if not current_input_list_list:
                self.L.print_title("SINGLE POINT ANALYSIS")
                run_list = input_list + [save_folder, forecast_enabled]
                self.L.Wrap('Running: '+str(run_list))
                result_pdf, run_y_max, condition, ante_score, wet_dry_season, palmer_value, palmer_class = ante_instance.setInputs(run_list, watershed_analysis=False, all_sampling_coordinates=None)
                if result_pdf is not None:
                    # Open PDF in new process
                    self.L.Wrap('Opening PDF in a new process...')
                    subprocess.Popen(result_pdf, shell=True)
                del run_list
            else:
#                if watershed_scale != "Single Point":
#                    self.L.print_title("BATCH ANALYSIS ({} WATERSHED)".format(watershed_scale))
#                else:
#                    self.L.print_title("BATCH ANALYSIS (MANUAL CONFIGURATION)")
                pdf_list = []
                highest_y_max = 0
                # Ensure batches are saved to a folder (Force Desktop if empty)
                if save_folder is None:
                    save_folder = '{}\\Outputs'.format(ROOT)
                    self.L.Wrap('Setting Output Folder to default location: {}...'.format(save_folder))
                # Test for common naming
                img_event_name = current_input_list_list[0][6]
                for specific_input_list in current_input_list_list:
                    if img_event_name != specific_input_list[6]:
                        img_event_name = ''
                        break
                if img_event_name != '':
                    img_event_name = '{} '.format(img_event_name)
                # Calculate output_folder
                if radio == 'Rain':
                    if watershed_scale == 'Single Point':
                        watershed_analysis = False
                        output_folder = '{}\\Antecedent\\Rainfall\\{}, {}'.format(save_folder, input_list[1], input_list[2])
                        # Define PDF Outputs
                        final_path_variable = '{}\\({}, {}) Batch Result.pdf'.format(output_folder,
                                                                                     latitude,
                                                                                     longitude)
                        final_path_fixed = '{}\\({}, {}) Batch Result - Fixed.pdf'.format(output_folder,
                                                                                          latitude,
                                                                                          longitude)
                        # Define CSV Output
                        csv_path = '{}\\({}, {}) Batch Result.csv'.format(output_folder,
                                                                          latitude,
                                                                          longitude)
                    elif watershed_scale == 'Custom Polygon':
                        watershed_analysis = True
                        output_folder = '{}\\Antecedent\\Rainfall\\~Watershed\\{}\\{}'.format(save_folder, watershed_scale, custom_watershed_name)
                        watershed_analysis = True
                        # Define PDF Outputs
                        final_path_variable = '{}\\{} - {} - Batch Result.pdf'.format(output_folder,
                                                                                          observation_date,
                                                                                          custom_watershed_name)
                        watershed_summary_path = '{}\\{} - {} - Summary Page.pdf'.format(output_folder,
                                                                                             observation_date,
                                                                                             custom_watershed_name)
                        final_path_fixed = '{}\\{} - {} - Batch Result - Fixed Scale.pdf'.format(output_folder,
                                                                                                     observation_date,
                                                                                                     custom_watershed_name)
                        # Define CSV Output
                        csv_path = '{}\\{} - {} - Batch Result.csv'.format(output_folder,
                                                                               observation_date,
                                                                               custom_watershed_name)
                    else:
                        output_folder = '{}\\Antecedent\\Rainfall\\~Watershed\\{}\\{}'.format(save_folder, watershed_scale, huc)
                        watershed_analysis = True
                        # Define PDF Outputs
                        final_path_variable = '{}\\{} - HUC {} - Batch Result.pdf'.format(output_folder,
                                                                                          observation_date,
                                                                                          huc)
                        watershed_summary_path = '{}\\{} - HUC {} - Summary Page.pdf'.format(output_folder,
                                                                                             observation_date,
                                                                                             huc)
                        final_path_fixed = '{}\\{} - HUC {} - Batch Result - Fixed Scale.pdf'.format(output_folder,
                                                                                                     observation_date,
                                                                                                     huc)
                        # Define CSV Output
                        csv_path = '{}\\{} - HUC {} - Batch Result.csv'.format(output_folder,
                                                                               observation_date,
                                                                               huc)
                elif radio == 'Snow':
                    watershed_analysis = False
                    output_folder = '{}\\Antecedent\\Snowfall\\{}, {}'.format(save_folder, input_list[1], input_list[2])
                    # Define PDF Outputs
                    final_path_variable = '{}\\({}, {}) Batch Result.pdf'.format(output_folder,
                                                                                 latitude,
                                                                                 longitude)
                    final_path_fixed = '{}\\({}, {}) Batch Result - Fixed.pdf'.format(output_folder,
                                                                                      latitude,
                                                                                      longitude)
                    # Define CSV Output
                    csv_path = '{}\\({}, {}) Batch Result.csv'.format(output_folder,
                                                                      latitude,
                                                                      longitude)
                elif radio == 'Snow Depth':
                    watershed_analysis = False
                    output_folder = '{}\\Antecedent\\Snow Depth\\{}, {}'.format(save_folder, input_list[1], input_list[2])
                    # Define PDF Outputs
                    final_path_variable = '{}\\({}, {}) Batch Result.pdf'.format(output_folder,
                                                                                 latitude,
                                                                                 longitude)
                    final_path_fixed = '{}\\({}, {}) Batch Result - Fixed.pdf'.format(output_folder,
                                                                                      latitude,
                                                                                      longitude)
                    # Define CSV Output
                    csv_path = '{}\\({}, {}) Batch Result.csv'.format(output_folder,
                                                                      latitude,
                                                                      longitude)
                # Add save_folder and Forecast setting to input lists
                for count, specific_input_list in enumerate(current_input_list_list):
                    current_input_list_list[count] = specific_input_list + [save_folder, forecast_enabled]


                # Create csv_writer
                csv_writer = JLog.PrintLog(Delete=True,
                                           Log=csv_path,
                                           Indent=0,
                                           Width=400,
                                           LogOnly=True)
                # Write first line of CSV
                if watershed_scale == 'Single Point':
                    csv_writer.Wrap('Latitude,Longitude,Date,Image Name,Image Source,PDSI Value,PDSI Class,Season,ARC Score,Antecedent Precip Condition')
                else:
                    csv_writer.Wrap('Latitude,Longitude,Date,PDSI Value,PDSI Class,Season,ARC Score,Antecedent Precip Condition')
                # Create watershed_summary results_list
                watershed_results_list = []
                # Set PDF Counter and Part Counter to 0
                pdf_count = 0
                part_count = 0
                parts_2_delete = []
                total_pdfs = len(current_input_list_list)
                run_count = 0
                for current_input_list in current_input_list_list:
                    run_count += 1
                    if watershed_scale == 'Single Point':
                        sampling_points = None
                        self.L.print_title("Single Point Batch Analysis - Date {} of {}".format(run_count, total_pdfs))
                    else:
                        self.L.print_title("{} WATERSHED ANALYSIS - SAMPLING POINT {} of {}".format(watershed_scale, run_count, total_pdfs))
                    self.L.Wrap('')
                    self.L.Wrap('Running: '+str(current_input_list))
                    self.L.Wrap('')
                    result_pdf, run_y_max, condition, ante_score, wet_dry_season, palmer_value, palmer_class = ante_instance.setInputs(current_input_list, watershed_analysis=watershed_analysis, all_sampling_coordinates=sampling_points)
                    if run_y_max > highest_y_max:
                        highest_y_max = run_y_max
                    if result_pdf is not None:
                        if total_pdfs > 1:
                            pdf_list.append(result_pdf)
                            # CHECK TO SEE IF INCREMENTAL MERGING IS NECESSARY
                            pdf_count += 1
                            if len(pdf_list) > 365:
                                if (total_pdfs - pdf_count) > 25:
                                    part_count += 1
                                    # Merging current PDFs to avoid crash when too many PDFs are merged at once
                                    self.L.Wrap('')
                                    self.L.Wrap('Merging PDFs to temp file to avoid crash at the end from merging too many files at once...')
                                    self.L.Wrap('')
                                    # Determine available temp file name
                                    final_path_variable_part = '{} - Part {}.pdf'.format(final_path_variable[:-4],
                                                                                         part_count)
                                    # Merge current PDFs
                                    merger = PyPDF2.PdfFileMerger()
                                    for doc in pdf_list:
                                        merger.append(PyPDF2.PdfFileReader(doc), "rb")
                                    merger.write(final_path_variable_part)
                                    # Clear pdf_list
                                    pdf_list = []
                                    # Add Merged PDF to the newly cleared PDF list
                                    pdf_list.append(final_path_variable_part)
                                    del merger
                                    # Remember to delete these partial files later
                                    parts_2_delete.append(final_path_variable_part)
                            # Create all_items list for CSV writing
                            all_items = current_input_list + [palmer_value, palmer_class, wet_dry_season, condition, ante_score]
                            if watershed_scale == 'Single Point':
                                # Write results to CSV
                                csv_writer.Wrap('{},{},{}-{}-{},{},{},{},{},{} Season,{},{}'.format(current_input_list[1], # Latitude
                                                                                                    current_input_list[2], # Longitude
                                                                                                    all_items[3], # Observation Year
                                                                                                    all_items[4], # Observation Month
                                                                                                    all_items[5], # Observation Day
                                                                                                    all_items[6], # Image Name
                                                                                                    all_items[7], # Image Source
                                                                                                    all_items[10], # PDSI Value
                                                                                                    all_items[11], # PDSI Class
                                                                                                    all_items[12], # Season
                                                                                                    all_items[14], # ARC Score
                                                                                                    all_items[13])) # Antecedent Precip Condition
                            else:
                                watershed_results_list.append((ante_score, condition, wet_dry_season, palmer_class))
                                csv_writer.Wrap('{},{},{}-{}-{},{},{},{} Season,{},{}'.format(current_input_list[1], # Latitude
                                                                                              current_input_list[2], # Longitude
                                                                                              all_items[3], # Observation Year
                                                                                              all_items[4], # Observation Month
                                                                                              all_items[5], # Observation Day
                                                                                              all_items[10], # PDSI Value
                                                                                              all_items[11], # PDSI Class
                                                                                              all_items[12], # Season
                                                                                              all_items[14], # ARC Score
                                                                                              all_items[13])) # Antecedent Precip Condition
                        else:
                            # Open PDF in new process
                            self.L.Wrap('Opening PDF in a new process...')
                            subprocess.Popen(result_pdf, shell=True)
                if watershed_scale != 'Single Point':
                    if watershed_scale == 'Custom Polygon':
                        huc = custom_watershed_name
                    generated = watershed_summary.create_summary(site_lat=latitude,
                                                                 site_long=longitude,
                                                                 observation_date=observation_date,
                                                                 geographic_scope=watershed_scale,
                                                                 huc=huc,
                                                                 huc_size=huc_square_miles,
                                                                 results_list=watershed_results_list,
                                                                 watershed_summary_path=watershed_summary_path)
                    if generated:
                        pdf_list = [watershed_summary_path] + pdf_list
                        parts_2_delete.append(watershed_summary_path)
                if pdf_list: # Testing list for content
                    merger = PyPDF2.PdfFileMerger()
                    for doc in pdf_list:
                        merger.append(PyPDF2.PdfFileReader(doc), "rb")
                    merger.write(final_path_variable)
                    # Open Excel Results
                    self.L.Wrap('Opening Batch Results CSV in new process...')
                    subprocess.Popen(csv_path, shell=True)
                    # Open finalPDF
                    self.L.Wrap('Opening finalPDF in new process...')
                    subprocess.Popen(final_path_variable, shell=True)
                    # Open folder containing outputs
                    subprocess.Popen('explorer "{}"'.format(output_folder))
                    del merger
                    if fixed_y_max is True:
                        # Re-run batch with fixed yMax value
                        ante_instance.set_yMax(highest_y_max)
                        # Set PDF Counter and Part Counter to 0
                        pdf_count = 0
                        part_count = 0
                        # Clear pdf_list
                        pdf_list = []
                        for current_input_list in current_input_list_list:
                            self.L.Wrap('')
                            self.L.Wrap('Re-running with fixed yMax value: '+str(current_input_list))
                            self.L.Wrap('')
                            result_pdf, run_y_max, condition, ante_score, wet_dry_season, palmer_value, palmer_class = ante_instance.setInputs(current_input_list, watershed_analysis=False, all_sampling_coordinates=None)
                            pdf_list.append(result_pdf)
                            # CHECK TO SEE IF INCREMENTAL MERGING IS NECESSARY
                            pdf_count += 1
                            if len(pdf_list) > 365:
                                if (total_pdfs - pdf_count) > 25:
                                    part_count += 1
                                    # Merging current PDFs to avoid crash when too many PDFs are merged at once
                                    self.L.Wrap('')
                                    self.L.Wrap('Merging PDFs to temp file to avoid crash at the end from merging too many files at once...')
                                    self.L.Wrap('')
                                    # Determine available temp file name
                                    final_path_fixed_part = '{} - Part {}.pdf'.format(final_path_fixed[:-4],
                                                                                      part_count)
                                    # Merge current PDFs
                                    merger = PyPDF2.PdfFileMerger()
                                    for doc in pdf_list:
                                        merger.append(PyPDF2.PdfFileReader(doc), "rb")
                                    merger.write(final_path_fixed_part)
                                    # Clear pdf_list
                                    pdf_list = []
                                    # Add temp file to pdf_list
                                    pdf_list.append(final_path_fixed_part)
                                    del merger
                                    # Remember to delete these partial files later
                                    parts_2_delete.append(final_path_fixed_part)
                        ante_instance.set_yMax(None)
                        if pdf_list:
                            merger = PyPDF2.PdfFileMerger()
                            for doc in pdf_list:
                                merger.append(PyPDF2.PdfFileReader(doc), "rb")
                            merger.write(final_path_fixed)
                            # Open finalPDF
                            self.L.Wrap('Opening finalPDF in new process...')
                            subprocess.Popen(final_path_fixed, shell=True)
                            del merger
                    # Attempt to delete partial files
                    self.L.Wrap('Attempting to delete temporary files...')
                    if parts_2_delete:
                        for part in parts_2_delete:
                            try:
                                os.remove(part)
                            except Exception:
                                pass
                if radio == 'Rain':
                    self.input_list_list_prcp = []
                elif radio == 'Snow':
                    self.input_list_list_snow = []
                elif radio == 'Snow Depth':
                    self.input_list_list_snwd = []
            self.L.Wrap('')
            self.L.Time(StartTime=start_time,
                        Task="All tasks")
            self.L.Wrap('')
            self.L.Wrap('Ready for new input.')
    # End calculate_or_add_batch function


class DateEntry(tkinter.ttk.Frame):
    """Date entry box"""
    def __init__(self, master, frame_look={}, **look):
        args = dict(relief=tkinter.SUNKEN, border=1)
        args.update(frame_look)
        tkinter.Frame.__init__(self, master, **args)

        args.update(look)
    
        #---SEPARATOR STYLE---#
        self.line_style = tkinter.ttk.Style()
        self.line_style.configure("Line.TSeparator", background="#000000")

        self.entry_year = tkinter.ttk.Entry(self, width=4)
#        self.label_yr_mo = tkinter.ttk.Label(self, text='-')
        self.label_yr_mo = tkinter.ttk.Separator(self, orient="horizontal", style="Line.TSeparator")
        self.entry_month = tkinter.ttk.Entry(self, width=2)
#        self.label_mo_dd = tkinter.ttk.Label(self, text='-')
        self.label_mo_dd = tkinter.ttk.Separator(self, orient="horizontal", style="Line.TSeparator")
        self.entry_day = tkinter.ttk.Entry(self, width=2)

        self.entry_year.grid(row=0, column=0, sticky='w')
        self.label_yr_mo.grid(row=0, column=1, sticky='ew', padx=2)
        self.entry_month.grid(row=0, column=2, sticky='w')
        self.label_mo_dd.grid(row=0, column=3, sticky='ew', padx=2)
        self.entry_day.grid(row=0, column=4, sticky='w')

        self.entry_year.bind('<KeyRelease>', self._entry_year_check)
        self.entry_month.bind('<KeyRelease>', self._entry_month_check)
        self.entry_day.bind('<KeyRelease>', self.entry_day_check)

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, 'end')
        entry.insert(0, cont[:-1])

    def _entry_year_check(self, e):
        cont = self.entry_year.get()
        if len(cont) == 0:
            return
        if len(cont) >= 4:
            self.entry_month.focus()
        if len(cont) > 4 or not cont[-1].isdigit():
            self._backspace(self.entry_year)
            self.entry_year.focus()

    def _entry_month_check(self, e):
        cont = self.entry_month.get()
        if len(cont) == 0:
            return
        if len(cont) >= 2:
            self.entry_day.focus()
        if len(cont) > 2 or not cont[-1].isdigit():
            self._backspace(self.entry_month)
            self.entry_month.focus()

    def entry_day_check(self, e):
        cont = self.entry_day.get()
        if len(cont) == 0:
            return
        if len(cont) > 2 or not cont[-1].isdigit():
            self._backspace(self.entry_day)

    def get(self):
        return self.entry_year.get(), self.entry_month.get(), self.entry_day.get() 
    
    def set(self, year, month, day):
        self.entry_year.delete(0, 'end')
        self.entry_year.insert(0, year)
        self.entry_month.delete(0, 'end')
        self.entry_month.insert(0, month)
        self.entry_day.delete(0, 'end')
        self.entry_day.insert(0, day)


if __name__ == '__main__':
    APP = Main()
    APP.run()

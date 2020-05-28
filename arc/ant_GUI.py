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
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-27   ##
##  ------------------------------- ##
######################################

"""
Graphical user interface for the Antecedent Rainfall Calculator
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
import winshell
import PyPDF2
import requests

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Import Custom Libraries
try:
    from . import potentialTitles
    from . import windowsScaling
    from . import huc_query
    from . import custom_watershed_query
    from . import check_usa
    from . import watershed_summary
    from .utilities import JLog
    CHECK_FOR_UPDATES = False
except Exception:
    import potentialTitles
    import windowsScaling
    import huc_query
    import custom_watershed_query
    import check_usa
    import watershed_summary
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts'.format(ROOT))
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
        sys.path.append('{}\\Python Scripts\\get_arc\\arc_installer'.format(ROOT))
        import get_arc_main
        CHECK_FOR_UPDATES = True
        
    else:
        sys.path.append('{}\\arc'.format(ROOT))
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
        CHECK_FOR_UPDATES = False
    import JLog

def ensure_dir(folder):
    """Ensures entire directory structure given exists"""
    try:
        os.makedirs(folder)
    except Exception:
        pass
# End of ensure_dir function

#def checkUSA(lat, lon):
#    """Checks if a given Lat/Long is within the US boundary (To decide which elev service to use)"""
#    # http://en.wikipedia.org/wiki/Extreme_points_of_the_United_States#Westernmost
#    top = 49.3457868 # north lat
#    left = -124.7844079 # west long
#    right = -66.9513812 # east long
#    bottom = 24.7433195 # south lat
#    if bottom <= float(lat) <= top and left <= float(lon) <= right:
#        in_usa = True
#    else:
#        in_usa = False
#    return in_usa


################################################################
#### ----------------- CLASS DEFINITIONS -----------------  ####
################################################################

class Main(object):
    """GUI for the Antecedent Rainfall Calculator"""

    def __init__(self):
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
        install_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        # Print Title Graphic
        print(potentialTitles.FINAL_TITLE)
        # Check for updates
        if CHECK_FOR_UPDATES is True:
            try:
                get_arc_main.install_or_upgrade()
            except Exception:
                pass
        # Create PrintLog
        self.L = JLog.PrintLog(Delete=True)
        # Announce GUI
        self.L.Wrap("Launching Graphical User Interface...")
        # Determine DPI Scaling settings
        dpi_set_at_125 = windowsScaling.scalingAt125()
        if dpi_set_at_125 is True:   # Medium - 125% Windows DPI scaling
            self.START_SIZE = (510, 150)
            self.EXPANDED_WATERSHED_SIZE = (544, 450)
            self.EXPANDED_SIZE = (544, 494)
            GEOM = "510x150+600+350"
        else:  # Small or Large - 100% or 150% Windows DPI scaling
#            self.START_SIZE = (396, 122)
#            self.EXPANDED_SIZE = (440, 410)
#            GEOM = "396x122+600+350"
            self.START_SIZE = (396, 130)
            self.EXPANDED_WATERSHED_SIZE = (440, 350)
            self.EXPANDED_SIZE = (440, 420)
            GEOM = "396x132+600+350"
        # Create UI Object
        self.master = tkinter.Tk()
        self.master.title('Antecedent Rainfall Calculator')
        try:
            graph_icon_file = install_folder + '/GUI Images/Graph.ico'
            self.master.wm_iconbitmap(graph_icon_file)
        except Exception:
            graph_icon_file = os.path.join(sys.prefix, 'images\\Graph.ico')
            self.master.wm_iconbitmap(graph_icon_file)
        self.master.minsize(width=self.START_SIZE[0], height=self.START_SIZE[1])
        self.master.geometry(GEOM)
        # Create Labels
        self.label_latitude = tkinter.ttk.Label(self.master, text="Latitude (DD):")
        self.label_longitude = tkinter.ttk.Label(self.master, text="Longitude (-DD):")
        self.label_year = tkinter.ttk.Label(self.master, text='Year (yyyy):')
        self.label_month = tkinter.ttk.Label(self.master, text="Month (m or mm):")
        self.label_day = tkinter.ttk.Label(self.master, text="Day (d or dd):")
        self.label_watershed_scope = tkinter.ttk.Label(self.master, text="Geographic Scope")
        self.label_image_name = tkinter.ttk.Label(self.master, text='Image or Event Name (Optional):')
        self.label_image_source = tkinter.ttk.Label(self.master, text='Image Source (Optional):')
        self.label_output_folder = tkinter.ttk.Label(self.master, text='Output Folder (Optional - Saves figure as PDF):')
        self.label_parameter = tkinter.ttk.Label(self.master, text='Parameter to be calculated/graphed:')
        self.label_y_axis_scale = tkinter.ttk.Label(self.master, text='Y-Axis Scale (For batch operations):')
        self.label_forecast = tkinter.ttk.Label(self.master, text='7-Day Forecast - Powered by Dark Sky (https://darksky.net/poweredby):')
        self.LABEL_CUSTOM_WATERSHED_NAME = tkinter.ttk.Label(self.master, text='Custom Watershed Name:')
        self.LABEL_CUSTOM_WATERSHED_FILE = tkinter.ttk.Label(self.master, text='Custom Watershed Shapefile:')
        # Create Entry Boxes
        self.ENTRY_LATITUDE = tkinter.ttk.Entry(self.master)
        self.ENTRY_LONGITUDE = tkinter.ttk.Entry(self.master)
        self.ENTRY_YEAR = tkinter.ttk.Entry(self.master)
        self.ENTRY_MONTH = tkinter.ttk.Entry(self.master)
        self.ENTRY_DAY = tkinter.ttk.Entry(self.master)
        self.ENTRY_IMAGE_NAME = tkinter.ttk.Entry(self.master)
        self.ENTRY_IMAGE_SOURCE = tkinter.ttk.Entry(self.master)
        self.ENTRY_OUTPUT_FOLDER = tkinter.ttk.Entry(self.master)
        self.ENTRY_OUTPUT_FOLDER.insert(0, str(winshell.desktop()))
        self.ENTRY_CUSTOM_WATERSHED_NAME = tkinter.ttk.Entry(self.master)
        self.ENTRY_CUSTOM_WATERSHED_FILE = tkinter.ttk.Entry(self.master)
        # Create Radio Button for Parameter Selection
        self.RADIO_VARIABLE_PARAMETER = tkinter.StringVar()
        self.RADIO_VARIABLE_PARAMETER.set('Rain')  # initialize
        self.RADIO_BUTTON_PARAMETER_RAIN = tkinter.ttk.Radiobutton(self.master, text='Rain', variable=self.RADIO_VARIABLE_PARAMETER, value='Rain')
        self.RADIO_BUTTON_PARAMETER_SNOW = tkinter.ttk.Radiobutton(self.master, text='Snow', variable=self.RADIO_VARIABLE_PARAMETER, value='Snow')
        self.RADIO_BUTTON_PARAMETER_SNOW_DEPTH = tkinter.ttk.Radiobutton(self.master, text='Snow Depth', variable=self.RADIO_VARIABLE_PARAMETER, value='Snow Depth')
        # Create Radio Button for Y-Axis-Scale
        self.RADIO_VARIABLE_Y_AXIS = tkinter.StringVar()
        self.RADIO_VARIABLE_Y_AXIS.set(False)  # initialize
        self.RADIO_BUTTON_Y_AXIS_VARIABLE = tkinter.ttk.Radiobutton(self.master, text='Variable', variable=self.RADIO_VARIABLE_Y_AXIS, value=False)
        self.RADIO_BUTTON_Y_AXIS_CONSTANT = tkinter.ttk.Radiobutton(self.master, text='Constant', variable=self.RADIO_VARIABLE_Y_AXIS, value=True)
        # Create Radio Button for 7-day Forecast
        self.RADIO_VARIABLE_FORECAST = tkinter.StringVar()
        self.RADIO_VARIABLE_FORECAST.set(False)  # initialize
        self.RADIO_BUTTON_FORECAST_INCLUDE = tkinter.ttk.Radiobutton(self.master, text='Include Forecast', variable=self.RADIO_VARIABLE_FORECAST, value=True)
        self.RADIO_BUTTON_FORECAST_EXCLUDE = tkinter.ttk.Radiobutton(self.master, text="Don't Include Forecast", variable=self.RADIO_VARIABLE_FORECAST, value=False)
        # Create watershed scope dropdown
        self.watershed_scope_string_var = tkinter.StringVar()
        self.watershed_scope_string_var.set('Single Point')
        options = ['Single Point',
                   'HUC12',
                   'HUC10',
                   'HUC8',
                   'Custom Polygon']
        self.watershed_scope_menu = tkinter.OptionMenu(self.master,
                                                       self.watershed_scope_string_var,
                                                       *(options),
                                                       command=self.watershed_selection)
        # Create Image Object for button Browse_DIR button
        try:
            folder_icon_path = os.path.join(sys.prefix, 'images\\folder.gif')
            self.FOLDER_IMAGE = tkinter.PhotoImage(file=folder_icon_path)
        except Exception:
            folder_icon_path = install_folder + '/GUI Images/folder.gif'
            self.FOLDER_IMAGE = tkinter.PhotoImage(file=folder_icon_path)
        # Create StringVar Objects
        self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON = tkinter.StringVar()
        self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON.set('Show Options')
        # Create Buttons
        self.BUTTON_CALCULATE = tkinter.ttk.Button(self.master, text='Calculate/Graph', command=self.calculate_and_graph)
        self.BUTTON_BATCH = tkinter.ttk.Button(self.master, text='Add to Batch', command=self.add_to_batch_list)
        self.BUTTON_SHOW_OPTIONS = tkinter.ttk.Button(self.master, textvariable=self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON, command=self.show_save_options)
        self.BUTTON_QUIT = tkinter.ttk.Button(self.master, text='Quit', command=self.quit_command)
        self.BUTTON_BROWSE_DIR = tkinter.ttk.Button(self.master, text='Browse', command=self.ask_directory, image=self.FOLDER_IMAGE)
        self.BUTTON_BROWSE_SHAPEFILE = tkinter.ttk.Button(self.master, text='Browse', command=self.ask_shapefile, image=self.FOLDER_IMAGE)
        self.BUTTON_REPORT_ISSUE = tkinter.ttk.Button(self.master, text='Report Issue', command=self.send_log)
        # Grid Labels
        self.label_latitude.grid(row=1, column=0, sticky='w', padx=3, pady=2, columnspan=1)
        self.label_longitude.grid(row=1, column=1, sticky='w', padx=3, pady=2, columnspan=1)
        self.label_year.grid(row=3, column=0, sticky='w', padx=3, pady=2, columnspan=1)
        self.label_month.grid(row=3, column=1, sticky='w', padx=3, pady=2, columnspan=1)
        self.label_day.grid(row=3, column=2, sticky='w', padx=3, pady=2, columnspan=1)
        self.label_watershed_scope.grid(row=1, column=2, sticky='W', padx=3, pady=2, columnspan=1)
        # Grid Entry Boxes
        self.ENTRY_LATITUDE.grid(row=2, column=0, padx=3, sticky='w')
        self.ENTRY_LONGITUDE.grid(row=2, column=1, padx=3, sticky='w')
        self.ENTRY_YEAR.grid(row=4, column=0, padx=3, sticky='w')
        self.ENTRY_MONTH.grid(row=4, column=1, padx=3, sticky='w')
        self.ENTRY_DAY.grid(row=4, column=2, padx=3, sticky='w')
        # Grid Watershed Scale Drop-down
        self.watershed_scope_menu.grid(row=2, column=2, sticky='w')
        # Grid Buttons
        self.BUTTON_CALCULATE.grid(row=21, column=0, padx=5, pady=5, columnspan=2, sticky='w')
        self.BUTTON_BATCH.grid(row=21, column=1, padx=1, pady=5, sticky='w')
        self.BUTTON_SHOW_OPTIONS.grid(row=21, column=1, padx=5, pady=5, columnspan=2)
        self.BUTTON_QUIT.grid(row=21, column=2, padx=1, pady=5, sticky='e')
#        self.BUTTON_REPORT_ISSUE.grid(row=1, column=2, sticky='ne')
        # Configure rows and columns
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        # a trick to activate the window (on windows 7)
        self.master.deiconify()
    # End of __init__ method

    def run(self):
        """Starts the GUI's TKinter mainloop"""
        # start mainloop
        self.master.mainloop()
    # End of run method

    def watershed_selection(self, event):
        """Acts on the self.watershed_scope_menu drop-down selection"""
        watershed_scale = self.watershed_scope_string_var.get()
        if watershed_scale == 'Single Point':
            if self.show:
                try:
                    # Remove Custom Watershed Label and Entry Box
                    self.LABEL_CUSTOM_WATERSHED_NAME.grid_forget()
                    self.ENTRY_CUSTOM_WATERSHED_NAME.grid_forget()
                    self.LABEL_CUSTOM_WATERSHED_FILE.grid_forget()
                    self.ENTRY_CUSTOM_WATERSHED_FILE.grid_forget()
                    self.BUTTON_BROWSE_SHAPEFILE.grid_forget()
                    # Unblock snow and snow depth
                    self.RADIO_BUTTON_PARAMETER_SNOW.grid(row=16, column=1)
                    self.RADIO_BUTTON_PARAMETER_SNOW_DEPTH.grid(row=16, column=2)
                    # Unblock Forecast
                    self.label_forecast.grid(row=19, sticky='sw', padx=5, pady=3, columnspan=5)
                    self.RADIO_BUTTON_FORECAST_INCLUDE.grid(row=20, column=0)
                    self.RADIO_BUTTON_FORECAST_EXCLUDE.grid(row=20, column=1)
                    # Unblock Variable Y-Axis Selection
                    self.label_y_axis_scale.grid(row=17, sticky='sw', padx=5, pady=3, columnspan=5)
                    self.RADIO_BUTTON_Y_AXIS_VARIABLE.grid(row=18, column=0, padx=7)
                    self.RADIO_BUTTON_Y_AXIS_CONSTANT.grid(row=18, column=1, padx=7)
                    # Unblock Image Name and Source Selections
                    self.label_image_name.grid(row=9, sticky='sw', padx=5, pady=3, columnspan=5)
                    self.ENTRY_IMAGE_NAME.grid(row=10, padx=5, sticky='ew', columnspan=6)
                    self.label_image_source.grid(row=11, sticky='sw', padx=5, pady=3, columnspan=5)
                    self.ENTRY_IMAGE_SOURCE.grid(row=12, padx=5, sticky='ew', columnspan=6)
                    # Unblock Batch Button
                    self.BUTTON_BATCH.grid(row=21, column=1, padx=1, pady=5, sticky='w')
                except Exception:
                    pass
                self.master.minsize(width=self.EXPANDED_SIZE[0], height=self.EXPANDED_SIZE[1])
            else:
                self.master.minsize(width=self.START_SIZE[0], height=self.START_SIZE[1])
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
        else: # Watershed Analysis
            # Set Parameter Variable to Rain
            self.RADIO_VARIABLE_PARAMETER.set('Rain')
            # Set Forecast variable to false
            self.RADIO_VARIABLE_FORECAST.set(False)
            # Set variable y-axis to Fixed 
            self.RADIO_VARIABLE_Y_AXIS.set(False)
            # Set Image Name and Source to Blank
            self.ENTRY_IMAGE_NAME.delete(0, 'end')
            self.ENTRY_IMAGE_SOURCE.delete(0, 'end')
            # Block any but Rain selection 
            if self.show:
                try:
                    self.RADIO_BUTTON_PARAMETER_SNOW.grid_forget()
                    self.RADIO_BUTTON_PARAMETER_SNOW_DEPTH.grid_forget()
                    # Block Forecast Selection
                    self.label_forecast.grid_forget()
                    self.RADIO_BUTTON_FORECAST_INCLUDE.grid_forget()
                    self.RADIO_BUTTON_FORECAST_EXCLUDE.grid_forget()
                    # Block Variable Y-Axis Selection
                    self.label_y_axis_scale.grid_forget()
                    self.RADIO_BUTTON_Y_AXIS_VARIABLE.grid_forget()
                    self.RADIO_BUTTON_Y_AXIS_CONSTANT.grid_forget()
                    # Block Image Name and Source selections
                    self.label_image_name.grid_forget()
                    self.label_image_source.grid_forget()
                    self.ENTRY_IMAGE_NAME.grid_forget()
                    self.ENTRY_IMAGE_SOURCE.grid_forget()
                    # Block Batch Button
                    self.BUTTON_BATCH.grid_forget()
                except Exception:
                    pass
                self.master.minsize(width=self.EXPANDED_WATERSHED_SIZE[0], height=self.EXPANDED_WATERSHED_SIZE[1])
                self.master.columnconfigure(0, weight=1)
                self.master.rowconfigure(0, weight=1)
        if watershed_scale == 'Custom Polygon':
            # Open options (if not already)
            if not self.show:
                self.show_save_options()
            # Grid Custom Watershed Entry Box
            self.LABEL_CUSTOM_WATERSHED_NAME.grid(row=9, sticky='sw', padx=5, pady=3, columnspan=5)
            self.ENTRY_CUSTOM_WATERSHED_NAME.grid(row=10, padx=5, sticky='ew', columnspan=6)
            self.LABEL_CUSTOM_WATERSHED_FILE.grid(row=11, sticky='sw', padx=5, pady=3, columnspan=5)
            self.ENTRY_CUSTOM_WATERSHED_FILE.grid(row=12, padx=5, sticky='ew', columnspan=6)
            self.BUTTON_BROWSE_SHAPEFILE.grid(row=12, column=6, padx=4, pady=1)
            # Remove options button
            self.BUTTON_SHOW_OPTIONS.grid_forget()
        else:
            # Remove Custom Watershed Label and Entry Box
            self.LABEL_CUSTOM_WATERSHED_NAME.grid_forget()
            self.ENTRY_CUSTOM_WATERSHED_NAME.grid_forget()
            self.LABEL_CUSTOM_WATERSHED_FILE.grid_forget()
            self.ENTRY_CUSTOM_WATERSHED_FILE.grid_forget()
            self.BUTTON_BROWSE_SHAPEFILE.grid_forget()
            # Replace Show Options Button
            try:
                self.BUTTON_SHOW_OPTIONS.grid(row=21, column=1, padx=5, pady=5, columnspan=2)
            except Exception:
                pass


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

    def askfile(self):
        """Returns a selected CSV file."""
#        initial_folder = os.path.join(sys.prefix, 'Batch_Files')
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        batch_folder = '{}\\Batch'.format(root)
        default_template_path = '{}\\ARC Batch Template.csv'.format(batch_folder)
        # define options for opening a file
        file_opt = options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('CSV file', '.csv'), ('all files', '.*')]
        options['initialdir'] = batch_folder
        options['initialfile'] = 'ARC Batch Template.csv'
        options['parent'] = self.master
        options['title'] = "Locate the batch CSV file for this project"
        # get filename
        filename = tkinter.filedialog.askopenfilename(**file_opt)
        return filename
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

    def show_save_options(self):
        """
        Toggles the visibility of advanced options
        """
        watershed_scale = self.watershed_scope_string_var.get()
        if self.show:
            self.label_image_name.grid_forget()
            self.label_image_source.grid_forget()
            self.ENTRY_IMAGE_NAME.grid_forget()
            self.ENTRY_IMAGE_SOURCE.grid_forget()
            self.label_output_folder.grid_forget()
            self.ENTRY_OUTPUT_FOLDER.grid_forget()
            self.BUTTON_BROWSE_DIR.grid_forget()
            self.label_parameter.grid_forget()
            self.RADIO_BUTTON_PARAMETER_RAIN.grid_forget()
            self.RADIO_BUTTON_PARAMETER_SNOW.grid_forget()
            self.RADIO_BUTTON_PARAMETER_SNOW_DEPTH.grid_forget()
            self.label_y_axis_scale.grid_forget()
            self.RADIO_BUTTON_Y_AXIS_VARIABLE.grid_forget()
            self.RADIO_BUTTON_Y_AXIS_CONSTANT.grid_forget()
            self.label_forecast.grid_forget()
            self.RADIO_BUTTON_FORECAST_INCLUDE.grid_forget()
            self.RADIO_BUTTON_FORECAST_EXCLUDE.grid_forget()
            self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON.set('Show Options')
            self.master.minsize(width=self.START_SIZE[0], height=self.START_SIZE[1])
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
            self.show = False
        else:
            if watershed_scale == 'Single Point':
                self.label_image_name.grid(row=9, sticky='sw', padx=5, pady=3, columnspan=5)
                self.ENTRY_IMAGE_NAME.grid(row=10, padx=5, sticky='ew', columnspan=6)
                self.label_image_source.grid(row=11, sticky='sw', padx=5, pady=3, columnspan=5)
                self.ENTRY_IMAGE_SOURCE.grid(row=12, padx=5, sticky='ew', columnspan=6)
            self.label_output_folder.grid(row=13, sticky='sw', padx=5, pady=3, columnspan=5)
            self.ENTRY_OUTPUT_FOLDER.grid(row=14, padx=5, sticky='ew', columnspan=6)
            self.BUTTON_BROWSE_DIR.grid(row=14, column=6, padx=4, pady=1)
            self.label_parameter.grid(row=15, sticky='sw', padx=6, pady=3, columnspan=5)
            self.RADIO_BUTTON_PARAMETER_RAIN.grid(row=16, column=0)
            if watershed_scale == 'Single Point':
                self.RADIO_BUTTON_PARAMETER_SNOW.grid(row=16, column=1)
                self.RADIO_BUTTON_PARAMETER_SNOW_DEPTH.grid(row=16, column=2)
                self.label_y_axis_scale.grid(row=17, sticky='sw', padx=5, pady=3, columnspan=5)
                self.RADIO_BUTTON_Y_AXIS_VARIABLE.grid(row=18, column=0, padx=7)
                self.RADIO_BUTTON_Y_AXIS_CONSTANT.grid(row=18, column=1, padx=7)
                self.label_forecast.grid(row=19, sticky='sw', padx=5, pady=3, columnspan=5)
                self.RADIO_BUTTON_FORECAST_INCLUDE.grid(row=20, column=0)
                self.RADIO_BUTTON_FORECAST_EXCLUDE.grid(row=20, column=1)
                self.master.minsize(width=self.EXPANDED_SIZE[0], height=self.EXPANDED_SIZE[1])
            else:
                self.master.minsize(width=self.EXPANDED_WATERSHED_SIZE[0], height=self.EXPANDED_WATERSHED_SIZE[1])
            self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON.set('Hide Options')
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
            self.show = True
        return
    # End show_save_options method

    def calculate_and_graph(self):
        """
        Runs the main function with currently selected values.
            -Will run as batch if batch processes have already been entered
        """
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
            self.L.Wrap('Click "Calculate/Graph" to retry, "Report Issue" to send an error log to the developer, or "Quit" to exit the program.')
        else:
            self.L.Wrap("  NOAA's Servers ONLINE.  Proceeding with request...")
            self.L.print_separator_line()
            self.L.Wrap('')
            try:
                self.calculate_or_add_batch(False)
            except Exception:
                self.L.Wrap(traceback.format_exc())
                raise
    # End of calculate_and_graph method

    def add_to_batch_list(self):
        """Adds Currently entered values to batch processing list"""
        try:
            self.calculate_or_add_batch(True)
        except Exception:
            self.L.Wrap(traceback.format_exc())
    # End of add_to_batch_list method

    def batch_from_csv(self):
        """Reads batch inputs from CSV and runs them"""
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        batch_folder = '{}\\Batch'.format(root)
        default_template_path = '{}\\ARC Batch Template.csv'.format(batch_folder)
        # Test for presence of Batch Template CSV
        template_exists = os.path.exists(default_template_path)
        if not template_exists:
            try:
                # Ensure Batch Folder Exists
                ensure_dir(batch_folder)
                with open(default_template_path, 'w') as CSV:
                    CSV.write('Latitude (Decimal Degrees),Longitude (Decimal Degrees),Year (yyyy),Month (m or mm),Day (d or dd),Image or Event Name (Optional),Image Source (Optional),Output Folder\n')
            except Exception:
                pass
        batch_csv_file = self.askfile()
        try:
            if batch_csv_file == '':
                pass
            elif os.path.splitext(batch_csv_file)[1].lower() == '.csv':
                # Locate new values
                first_line = True
                with open(batch_csv_file, 'r') as lines:
                    for line in lines:
                        if first_line:
                            first_line = False
                        else:
                            # Clear Existing Values
                            self.ENTRY_LATITUDE.delete(0, 'end')
                            self.ENTRY_LONGITUDE.delete(0, 'end')
                            self.ENTRY_YEAR.delete(0, 'end')
                            self.ENTRY_MONTH.delete(0, 'end')
                            self.ENTRY_DAY.delete(0, 'end')
                            self.ENTRY_IMAGE_NAME.delete(0, 'end')
                            self.ENTRY_IMAGE_SOURCE.delete(0, 'end')
                            self.ENTRY_OUTPUT_FOLDER.delete(0, 'end')
                            # Parse CSV Line Values
                            csv_inputs = line.replace('\n', '').split(',')
                            # Insert New Values
                            self.ENTRY_LATITUDE.insert(0, csv_inputs[0])
                            self.ENTRY_LONGITUDE.insert(0, csv_inputs[1])
                            self.ENTRY_YEAR.insert(0, csv_inputs[2])
                            self.ENTRY_MONTH.insert(0, csv_inputs[3])
                            self.ENTRY_DAY.insert(0, csv_inputs[4])
                            self.ENTRY_IMAGE_NAME.insert(0, csv_inputs[5])
                            self.ENTRY_IMAGE_SOURCE.insert(0, csv_inputs[6])
                            self.ENTRY_OUTPUT_FOLDER.insert(0, csv_inputs[7])
                            self.add_to_batch_list()
                self.calculate_and_graph()
            else:
                print('')
                print('Selected file must be in CSV format!')
                print('')
        except Exception:
            print('')
            print('Selected file must be in CSV format!')
            print('')
    # End batch_from_csv method

    def get_30_years(self):
        """Runs a batch of the most recent 30 years (since the last GRID data update) at the selected point"""
        # Set scale to Constant
        ##        originalVar2 = self.RADIO_VARIABLE_Y_AXIS.get()
        # self.RADIO_VARIABLE_Y_AXIS.set(True)
        # Force Month to March if none given
        original_month = self.ENTRY_MONTH.get()
        if original_month == "":
            self.ENTRY_MONTH.insert(0, 3)
        # Force Day to the 15th if none given
        original_day = self.ENTRY_DAY.get()
        if original_day == "":
            self.ENTRY_DAY.insert(0, 15)
        # Force img name
        original_name = self.ENTRY_IMAGE_NAME.get()
        if original_name == "":
            self.ENTRY_IMAGE_NAME.insert(0, 'Individual Station Data')
        # Force Source
        original_source = self.ENTRY_IMAGE_SOURCE.get()
        if original_source == "":
            self.ENTRY_IMAGE_SOURCE.insert(0, 'Individual Station Data')
        # Set year field to each viable year
        for year in range(2017, 1984, -1):
            self.ENTRY_YEAR.delete(0, 'end')
            self.ENTRY_YEAR.insert(0, year)
            self.add_to_batch_list()
        self.calculate_and_graph()
        # Restore changed settings
    # self.RADIO_VARIABLE_Y_AXIS.set(originalVar2)
        self.ENTRY_YEAR.delete(0, 'end')
        self.ENTRY_YEAR.insert(0, 30)
        self.ENTRY_MONTH.delete(0, 'end')
        self.ENTRY_MONTH.insert(0, original_month)
        self.ENTRY_DAY.delete(0, 'end')
        self.ENTRY_DAY.insert(0, original_day)
        self.ENTRY_IMAGE_NAME.delete(0, 'end')
        self.ENTRY_IMAGE_NAME.insert(0, original_name)
        self.ENTRY_IMAGE_SOURCE.delete(0, 'end')
        self.ENTRY_IMAGE_SOURCE.insert(0, original_source)
    # End of get_30_years method

    def get_50_years(self):
        """Runs a batch of the most recent 50 years at the location, month, and day provided"""
        # Set forcast to Enabled
        original_variable_3 = self.RADIO_VARIABLE_FORECAST.get()
        self.RADIO_VARIABLE_FORECAST.set(True)
        # Set scale to Constant
        original_variable_2 = self.RADIO_VARIABLE_Y_AXIS.get()
        self.RADIO_VARIABLE_Y_AXIS.set(True)
        # Force Month to JUanuary if none given
        original_month = self.ENTRY_MONTH.get()
        if original_month == "":
            self.ENTRY_MONTH.insert(0, 1)
        # Force Day to the 15th if none given
        original_day = self.ENTRY_DAY.get()
        if original_day == "":
            self.ENTRY_DAY.insert(0, 15)
        # Set year field to current year
        current_date = datetime.datetime.now()
        year = int(current_date.strftime('%Y'))
        count = 50
        while count > 0:
            count -= 1
            self.ENTRY_YEAR.delete(0, 'end')
            self.ENTRY_YEAR.insert(0, year)
            year -= 1
            self.add_to_batch_list()
        self.calculate_and_graph()
        # Restore changed settings
        self.RADIO_VARIABLE_Y_AXIS.set(original_variable_2)
        self.RADIO_VARIABLE_FORECAST.set(original_variable_3)
        self.ENTRY_MONTH.delete(0, 'end')
        self.ENTRY_MONTH.insert(0, original_month)
        self.ENTRY_DAY.delete(0, 'end')
        self.ENTRY_DAY.insert(0, original_day)
    # End of get_50_years method

    def calculate_or_add_batch(self, batch):
        """
        If batch is False
        --Executes main business logic of the Antecedent Rainfall Calculator
        If batch is True
        --Adds current field values to batch list
        """
        start_time = time.clock()
        # Get Paramaters
        latitude = self.ENTRY_LATITUDE.get()
        longitude = self.ENTRY_LONGITUDE.get()
        observation_year = self.ENTRY_YEAR.get()
        observation_month = self.ENTRY_MONTH.get()
        observation_day = self.ENTRY_DAY.get()
        image_name = self.ENTRY_IMAGE_NAME.get()
        image_source = self.ENTRY_IMAGE_SOURCE.get()
        save_folder = self.ENTRY_OUTPUT_FOLDER.get()
        custom_watershed_name = self.ENTRY_CUSTOM_WATERSHED_NAME.get()
        custom_watershed_file = self.ENTRY_CUSTOM_WATERSHED_FILE.get()
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
                # Testing / Batch Shortcuts
                if str(observation_year) == '50':  # 50 Years trick
                    self.get_50_years()
                    observation_year = self.ENTRY_YEAR.get()
                    return
                elif str(observation_year) == '30':  # 30 Years AlphaGrid Test
                    self.get_30_years()
                    return
                else:
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
        radio = self.RADIO_VARIABLE_PARAMETER.get()
        fixed_y_max = self.RADIO_VARIABLE_Y_AXIS.get()
        if fixed_y_max == "1":
            fixed_y_max = True
        forecast_enabled = self.RADIO_VARIABLE_FORECAST.get()
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
                    self.L.Wrap('Setting Output Folder to Desktop...')
                    save_folder = str(winshell.desktop())
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

if __name__ == '__main__':
    APP = Main()
    APP.run()

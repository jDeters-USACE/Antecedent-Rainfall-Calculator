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
##           install.py             ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

"""Creates a desktop shortcut for the Antecedent Rainfall Calculator"""

import os
import time
import winshell
import multiprocessing


def create_shortcut_unfrozen():
    """Creates a desktop shortcut for the Antecedent Rainfall Calculator"""
    # Define Shortcut Variables
    python_path = 'C:\\Antecedent Rainfall Calculator\\WinPythonZero32\\python-3.6.5\\python.exe'
    desktop_path = str(winshell.desktop()) # get desktop path
    icon = "C:\\Antecedent Rainfall Calculator\\GUI Images\\Graph.ico"
    launch_script = '"C:\\Antecedent Rainfall Calculator\\Python Scripts\\ant_GUI.py"'
    shortcut_path = os.path.join(desktop_path, 'Antecedent Rainfall Calculator.lnk')
    description = 'Launches the Antecedent Rainfall Calculator, written by Jason C. Deters'
    # Create shortcut
    shortcut_exists = os.path.exists(shortcut_path)
    if not shortcut_exists:
        print('Creating Desktop shortcut for the Antecedent Rainfall Calculator...')
    else:
        print('Validating Desktop shortcut...')
    winshell.CreateShortcut(Path=shortcut_path,
                            Target=python_path,
                            Arguments=launch_script,
                            StartIn=desktop_path,
                            Icon=(icon, 0),
                            Description=description)
    print('')
    print('All Elements installed successfully!    Closing window in 5 seconds')
    time.sleep(5)


def create_shortcut_frozen():
    """Creates a desktop shortcut for the Antecedent Rainfall Calculator"""
    # Define Shortcut Variables
    module_path = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_path)[0]
    frozen_exe_path = '{}\\Antecedent Rainfall Calculator.exe'.format(root_folder)
    desktop_path = str(winshell.desktop()) # get desktop path
    icon = "{}\\GUI Images\\Graph.ico".format(root_folder)
    shortcut_path = os.path.join(desktop_path, 'Antecedent Rainfall Calculator.lnk')
    description = 'Launches the Antecedent Rainfall Calculator, written by Jason C. Deters'
    # Create shortcut
    shortcut_exists = os.path.exists(shortcut_path)
    if not shortcut_exists:
        print('Creating Desktop shortcut for the Antecedent Rainfall Calculator...')
    else:
        print('Validating Desktop shortcut...')
    winshell.CreateShortcut(Path=shortcut_path,
                            Target=frozen_exe_path,
                            StartIn=desktop_path,
                            Icon=(icon, 0),
                            Description=description)
    print('')




if __name__ == '__main__':
    multiprocessing.freeze_support()
    create_shortcut_frozen()
    
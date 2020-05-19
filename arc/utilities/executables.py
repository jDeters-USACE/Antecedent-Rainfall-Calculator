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
##          executables.py          ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-18   ##
##  ------------------------------- ##
######################################

from __future__ import (absolute_import)

# Import Built-In Libraries
import os
import sys
import time
import subprocess

# Import Custom Libraries
try:
    from . import JLog
except Exception:
    import JLog

# FUNCTION DEFINITIONS

def check_output(command,console):
    """This function allows me the main process to receive the output from an external .exe process without queues"""
    if console is True:
        process = subprocess.Popen(command, close_fds=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        return
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        output, error = process.communicate()
        returncode = process.poll()
        return returncode,output
# End of check_output


# CLASS DEFINITIONS

class cmdString(object):
    """This function simplifies the programmatic generation/execution of command line processes"""

    def __init__(self):
        self.command = []
        self.command_string = ""
        self.L = JLog.PrintLog(Indent=6)

    def AddStringInQuotes(self,String):
        """Retains '"' around directories to protect from space breaks in the CMD interpreter"""
        self.command.append('"'+String+'"')
        return

    def AddString(self,String):
        self.command.append(String)
        return

    def Batch(self):
        # Determine number of commands in command list
        command_length = len(self.command)
        # Create command string for printing / debugging
        self.command_string = str(self.command[0])
        # Remove quotes from first item in command list
        self.command[0] = self.command[0].strip('"')
        for i in range(1, command_length):
            # Keep self.command_string updated (for printing/debugging)
            self.command_string = self.command_string + ' ' + str(self.command[i])
            # Remove quotes from command list item
            self.command[i] = self.command[i].strip('"')
        # Print the string version of the command list
        self.L.Wrap('Command line string to be executed:')
        self.L.Wrap(self.command_string)
        self.L.Wrap(' ')
        bat = r"C:\Temp\CMD.bat"
        B = JLog.PrintLog(Delete=True,Log=bat,Width=1000)
        B.Write(self.command_string)
        returncode,output = check_output(bat, True)

    def Execute(self):
        # Determine number of commands in command list
        command_length = len(self.command)
        # Create command string for printing / debugging
        self.command_string = str(self.command[0])
        # Remove quotes from first item in command list
        self.command[0] = self.command[0].strip('"')
        for i in range(1, command_length):
            # Keep self.command_string updated (for printing/debugging)
            self.command_string = self.command_string + ' ' + str(self.command[i])
            # Remove quotes from command list item
            self.command[i] = self.command[i].strip('"')
        # Print the string version of the command list
        self.L.Wrap('Command line string to be executed:')
        self.L.Wrap(self.command_string)
        self.L.Wrap(' ')
        # Run command
        self.L.Wrap(str(time.ctime())+" - Executing command...")
        returncode,output = check_output(self.command, False)
        # Report output
        self.L.Wrap('Command line output:')
        self.L.Wrap(output)
        # Check return code
        if returncode != 0:
            self.L.Wrap('Error: Execution failed.')
        return

    def ExecuteConsole(self):
        # Determine number of commands in command list
        command_length = len(self.command)
        # Create command string for printing / debugging
        self.command_string = str(self.command[0])
        # Remove quotes from first item in command list
        self.command[0] = self.command[0].strip('"')
        for i in range(1, command_length):
            # Keep self.command_string updated (for printing/debugging)
            self.command_string = self.command_string + ' ' + str(self.command[i])
            # Remove quotes from command list item
            self.command[i] = self.command[i].strip('"')
        # Print the string version of the command list
        self.L.Wrap('Command line string to be executed:')
        self.L.Wrap(self.command_string)
        self.L.Wrap(' ')
        # Run command
        self.L.Wrap(str(time.ctime())+" - Executing command...")
        check_output(self.command, True)
        return
# end of cmdString class

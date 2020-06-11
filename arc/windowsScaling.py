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
##        windowsScaling.py         ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

"""
Determine if the user has Windows Scaling set to 100%, 125% or 150% using only Tkinter
This is important because GUI sizing can be disrupted by Windows Scaling settings
"""

try:
    import Tkinter
except:
    import tkinter as Tkinter

def scalingAt125():
    """
    Determine if the user has Windows Scaling set to 100%, 125% or 150% using only Tkinter
    This is important because GUI sizing can be disrupted by Windows Scaling settings
    """
    Window = Tkinter.Tk()
    Window.geometry("500x500+80+80")
    # Create a frame in which to place the test label
    frame = Tkinter.Frame(Window) 
    frame.pack(side = "top")
    # Create the label to be measured
    label_to_be_measured = Tkinter.Label(frame, font = ("Purisa", 10), text = "The width of this in pixels is.....", bg = "yellow")
    # Grid the label to be measured
    label_to_be_measured.grid(row = 0, column = 0) # put the label in
    # Call Update label to be measured [TRIGGERS WIDTH CALCULATION EVENT]
    label_to_be_measured.update_idletasks()
    # Get width info from label to be measured
    width = label_to_be_measured.winfo_width()
    # Close test window
    Window.destroy()
    # Set default scalingSetAt125 value to False
    scalingSetAt125 = False
    # If width exceeds 195, set scalingSetAt125 value to True
    if width > 195:
        scalingSetAt125 = True
    # Return scalingSetAt125 value
    return scalingSetAt125

if __name__ == '__main__':
    result = scalingAt125()
    print('Scaling set to 125% = {}'.format(result))

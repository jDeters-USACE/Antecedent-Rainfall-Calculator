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
##         os_convenience.py        ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-18   ##
##  ------------------------------- ##
######################################

"""
A few convenience functions I got tired of writing into scripts.
"""

import os
import stat

def ensure_dir(folder):
    """Ensures entire directory structure given exists"""
    try:
        os.makedirs(folder)
    except Exception:
        pass
# End of ensure_dir function


def delete_read_only(file_path):
    """Deletes read-only files by changing their properties and retrying"""
    try:
        os.remove(file_path)
    except Exception:
        os.chmod(file_path, stat.S_IWRITE)
        os.remove(file_path)
# End of delete_read_only function

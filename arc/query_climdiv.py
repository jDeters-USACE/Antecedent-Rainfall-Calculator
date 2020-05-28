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
##        query_climdiv.py          ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

"""
Downloads, updates, and querries climdiv data from NOAA
"""
from __future__ import (print_function, absolute_import)  # Python 3 support

# Import Standard Libraries
import os
import sys
import urllib3
import stat
import time
import datetime
import traceback
import requests

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Import Custom Libraries
try:
    # Frozen Application Method
    from . import query_shapefile_at_point
    from .utilities import JLog
except Exception:
    # Development Environment Method
    import query_shapefile_at_point
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
    import JLog

log = JLog.PrintLog()

# Find module path
MODULE_FOLDER = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT_FOLDER = os.path.split(MODULE_FOLDER)[0]
# Find clim_div folder
CLIM_DIV_FOLDER = u'{}\\GIS\\climdiv'.format(ROOT_FOLDER)

def ensure_dir(folder):
    """Ensures entire directory structure given exists"""
    try:
        os.makedirs(folder)
    except Exception:
        pass
# End of ensure_dir function

def delete_read_only(file_path):
    """Ensures Windows Read-Only status does not interrupt os.remove function"""
    try:
        os.remove(file_path)
    except Exception:
        try:
            os.chmod(file_path, stat.S_IWRITE)
            os.remove(file_path)
        except Exception:
            pass

def sizeof_fmt(num, suffix='B'):
    for unit in [' ', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "{:6.2f} {}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:6.2f} {}{}".format(num, 'Y', suffix)

def ensure_current_pdsidv_file():
    """Checks that the newest procdate.txt corresponds with the current pdsidv file"""
    download = False
    ensure_dir(CLIM_DIV_FOLDER)
    base_url = 'https://www1.ncdc.noaa.gov/pub/data/cirs/climdiv'
    proc_date_url = '{}/procdate.txt'.format(base_url)
    # Try to avoid checking the server, if possible (New file published on 4th of the month)
    check_server = True
    log.Wrap("  Checking for this month's PDSI file on local drive...")
    today = datetime.datetime.today()
    this_month_proc_date = today.strftime('%Y%m04')
    this_month_file_name = 'climdiv-pdsidv-v1.0.0-{}'.format(this_month_proc_date)
    current_file_path = '{}\\{}'.format(CLIM_DIV_FOLDER, this_month_file_name)
    if os.path.exists(current_file_path) is True:
        log.Wrap('    Local PDSI file found. Testing file...')
        pdsidv_file_size = os.path.getsize(current_file_path)
        if not pdsidv_file_size < 4415776:
            log.Wrap('      Test passed.')
            check_server = False
        else:
            log.Wrap('      Local PDSI file corrupt.')
            log.Wrap('      Deleting local file...')
            delete_read_only(current_file_path)
            check_server = True
    else:
        log.Wrap("    This month's PDSI file not found on local drive")
    if check_server is True:
        # Query ProcDate
        log.Wrap('  Querying the name and date of the latest PDSI file...')
        # urllib3
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
        response = http.request('GET', proc_date_url)
        proc_date = str(response.data.split(b"\n")[0], 'utf-8')
        current_file_name = 'climdiv-pdsidv-v1.0.0-{}'.format(str(proc_date))
        current_file_path = '{}\\{}'.format(CLIM_DIV_FOLDER, current_file_name)
        log.Wrap('    Latest file = {}'.format(current_file_name))
        log.Wrap('  Checking for PDSI file on local drive...')
        if os.path.exists(current_file_path) is False:
            log.Wrap('    Local PDSI file not found.')
            download = True
        else:
            log.Wrap('    Local PDSI file found. Testing file...')
            pdsidv_file_size = os.path.getsize(current_file_path)
            if pdsidv_file_size < 4415776:
                log.Wrap('      Local PDSI file corrupt.')
                log.Wrap('      Deleting local file...')
                delete_read_only(current_file_path)
                download = True
            else:
                log.Wrap('      Test passed.')
        if download is True:
            # Download Latest Dataset
            current_file_url = '{}/{}'.format(base_url, current_file_name)
            log.Wrap('  Connecting to latest PDSI file on server...')
            # Streaming with requests module
            num_bytes = 0
            count = 0
            with requests.get(current_file_url, stream=True) as r:
                r.raise_for_status()
                log.Wrap('  Writing PDSI file to local drive...')
                with open(current_file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                            num_bytes += 8192
                            count += 1
                            if count > 25:
                                formatted_bytes = sizeof_fmt(num_bytes)
                                log.print_status_message('  Downloading file... ({} bytes)'.format(formatted_bytes))
                                count = 0
            sys.stdout.flush()
            time.sleep(.1)
        # Clear out any old versions of the pdsidv file
        log.Wrap('  Searching for extraneous PDSI files on local drive...')
        for root, directories, file_names in os.walk(CLIM_DIV_FOLDER):
            for file_name in file_names:
                if 'pdsidv' in file_name:
                    if not proc_date in file_name:
                        log.Wrap('Deleting {}...'.format(file_name))
                        delete_path = '{}\\{}'.format(root, file_name)
                        delete_read_only(delete_path)
    return current_file_path

def get_clim_div(lat, lon):
    """Finds the NOAA Climate Division associated with a given Lat and Lon"""
    clim_div_shapefile = '{}\\GIS.OFFICIAL_CLIM_DIVISIONS.shp'.format(CLIM_DIV_FOLDER)
    feature_attribute_to_query = "CLIMDIV"
    clim_div = query_shapefile_at_point.check(lat=lat,
                                                lon=lon,
                                                shapefile=clim_div_shapefile,
                                                field_name=feature_attribute_to_query)
    if len(clim_div) < 4:
        clim_div = '0{}'.format(clim_div)
    return clim_div

def get_pdsidv(lat, lon, year, month, pdsidv_file):
    """Queries downloaded Palmer Drought Severity Index value for given lat, lon, year, and month"""
    log.print_section('PDSI - Palmer Drought Severity Index')
    log.Wrap('Querying the Palmer Drought Severity Index...')
    monthly_values = []
    values_with_classes = []
    lightgrn = (0.5, 0.8, 0.5)
    lightblu = (0.4, 0.5, 0.8)
    lightred = (0.8, 0.5, 0.5)
    white = (1, 1, 1)
    try:
        clim_div = get_clim_div(lat, lon)
        if pdsidv_file is None:
            pdsidv_file = ensure_current_pdsidv_file()
        line_identifier = '{}05{}'.format(clim_div, year)
        log.Wrap('  Opening PDSI file to collect monthly values...')
        for line in open(pdsidv_file):
            if line_identifier in line:
                monthly_values.append(line[11:17].replace(" ", ""))
                monthly_values.append(line[18:24].replace(" ", ""))
                monthly_values.append(line[25:31].replace(" ", ""))
                monthly_values.append(line[32:38].replace(" ", ""))
                monthly_values.append(line[39:45].replace(" ", ""))
                monthly_values.append(line[46:52].replace(" ", ""))
                monthly_values.append(line[53:59].replace(" ", ""))
                monthly_values.append(line[60:66].replace(" ", ""))
                monthly_values.append(line[67:73].replace(" ", ""))
                monthly_values.append(line[74:80].replace(" ", ""))
                monthly_values.append(line[81:87].replace(" ", ""))
                monthly_values.append(line[88:94].replace(" ", ""))
        if not monthly_values:
            log.Wrap('    Required monthly values not found in PDSI file.')
            # Test if this year's file is not yet available (Government Shutdown Workaround)
            pdsi_file_year = int(pdsidv_file[-8:-4])
            if pdsi_file_year < int(year):
                log.Wrap('      NOAA server has yet to publish the most up-to-date file.  PDSI Unavailable.')
            else:
                log.Wrap('      PDSI file assumed corrupt.  Deleting...')
                delete_read_only(pdsidv_file)
            output = [-99.99, 'Not available', white] + [pdsidv_file]
        else:
            for value in monthly_values:
                value_num = float(value)
                if value_num == -99.99:
                    classification = 'Not available'
                    shading = white
                elif value_num > 4:
                    classification = 'Extreme wetness'
                    shading = white
                elif value_num > 2.99:
                    classification = 'Severe wetness'
                    shading = white
                elif value_num > 1.99:
                    classification = 'Moderate wetness'
                    shading = white
                elif value_num > 0.99:
                    classification = 'Mild wetness'
                    shading = white
                elif value_num > 0.49:
                    classification = 'Incipient wetness'
                    shading = white
                elif value_num > -0.51:
                    classification = 'Normal'
                    shading = white
                elif value_num > -1.01:
                    classification = 'Incipient drought'
                    shading = lightred
                elif value_num > -2.01:
                    classification = 'Mild drought'
                    shading = lightred
                elif value_num > -3.01:
                    classification = 'Moderate drought'
                    shading = lightred
                elif value_num > -4.01:
                    classification = 'Severe drought'
                    shading = lightred
                elif value_num < -4:
                    classification = 'Extreme drought'
                    shading = lightred
                values_with_classes.append([value_num, classification, shading])
            output = values_with_classes[int(month)-1] + [pdsidv_file]
            if output[0] == -99.99:
                output = values_with_classes[int(month)-2] + [pdsidv_file]
                month = int(month) - 1
                if month < 1:
                    month = 12
                    year = int(year) - 1
                output[1] = "{} ({}-{:02d})".format(output[1], year, month)
            log.Wrap('   PDSI Value = {} - {}'.format(output[0], output[1]))
    except Exception:
        log.Wrap('      #---PDSI Not Available---#')
        log.Wrap(traceback.format_exc())
        log.Wrap('      #---PDSI Not Available---#')
        output = [-99.99, 'Not available', white, pdsidv_file]
    log.print_separator_line()
    log.Write('')
    return output

if __name__ == '__main__':
    palmer_value, palmer_class, palmer_color, pdsidv_file = get_pdsidv(lat=38.2753586,
                                                                       lon=-121.8237463,
                                                                       year='2019',
                                                                       month='6',
                                                                       pdsidv_file=None)
    print('palmer_value={}'.format(palmer_value))
    print('palmer_class={}'.format(palmer_class))
    print('palmer_color={}'.format(palmer_color))
    print('pdsidv_file={}'.format(pdsidv_file))

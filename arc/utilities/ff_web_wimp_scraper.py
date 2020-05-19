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
##      ff_web_wimp_scraper.py      ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-18   ##
##  ------------------------------- ##
######################################


# Import Standard Libraries
import os
import json
import time
import traceback
import requests
import datetime

# Import PIP Libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Import Custom Libraries
import JLog


# Start of function
lat = 38.5
lon = -121.5
"""
Queries WebWIMP:
The Web-based, Water-Budget, Interactive, Modeling Programworldwide elevation service by using
Selenium to operate the JavaScript form at "https://www.freemaptools.com/elevation-finder.htm"

Excerpt from ERDC/EL TR-08-28
Regional Supplement to the Corps of Engineers Wetland Delineation Manual
Arid West Region (Version 2.0)
Section 5 - Difficult Wetland Situations in the Arid West
Wetlands that periodically lack indicators of wetland hydrology:
    "...
    3. Use one or more of the following approaches to determine whether wetland
    hydrology is present and the site is a wetland. In the remarks section
    of the data form or in the delineation report, explain the rationale for
    concluding that wetland hydrology is present even though indicators of
    wetland hydrology described in Chapter 4 were not observed.
    a. Site visits during the dry season. Determine whether the site visit
    occurred during the normal annual dry season. The dry season, as
    used in this supplement, is the period of the year when soil moisture is
    normally being depleted and water tables are falling to low levels in
    response to decreased precipitation and/or increased evapotranspiration,
    usually during late spring and summer. It also includes the
    beginning of the recovery period in late summer or fall. The Web-
    Based Water-Budget Interactive Modeling Program (WebWIMP) is
    one source for approximate dates of wet and dry seasons for any
    terrestrial location based on average monthly precipitation and estimated
    evapotranspiration (http://climate.geog.udel.edu/~wimp/). In general, the
    dry season in a typical year is indicated when potential evapotranspiration
    exceeds precipitation (indicated by negative values of DIFF in the
    WebWIMP output), resulting in drawdown of soil moisture storage
    (negative values of DST) and/or a moisture deficit (positive values of
    DEF, also called the unmet atmospheric demand for moisture). Actual
    dates for the dry season vary by locale and year.
    ..."   
"""
log = JLog.PrintLog()
url = "http://climate.geog.udel.edu/~wimp/index.html"
# Locate Chrome Binary
module_path = os.path.dirname(os.path.realpath(__file__))
firefoxDriverPath = "{}\\webDrivers\\FireFox\\geckodriver.exe".format(module_path)
chrome_driver_path = "{}\\webDrivers\\Chrome\\chromedriver.exe".format(module_path)
# Create Options object and set automation options
profile = webdriver.FirefoxProfile()
##chrome_options = webdriver.ChromeOptions()
##chrome_options.add_argument('--disable-extensions')
##chrome_options.add_argument('--no-sandbox')
##chrome_options.add_argument('--headless')
# Create driver object
#driver = webdriver.Chrome(chrome_driver_path, chrome_options=chrome_options)
profile.set_preference("devtools.jsonview.enabled", False)



binary_argument = FirefoxBinary(r"C:\Users\L2RCSJ9D\AppData\Local\Mozilla Firefox\firefox.exe")
capabilities_argument = DesiredCapabilities().FIREFOX
capabilities_argument["marionette"] = False
driver = webdriver.Firefox(firefox_profile=profile, executable_path=firefoxDriverPath, capabilities=capabilities_argument)


#tries = 1
##while tries < 10:
##    try:
##        tries += 1


# Open Page
driver.get(url)
# Time buffer (Occasionally helps fewer warning messages post, but not mandatory)
time.sleep(.1)
# Get Project Title input Box
title_element = driver.find_element('name', 'yname')
# Type Current Date in Input Box
current_date = datetime.datetime.now()
current_date_string = current_date.strftime("%Y-%m-%d")
title_string = 'ARC Request - {}'.format(current_date_string)
title_element.clear()
title_element.send_keys(title_string)
# Submit Project Title by pressing return key
title_element.send_keys(Keys.RETURN)
# Find Latitude input box, clear it, then type selected Latitude
lat_element = driver.find_element('name', 'lati')
lat_element.clear()
lat_element.send_keys("{}".format(lat))
# Find Longitude input box, clear it, then type selected longitude
lon_element = driver.find_element('name', 'long')
lon_element.clear()
lon_element.send_keys("{}".format(lon))
# Submit inputs by pressing return key
lon_element.send_keys(Keys.RETURN)
# Find "Calculate Monthly Water Balance" button

##driver.stop_client()
##driver.quit()
                        






### Get input element
##input_element = driver.find_element_by_id('locationSearchTextBox')
### Enter Lat/Lon Query
##input_element.send_keys('{}, {}'.format(lat, lon))
### Submit Query
##input_element.send_keys(Keys.RETURN)
### Collect All Divs (NO SELECTABLE IDs on PAGE)
##divs = driver.find_elements(By.XPATH, "//div")
### Search for text string ending with " feet" FORMAT: "1044.0 m / 3425.2 feet"
##for item in divs:
##    if item.text.endswith(" feet"):
##        try:
##            # Parse string for elevation FORMAT: "1044.0 m / 3425.2 feet"
##            middle_string = " m / "
##            middle_location = item.text.find(middle_string)
##            elevation_meters = float(item.text[:middle_location])
##            elevation_feet = float(item.text[(middle_location + len(middle_string)):-5])
##            # Close the browser window and the driver executable
##            driver.stop_client()
##            driver.quit()
##            if units == 'Feet':
##                return elevation_feet
##            else:
##                return elevation_meters
##        except:
##            log.Write(traceback.format_exc())
##            raise
##    except Exception:
##        print('Attempt {} failed'.format(tries-1))
##        # Time buffer (Occasionally helps fewer warning messages post, but not mandatory)
##        time.sleep(.1)


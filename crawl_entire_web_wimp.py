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
##     crawl_entire_web_wimp.py     ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-18   ##
##  ------------------------------- ##
######################################

"""
Cache all of WebWIMP data within USA
"""

# Import Standard Libraries
import os
import sys
import time

# Import 3rd Party Libraries
import ogr
import pandas

# Import Custom Libraries
try:
    from . import JLog
    from . import web_wimp_scraper
    from . import os_convenience
except Exception:
    import JLog
    import web_wimp_scraper
    import os_convenience

def generate_usa_points():
    # Locate webWIMP_Cache folder and 
    utilities_path = os.path.dirname(os.path.realpath(__file__))
    python_scripts_path = os.path.dirname(utilities_path)
    root_path = os.path.dirname(python_scripts_path)
    wimp_cache_folder = '{}\\cached\\WebWIMP'.format(root_path)
    os_convenience.ensure_dir(wimp_cache_folder)
    # Generate CSV path
    csv_path = '{}\\USA_Coordinates.csv'.format(wimp_cache_folder)
    # Find USA Boundary Shapefile
    usa_shapefile_path = '{}\\us_shp\\cb_2018_us_nation_5m.shp'.format(root_path)
    # Get all latitudes within USA overall extent at 0.1 resolution
    print('Generating list of all latitudes within USA overall extent...')
    us_extent_lats = []
    lat = 71.4
    while lat > -14.4:
        us_extent_lats.append(round(lat, 1))
        lat -= 0.1
    # Get all longitudes within USA overall extent at 0.1 resolution
    print('Generating list of all longitudes within USA overall extent...')
    us_extent_lons = []
    lon = -179.2
    while lon < 179.9:
        us_extent_lons.append(round(lon, 1))
        lon += 0.1
    # Get the contents of the USA Boundary Shapefile
    ds_in = ogr.Open(usa_shapefile_path)
    # Get the shapefile's first layer
    lyr_in = ds_in.GetLayer()
    # Select USA Multi-Geometry Feature
    # Check if point is within boundary
    for feat_in in lyr_in:
        feat_in_geom = feat_in.geometry()
    # Keep only coordinates which fall within USA Boundaries
    print('Creating list of Coordinates within the USA at 0.1 resolution...')
    usa_points = []
    with open(csv_path, 'w') as csv:
        csv.write('lat,lon\n')
        sys.stdout.flush()
        for lat in us_extent_lats:
            for lon in us_extent_lons:
                # Create a point
                pt = ogr.Geometry(ogr.wkbPoint)
                pt.SetPoint_2D(0, lon, lat)
                # Test point
                contains_point = feat_in_geom.Contains(pt)
                if contains_point:
                    usa_points.append((lat, lon))
                    csv.write('{},{}\n'.format(lat, lon))
                    sys.stdout.flush()
    print('All USA coordinates found.')
    return usa_points

def get_usa_points():
    # Locate webWIMP_Cache folder and 
    utilities_path = os.path.dirname(os.path.realpath(__file__))
    python_scripts_path = os.path.dirname(utilities_path)
    root_path = os.path.dirname(python_scripts_path)
    wimp_cache_folder = '{}\\cached\\WebWIMP'.format(root_path)
    os_convenience.ensure_dir(wimp_cache_folder)
    # Generate CSV path
    csv_path = '{}\\USA_Coordinates.csv'.format(wimp_cache_folder)
    # check for CSV
    csv_exists = os.path.exists(csv_path)
    if csv_exists is False:
        # Generate CSV and points if they don't exist
        usa_points = generate_usa_points()
        return usa_points
    else:
        # Create a pandas dataframe from csv
        df = pandas.read_csv(csv_path, delimiter=',')
        # Create a list of tuples from dataframe rows
        usa_points = [tuple(row) for row in df.values]
        return usa_points

def web_crawl_web_wimp():
    # Locate webWIMP_Cache folder and 
    utilities_path = os.path.dirname(os.path.realpath(__file__))
    python_scripts_path = os.path.dirname(utilities_path)
    root_path = os.path.dirname(python_scripts_path)
    wimp_cache_folder = '{}\\cached\\WebWIMP'.format(root_path)
    # Get USA Points at 0.1 resolution
    usa_points = get_usa_points()
#    # Change Starting Point
#    usa_points = usa_points[:31700]
#    # flip points
#    flipped_points = []
#    for x in range(len(usa_points)):
#        x += 1
#        flipped_points.append(usa_points[-x])
#    usa_points = flipped_points
    # Save ouput for each USA Point
    wimp_scraper = web_wimp_scraper.WimpScraper(watershed_analysis=True)
    wimp_scraper.batch(usa_points,
                       write_dictionary=True)
    print('All complete...')
    time.sleep(5)


if __name__ == '__main__':
    web_crawl_web_wimp()

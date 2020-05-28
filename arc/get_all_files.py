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
##         get_all_files.py         ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

import os

try:
    from . import get_files
except Exception:
    import get_files

def ensure_wbd_exists():
    # Find Selected WBD shapefile
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    wbd_folder = u'{}\\GIS\\WBD'.format(root_folder)
    shapefile = '{}\\HUC2.shp'.format(wbd_folder)
    exists = os.path.exists(shapefile)
    if not exists:
        # Calculate url and paths
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/WBD/HUC2.zip'
        local_file_path = u'{}\\GIS\\HUC2.zip'.format(root_folder)
        # Download & Extract
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=wbd_folder)

def ensure_climdiv_exists():
    # Find Selected WBD shapefile
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    climdiv_folder = u'{}\\GIS\\climdiv'.format(root_folder)
    shapefile = '{}\\GIS.OFFICIAL_CLIM_DIVISIONS.shp'.format(climdiv_folder)
    exists = os.path.exists(shapefile)
    if not exists:
        # Calculate url and paths
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/climdiv/GIS.OFFICIAL_CLIM_DIVISIONS.zip'
        local_file_path = u'{}\\GIS\\GIS.OFFICIAL_CLIM_DIVISIONS.zip'.format(root_folder)
        # Download & Extract
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=climdiv_folder)

def ensure_us_shp_exists():
    # Find Selected WBD shapefile
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    us_shp_folder = u'{}\\GIS\\us_shp'.format(root_folder)
    shapefile = '{}\\cb_2018_us_nation_5m.shp'.format(us_shp_folder)
    exists = os.path.exists(shapefile)
    if not exists:
        # Calculate url and paths
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/us_shp/cb_2018_us_nation_5m.zip'
        local_file_path = u'{}\\GIS\\cb_2018_us_nation_5m.zip'.format(root_folder)
        # Download & Extract
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=us_shp_folder)

def ensure_wimp_pickle():
    # Find Selected WBD shapefile
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    us_shp_folder = u'{}\\cached'.format(root_folder)
    pickle_file = '{}\\wimp_dict.pickle'.format(us_shp_folder)
    exists = os.path.exists(pickle_file)
    if not exists:
        # Calculate url and paths
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/cached/wimp_dict.zip'
        local_file_path = u'{}\\cached\\wimp_dict.zip'.format(root_folder)
        # Download & Extract
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=us_shp_folder)

def ensure_package(launch_downloader=False):
    # Calculate Paths
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\versions\\ARC_Innards.zip'.format(root_folder)
    try:
        os.remove(local_file_path)
    except Exception:
        pass
    file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/package/ARC_Innards.zip'
    local_version_file = '{}\\versions\\package_version.txt'.format(root_folder)
    web_version_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/package/package_version.txt'
    # Download & Extract
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file,
                                     extract_path=root_folder,
                                     launch_downloader=launch_downloader)

def ensure_arc_exe(launch_downloader=False):
    # Calculate Paths
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\versions\\arc_ex.zip'.format(root_folder)
    try:
        os.remove(local_file_path)
    except Exception:
        pass
    file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/core/arc_ex.zip'
    local_version_file = '{}\\versions\\arc_ex_version.txt'.format(root_folder)
    web_version_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/core/arc_ex_version.txt'
    # Download & Extract
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file,
                                     extract_path=root_folder,
                                     extract_pwd='1234',
                                     launch_downloader=launch_downloader)

def downloader():
    ensure_package()
    ensure_arc_exe()
    ensure_wbd_exists()
    ensure_climdiv_exists()
    ensure_us_shp_exists()
    ensure_wimp_pickle()

def main():
    ensure_package(launch_downloader=True)
    ensure_arc_exe(launch_downloader=True)
    ensure_wbd_exists()
    ensure_climdiv_exists()
    ensure_us_shp_exists()
    ensure_wimp_pickle()


if __name__ == '__main__':
    main()

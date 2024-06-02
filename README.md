Script to create a custom airspace file for FlySkyHy.

The custom airspace is used to identify:
 - Landing Zones
 - Do Not Land areas
 - Seasonal raptor closure areas
 - Thermal hot spots (extracts from https://thermal.kk7.ch)

See the header for the custom airspace text file for info on updating FlySkyHy airspace settings.

# Development Information
This script was developed in Microsoft Visual Studio Code on Windows using Python 3.10.11 
(although the script is pretty basic; any recent version of Python is likely to work fine).

This script uses the following libraries that may need to be installed via pip:
 - shutil
 - pathlib
 - lxml

The script has variables to specify the source, archive, and destination file locations.  These will need to be changed for your file location.

# Creating a source file for thermal hot spots
To extract thermal hot spots from https://thermal.kk7.ch:
 - Pan/zoom until the area you want to extract is visible on the screen
 - Change settings (upper right corner) to disable thermals and show hotspots (not necessary, but helpful to see what will be extracted)
 - Click Downloads (top center of screen)
 - Scroll down to "Download Hotspots"
 - From the "Download currently visible hotspots" dropdown, select "GPS Exchange format (GPX)

# Creating a source file for LZ/DNL areas
To create a polygon for a LZ/DNL area:
 - Open Google Earth Pro
 - Pan/zoom to the desired area
 - From the menu, select Add --> Polygon
 - Name the LZ/DNL; make sure the name contains "DNL" if it should be created as a DNL airspace
 - Click on the corners to outline the LZ/DNL area
 - Click 'Ok' on the Polygon pop up.
 - From the Places listing on the left, right click on the new LZ/DNL
 - Click on 'Save Place As'
 - Change the type to '.kml'
 - Click Save

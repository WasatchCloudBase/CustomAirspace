# Convert files into custom airspaces (OpenAir airspace format) for FlySkyHy
# Supports the following types of files:
#    - Google earth places (polygons) .kml files
#    - thermal.kk7.ch hot spots (center points) .gpx files

import shutil                            # for file copy/delete functions
from pathlib import Path                 # for file directory functions
from lxml import etree                   # for XML functions

# Set paths
dest_dir = Path('/users/mikbrown/documents/coding/CustomAirspace')
source_dir = Path('/users/mikbrown/documents/coding/CustomAirspace/datafiles')
archive_dir = Path('/users/mikbrown/documents/coding/CustomAirspace/datafiles/archive')

# Open destination file
dest_file = open(dest_dir / 'custom airspace.txt', mode='a')

# Set factors for thermal hot spot octagon and airspace
scale_factor = .004
x_proportion = 1.2
high_probability_minimum = 80

# Function to create thermal hot spot coordinates for one of the octagon corners 
def thermal_hot_spot_coordinates (lat_center, lon_center, lat_offset, lon_offset):
    lat_coord = lat_center + (scale_factor * lat_offset)
    lon_coord = lon_center + (scale_factor * x_proportion * lon_offset)
    return str(lat_coord) + ' N ' + str(lon_coord) + ' W'

print('')
print('Starting processing')
print('-------------------')

# Process each source file
for source_file_listing in source_dir.iterdir():
    if Path.is_file(source_file_listing):

        print('Found file: ' + source_file_listing.name)

        # Clear data between files
        name = ''
        airspace_type = ''
        coordinates_data = ''
        coordinates_list = []
        coordinates = ''
        coord_component_list = []
        OpenAir_coordinates_list = []
        Supported_file = False

        #------------------------------------------------------------------------------------
        # Process kml files (LZ and DNL areas)
        #------------------------------------------------------------------------------------
        if source_file_listing.suffix == '.kml':
            Supported_file = True
   
            # Build XML tree of file contents
            root = etree.parse(source_file_listing)

            # Process LZs/DNLs from kml files based on a child of <Placemark>
            # Google Earth extract files specify a namespace of kml, so need to include namespace to find nodes correctly
            nsmap = {"kml": "http://www.opengis.net/kml/2.2"}
            placemarks = root.xpath(".//kml:Placemark", namespaces=nsmap)
            for placemark in placemarks:

                # Clear data between records
                name = ''
                airspace_type = ''
                coordinates_data = ''
                coordinates_list = []
                coordinates = ''
                coord_component_list = []
                OpenAir_coordinates_list = []

                # Find the 'name' node for the placemark
                names = placemark.xpath(".//kml:name", namespaces=nsmap)
                for name_node in names:
                    name = name_node.text

                    # Strip .kml and any quotes from name if needed
                    name = name.replace('.kml','')
                    name = name.replace("&apos;","")
                    name = name.replace('&quot;','')

                    # Set airspace type depending whether an LZ or DNL field
                    airspace_type = 'W'
                    if 'DNL' in name:
                        airspace_type = 'R'

                # Find 'coordinates' node for the placement and parse polygon coordinates
                coordinates = placemark.xpath(".//kml:coordinates", namespaces=nsmap)
                for coordinates_node in coordinates:
                    coordinates_data = coordinates_node.text.strip()
           
                # Create list of polygon coordinate data sets (three coordinates in each set) delimited by ' '
                coordinates_list = coordinates_data.split(' ')
           
                # Process each set of coordinates
                for coordinates in coordinates_list:

                    # Remove '-' from West coordinates
                    coordinates = coordinates.replace('-','')
               
                    # Strip extra characters from coordinates
                    coordinates = coordinates.replace('\n','')
                    coordinates = coordinates.replace('\t','')
               
                    # Split each coordinate data set into list of coordinate components
                    coord_component_list = coordinates.split(',')

                    # Transform to OpenAir format if not an empty coordinate row
                    if not coord_component_list[0] == '': 
                        OpenAir_coordinates = coord_component_list[1] + ' N ' + coord_component_list[0] + ' W'

                    # Add to OpenAir coordinate list
                    OpenAir_coordinates_list.append(OpenAir_coordinates)

                # Write OpenAir format if there is a name and coordinates
                if not name == '' and not OpenAir_coordinates_list[0] == '':
           
                    # Write airspace type, name, and altitude rows
                    dest_file.write('AC ' + airspace_type + '\n')
                    dest_file.write('AN ' + name + '\n')
                    dest_file.write('AL SFC' + '\n')
                    dest_file.write('AH 10 AGL' + '\n')
           
                    #Write coordinates
                    for OpenAir_coordinates in OpenAir_coordinates_list:
                        dest_file.write('DP ' + OpenAir_coordinates + '\n')
           
                    # Write spacing row
                    dest_file.write('*' + '\n')

                    print('Airspace added for LZ/DNL area: ' + name)

            # Archive source file
            archive_file_name = str(archive_dir) + '\\' + source_file_listing.name
            shutil.move(source_file_listing, archive_file_name)

        #------------------------------------------------------------------------------------
        # Process gpx files (Thermal hot spots)
        #------------------------------------------------------------------------------------
        if source_file_listing.suffix == '.gpx':
            Supported_file = True

            print('found gpx file')

            # Build XML tree of file contents
            root = etree.parse(source_file_listing)

            # Process thermal hot spots from gpx files based on a child of <wpt>
            # kk7 extract files specify a namespace of gpx, so need to include namespace to find nodes correctly
            nsmap = {"gpx": "http://www.topografix.com/GPX/1/1"}
            hotspots = root.xpath(".//gpx:wpt", namespaces=nsmap)
            for hotspot in hotspots:

                # Clear data between records
                name = ''
                airspace_type = ''
                coordinates_data = ''
                coordinates_list = []
                coordinates = ''
                coord_component_list = []
                OpenAir_coordinates_list = []

                # Find the 'ele' node for the thermal hot spot
                # (ele appears to be unique across kk7; name is only unique within a given hot spot extract)
                elements = hotspot.xpath(".//gpx:ele", namespaces=nsmap)
                for element_node in elements:
                    name = element_node.text

                    # Strip .kml and any quotes from name if needed
                    name = name.replace('.wpt','')
                    name = name.replace("&apos;","")
                    name = name.replace('&quot;','')

                # Find the 'cmt' node for thermal strength ('probability'; there is also 'importance' that could be used)
                comments = hotspot.xpath(".//gpx:cmt", namespaces=nsmap)
                for comment_node in comments:
                    comment = comment_node.text
                    # Remove everying starting at '%'
                    comment = comment.partition("%")[0]
                    # Remove everying up through ':' and convert to integer
                    thermal_probability = int(comment.partition(":")[2])

                    # Set airspace to 'AWY' for high probability and TMZ for low probability
                    airspace_type = 'AWY'
                    if thermal_probability <  high_probability_minimum:
                        airspace_type = 'TMZ'

                # Set center of thermal hot spot
                lat_center_string = hotspot.get('lat')
                lon_center_string = hotspot.get('lon')

                # Remove '-' from coordinates and convert to floating numbers
                lat_center = float(lat_center_string.replace('-',''))
                lon_center = float(lon_center_string.replace('-',''))

                # Build coordinates for each corner of an octagon around the thermal hot spot center
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center,      1,  0.414))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center,  0.414,      1))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center, -0.414,      1))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center,     -1,  0.414))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center,     -1, -0.414))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center, -0.414,     -1))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center,  0.414,     -1))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center,      1, -0.414))
                OpenAir_coordinates_list.append(thermal_hot_spot_coordinates(lat_center, lon_center,      1,  0.414))

                # Write OpenAir format if there is a name and coordinates
                if not name == '' and not OpenAir_coordinates_list[0] == '':
           
                    # Write airspace type, name, and altitude rows
                    dest_file.write('AC ' + airspace_type + '\n')
                    dest_file.write('AN ' + name + '\n')
                    dest_file.write('AL SFC' + '\n')
                    dest_file.write('AH 10 AGL' + '\n')
           
                    #Write coordinates
                    for OpenAir_coordinates in OpenAir_coordinates_list:
                        dest_file.write('DP ' + OpenAir_coordinates + '\n')
           
                    # Write spacing row
                    dest_file.write('*' + '\n')

                    print('Airspace added for thermal hot spot: ' + name)

            # Archive source file
            archive_file_name = str(archive_dir) + '\\' + source_file_listing.name
            shutil.move(source_file_listing, archive_file_name)
        
        if not Supported_file:
            print('Unsupported file type not processed: ' + source_file_listing.name)
        # End check of source file type

    # End check if file is found
       
# Close destination file
dest_file.close()

print ('-------------------')
print ('Processing complete')


# Google earth places .kml conversion to OpenAir airspace format

from pathlib import Path
import shutil

# Set paths
dest_dir = Path('/users/mikbrown/documents/coding/CustomAirspace')
source_dir = Path('/users/mikbrown/documents/coding/CustomAirspace/kml')
archive_dir = Path('/users/mikbrown/documents/coding/CustomAirspace/kml/archive')

# Open destination file
dest_file = open(dest_dir / 'custom airspace.txt', mode='a')

print('')
print('Starting processing')
print('-------------------')

# Process each source file
for source_file_listing in source_dir.iterdir():
    if Path.is_file(source_file_listing):
       
       # Skip non-KML files 
       if '.kml' not in source_file_listing.name:
           print('Non-KML file not processed: ' + source_file_listing.name)
       else:
               
           # Make sure all variables are cleared for new file
           name = ''
           airspace_type = ''
           coordinates_data = ''
           coordinates_list = []
           coordinates = ''
           coord_component_list = []
           OpenAir_coordinates_list = []
       
           # Read new file contents
           # Assumes one airspace per file
           source_file = open(source_file_listing, 'r')
           source_line = source_file.read()
           
           # Find object name
           if '<name>' in source_line:
               name = source_line[source_line.find('<name>')+6:source_line.find('</name>')]

               # Strip .kml and any quotes from name if needed
               name = name.replace('.kml','')
               name = name.replace("&apos;","")
               name = name.replace('&quot;','')
           
           # Set airspace type depending whether an LZ or DNL field
           airspace_type = 'W'
           if 'DNL' in name:
               airspace_type = 'R'

           # Parse polygon coordinates
           if '<coordinates>' in source_line:
               coordinates_data = source_line[source_line.find('<coordinates>')+13:source_line.find('</coordinates>')]
           
           # Create list of polygon coordinate data delimited by ' '
           coordinates_list = coordinates_data.split(' ')
           
           # Process each set of coordinates
           for coordinates in coordinates_list:

               # Remove '-' from West coordinates
               coordinates = coordinates.replace('-','')
               
               # Strip extra characters from coordinates
               coordinates = coordinates.replace('\n','')
               coordinates = coordinates.replace('\t','')
               
               # Create list of coordinate components
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

               print('Airspace added for: ' + name)

           # Close and archive source file
           source_file.close()
           archive_file_name = str(archive_dir) + '\\' + source_file_listing.name
           shutil.move(source_file_listing, archive_file_name)

     # End check of source file type (process only .kml files)
           
# Close destination file
dest_file.close()

print ('-------------------')
print ('Processing complete')


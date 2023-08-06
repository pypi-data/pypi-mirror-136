
# Sasdbpy

This is a simple helper class to read and use data stored in sas7bdat format, without having Sas.

This code will help you:

- explore a folder and identify all sas7bdat present therein
- have them organized in a python dictionary with, for each file:
    - the data as a pandas Dataframe
    - a field name mapper from the coded field name to the description from the meta data
    - a more detailed fields characteristics dataframe with information of Type, Length, Format
- Two search functions on the field names:
    - search_field, to identify fields from the database containing a certain string
    - search_field_description, to reverse search fields from a string contained in their description

# Usage

```
from sasdbpy.sasdbreader import SasDbReader
sdb = SasDbReader("[the folder path with the sas files]")

# get list of tables found
list_tables = list(sdb.res_data.keys())

#get the dataframe for one of the tables
table_name = list_tables[0]
df = sbd.res_data[table_name]['data']

#get field description map
sdb.res_data[table_name]['detail_fields']

# search for a field in the whole database
sdb.search_field('USERID')
# with information on the table where it sits
sdb.search_field('USERID', location=True)

# reverse search
sdb.search_field_description('identity')

```
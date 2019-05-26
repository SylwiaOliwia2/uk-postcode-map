uk-postcode-map
===============

The map shows how many percent of "feed-in tariff" ([FIT](https://www.ofgem.gov.uk/environmental-programmes/fit/contacts-guidance-and-resources/public-reports-and-data-fit/installation-reports)) 
panels was put on the Open Street Map (OSM) for UK. It was initially created for [OpenClimateFix](http://openclimatefix.discourse.group/) 
contributors to indicate which [postcode districts](https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom#Formatting) 
lack information about solar panels location. 

# How to use
To see the map, open the _frontend/mapbox_uk.html_ file in the browser.

To get the newest data form OSM about the amount of solar panels in the UK postcode areas,type in the console:
 
`python data_preprocessing/calculate_stats_for_postcodes.py`

The final data will be saved in _frontend/postcodes_updated.json_. The intermediate files (containing raw query results) will 
be saved in _data_preprocessing/data_.

The optional parameters for `calculate_stats_for_postcodes` (useful when updating only FIT data and by debuging):
* `--osm_from_pickle` – instead of querying solar panels coordinates from OSM, use already saved data from the recent search
* `--osm_postcodes_from_json` – instead of querying postcode for each solar panel from OSM, use already saved results from 
the recent search

To use th newest FIT data – download the latest files [here](https://www.ofgem.gov.uk/environmental-programmes/fit/contacts-guidance-and-resources/public-reports-and-data-fit/installation-reports) 
and update them manually according to _Methodology_ section.
 
# Metodology
## FIT data
The FIT data used on the map come from [this website](https://www.ofgem.gov.uk/publications-and-updates/feed-tariff-installation-report-31-march-2019). 
Each of the three files was manually pivoted (count for each _Installation Postcode_), filtered (_Technology=Photovoltaic_) and saved in _data_preprocessing/UK_Installed_pannels_ as **csv**, with two columns:
* first - postcode dictrict names.
* second - count of panels with given postcode 

There are **~850k** photovoltaic records in total; **14k** of them (**2%**) with postal code _UNKNOWN_. The FIT files can be 
manually updated, accordingly to the specification above (unfortunately python crashed to open original _xlsx_ files 
containing images).

##Solar Pannels in OSM
The information about amount of solar panels provided for each postcode is retrieved in two steps:
1. Solar panels are queried from OSM via overpass api. 
2. The closest postcode is queried for each solar panel via postcodes.io api

Then the statistics about number of solar panels are created. Panels are saved in OSM map in two formats - nodes (single point) 
and ways (area). To simplify, both single node and single way was assumed to be one solar panel.

## Geolocations
The original file with postcode coordinates was downloaded from [here](https://random.dev.openstreetmap.org/postcode_shapes/) (_postcode-XXNN.* files_). 
The file was preprocessed:
1. Postcode shapes were simplified with _Mapshaper_ asd saved as _shp_
2. Original file was lacking several postcodes, which were manually added.
3. File was saved as geojson: _data_preprocessing/data/postcodes.json_.

# TODO:
* **read geojson file from _frontend_ folder (currently the map is loaded from external link in _mapbox_uk.html_)**. 
* Add missing postcodes to geojson (they disappeared due to postcode shapes simplification): 
BN42, CF47, CH47, DA18, DT1, FY2, G34, GL1, XH1, OX28, PE35, PL31, TA15, TF5, TN1, TN10
* automate downloading and preprocessing FIT data
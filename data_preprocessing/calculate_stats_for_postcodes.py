import argparse
import json
import functions_panels_amount

###### Parse arguments
parser = argparse.ArgumentParser(description='Optionally provide query parameters')
parser.add_argument("--osm_form_pickle", help="load OSM panels coordinates from file instead of querying OSM",
                    action="store_true")
parser.add_argument("--osm_postcodes_from_json", help="load panels per postcodes from file instead of querying API",
                    action="store_true")
args = parser.parse_args()

# Calculate number of panels installed per Outward postcode	(dictrict)
# Details about post code dictrict: https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom#Formatting
panels_federal_data_aggr_json = json.loads(functions_panels_amount.panelsFromFederalData())
panels_from_OSM_raw = functions_panels_amount.getSolarPanelsFromOSM(osm_form_pickle=args.osm_form_pickle)
panels_from_OSM_aggr_json = functions_panels_amount.getPostCodesOSMPannels(panels_from_OSM_raw,
                                                                           osm_postcodes_from_json=args.osm_postcodes_from_json)
functions_panels_amount.savePanelsPerPostcode(panels_federal_data_aggr_json, panels_from_OSM_aggr_json)

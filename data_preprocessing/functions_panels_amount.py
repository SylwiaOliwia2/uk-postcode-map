import os
import codecs
import pandas as pd
import requests
import collections
import re
import json
import pickle

'''
Funcions used to calculate number and percentage of solar pannels already provided to OpenStreetMap
'''

def panelsFromFederalData(folder_with_input_files='UK_Installed_pannels', folder_with_output_files='data'):
    '''
    Aggregate number of installed panels per postcode district form folder "UK_Installed_pannels".
    The files in the folder were preciously manually aggregated from federal data: https://www.ofgem.gov.uk/publications-and-updates/feed-tariff-installation-report-31-march-2019 and saved as csv
    #TODO: automate creating CSV files (currently done manually in excel)
    Each file (csv) must have the following columns:
    - Installation Postcode: postcodes,
    - Count - Technology: total number of panels for given postcode
    !!! When creating pivot in excel, only technology=photovoltaics should be used

    :param folder_with_input_files: name of the folder with preprocessed federal data (stored as multiple CSV).
            Name without the path. Folder should be located in the same directory as functions_panels_amount file.
    :param folder_with_output_files: folder where output file should be stored. Name without the path.
            Folder should be located in the same directory as functions_panels_amount file.
    :return:
    '''

    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, folder_with_input_files)

    post_code_stats_files = [filename for filename in os.listdir(folder) if filename.endswith(".csv")]

    # preprocess data from each CSV file
    installed_panels_locations = []
    for n, file in enumerate(post_code_stats_files):
        panels_per_minor_postcode = pd.read_csv(folder + "/" + file, header=0, index_col=0).reset_index()
        # cut unnecessary details about the post code
        panels_per_minor_postcode.ix[:, 0] = panels_per_minor_postcode.ix[:, 0].str.strip().str.upper().replace(to_replace=r'\s.*', value='', regex=True).str.strip()
        panels_per_major_postcode = panels_per_minor_postcode.pivot_table(index=panels_per_minor_postcode.columns[0]
                                                                          , values=panels_per_minor_postcode.columns[1]
                                                                          , aggfunc='sum')
        installed_panels_locations.append(panels_per_major_postcode)

    # merge data from each CSV file
    number_of_panels = pd.concat(installed_panels_locations, axis=1, sort=True).fillna(0).astype(int).sum(axis=1)
    return number_of_panels.to_json()


def getSolarPanelsFromOSM(osm_form_pickle=False, folder_with_output_files='data', picklename="residential_panels"):
    '''
    Query OpenStreetMap to get all solar pannels within a country. Optionally - load pickled data
    :param osm_form_pickle: bool, if Solar Panels data should be loaded from pickle instead of querying from OSM.
            data from pickle are faster, but may be outdated. Should be used for development purposes or when unable to query OSM
    :param folder_with_output_files: name of the folder with preprocessed federal data (stored as multiple CSV).
            Name without the path. Folder should be located in the same directory as functions_panels_amount file.
    :param picklename: filename where data will be pickled
    :return: json with node coordinates
    '''
    dirname = os.path.dirname(__file__)

    if osm_form_pickle:
        # TODO: if no pickled data in folder- query OSM
        with open(os.path.join(dirname, folder_with_output_files, "residential_panels.pkl"), 'rb') as f:
            osm_queried_panels = pickle.load(f)
    else:
        overpass_url = "http://overpass-api.de/api/interpreter"

        ######### query all solar panels saved as polygon
        solar_ways_query = """
            [out:json];
            area["name"="United Kingdom"]->.searchArea;
            (way(area.searchArea)["generator:source"="solar"];
            );
            out body;
            >;
            out skel qt;
        """
        ways_solar = requests.get(overpass_url, params={'data': solar_ways_query}).json()

        # to simplify, one polygon will be represented as one panel
        # the panel will get coordinates of the first node of polygon
        first_node_ids = [element["nodes"][0] for element in ways_solar["elements"] if element["type"] == "way"]
        panels_from_polygon = [element for element in ways_solar["elements"] if element["id"] in first_node_ids]

        ######### query all solar panels saved as points (nodes)
        solar_nodes_query = """
            [out:json];
            area["name"="United Kingdom"]->.searchArea;
            (
             node(area.searchArea)["generator:source"="solar"];
            );
            out body;
            >;
            out skel qt;
        """
        panels_from_nodes = requests.get(overpass_url, params={'data': solar_nodes_query}).json()

        osm_queried_panels = panels_from_nodes["elements"] + panels_from_polygon

        with open(os.path.join(dirname, folder_with_output_files, picklename + ".pkl"), 'wb') as f:
            pickle.dump(osm_queried_panels, f)

    return osm_queried_panels


def getPostCodesOSMPannels(osm_queried_panels, osm_postcodes_from_json=False, radius=10000, folder_with_output_files='data'):
    '''
    Get post codes of Solar Panels from OSM
    :param osm_queried_panels: json with SolarPanels location from OSM
    :param radius: the max distance to find post code to the same post code
    :param folder_with_output_files: name of the folder with preprocessed federal data (stored as multiple CSV).
            Name without the path. Folder should be located in the same directory as functions_panels_amount file.
    :param osm_postcodes_from_json: bool, if post codes for Solar Panels should be loaded from json instead of querying the api
    :return: post codes and amount of Solar panels within it (json)
    '''
    dirname = os.path.dirname(__file__)

    if osm_postcodes_from_json:
        # TODO: if no pickled data in folder- query api.postcodes.io
        post_codes_frequency = pd.read_json(os.path.join(dirname, folder_with_output_files, "OSM_panels.json"), typ='series')
    else:

        json_parameters = [{"latitude": panel["lat"], "longitude": panel["lon"], "radius": radius, "limit": 1}
                           for panel in osm_queried_panels]
        post_codes = []
        #not_post_codes = []  # to check if any panels hawe no postcodes within radius. For 1000m there arte 140 Unknown (no postal code within 1000m) which is acceptable
        ## use api to request post codes
        for n in range(0, len(osm_queried_panels), 100):
            json_subset = json_parameters[n:n + 100]
            post_response = requests.post("https://api.postcodes.io/postcodes", json={"geolocations": json_subset}).json()
            post_codes = post_codes + [x["result"][0]["outcode"] for x in post_response["result"] if x["result"]]
        #not_post_codes = not_post_codes + [x for x in post_response["result"] if not x["result"]]
        post_codes_major = [re.sub(r"\s.*", "", p.upper().strip()) for p in post_codes]
        post_codes_frequency = dict(collections.Counter(post_codes_major))

        # save to json
        with open(os.path.join(dirname, folder_with_output_files, "OSM_panels.json"), 'w') as fp:
            json.dump(post_codes_frequency, fp)

    return post_codes_frequency


def summaryPanelsPerPostcode(panels_federal_data_aggr_json, panels_from_OSM_aggr_json, folder_with_output_files='data'):
    '''
    :param panels_federal_data_aggr_json: aggregated statistics of installed panels per postcode (from federal data)
    :param panels_from_OSM_aggr_json: aggregated statistics of installed panels per postcode (from OSM)
    :param folder_with_output_files: older_with_output_files: name of the folder with preprocessed federal data (stored as multiple CSV).
            Name without the path. Folder should be located in the same directory as functions_panels_amount file.
    :return: save stats to json file
    '''
    dirname = os.path.dirname(__file__)

    # Calculate statistics for panels placed on OSM map
    nominal = {key: panels_from_OSM_aggr_json.get(key, 0) for key in panels_federal_data_aggr_json.keys()}
    percent = {key: nominal[key] / panels_federal_data_aggr_json[key] * 100 for key in panels_federal_data_aggr_json.keys()}
    panels_plotted_on_OSM = {"nominal": {k: int(v) for k, v in nominal.items()}, "percent": percent}

    # TODO: Deal with UNKNOWN in UK_installed_panels_summary ?
    with open(os.path.join(dirname, folder_with_output_files, "panels_stats.json"), 'w') as fp:
        json.dump(panels_plotted_on_OSM, fp)
    return panels_plotted_on_OSM


def updateSaveGeojson(panels_plotted_on_OSM):

    dirname = os.path.dirname(__file__)
    postcodes_frequency = json.load(codecs.open(os.path.join(dirname, "data", "postcodes.json"), 'r', 'utf-8-sig'))

    for n, f in enumerate(postcodes_frequency["features"]):
        postcode = f["properties"]["name"]
        try:
            postcodes_frequency["features"][n]["properties"]["value_nominal"] = panels_plotted_on_OSM["nominal"][postcode]
            postcodes_frequency["features"][n]["properties"]["value_percent"] = panels_plotted_on_OSM["percent"][postcode]
        except:
            postcodes_frequency["features"][n]["properties"]["value_nominal"] = 0
            postcodes_frequency["features"][n]["properties"]["value_percent"] = 0

    with open(os.path.join(dirname, "..", "frontend", "postcodes_updated.json"), 'w') as fp:
        json.dump(postcodes_frequency, fp)


if __name__ == '__main__':
    panelsFromFederalData()
    getSolarPanelsFromOSM()
    getPostCodesOSMPannels()
    summaryPanelsPerPostcode()
    updateSaveGeojson()
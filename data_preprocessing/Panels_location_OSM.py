import requests
import json
import os
import collections
overpass_url = "http://overpass-api.de/api/interpreter"

folder_with_output_files = 'data'
dirname = os.path.dirname(__file__)
###################################################################################################
## Get data of solar panels in the UK
###################################################################################################
# get information about all solar panels in UK, represented as WAYS
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

# get the first node of each way and use them as panel location
first_node_ids = [element["nodes"][0] for element in ways_solar["elements"] if element["type"] == "way"]
first_nodes_from_ways = [element for element in ways_solar["elements"] if element["id"] in first_node_ids]


# get information about all solar panels in UK, represented as NODES
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
nodes_solar = requests.get(overpass_url, params={'data': solar_nodes_query}).json()

residential_panels = nodes_solar["elements"] + first_nodes_from_ways

###################################################################################################
## Residential panels
###################################################################################################
radius = 10000
json_parameters = [{"latitude": panel["lat"], "longitude": panel["lon"], "radius": radius, "limit": 1}
                   for panel in residential_panels]

post_codes = []
## use api to request post codes
for n in range(0, len(residential_panels), 100):
    json_subset = json_parameters[n:n+100]
    port_response = requests.post("https://api.postcodes.io/postcodes", json={"geolocations": json_subset}).json()
    post_codes = post_codes + [x["result"][0]["outcode"] for x in port_response["result"] if x["result"]]
    not_post_codes = [x for x in port_response["result"] if not x["result"]]


### teraz dostań post codes+
post_url = "https://api.postcodes.io/postcodes"
port_response = requests.post(post_url,  json={"geolocations": json_parameters}).json()
post_codes = [x["result"][0]["outcode"] for x in port_response["result"] if x["result"]]
not_post_codes = [x for x in port_response["result"] if not x["result"]]
post_codes_frequency = dict(collections.Counter(post_codes))

post_codes_frequency.to_json( os.path.join(dirname, folder_with_output_files, "UK_OSM_pannels.json"))

#print(json.dumps(port_response["result"][0], indent=4, sort_keys=True))

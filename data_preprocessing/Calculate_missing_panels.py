import pandas as pd
import os
import json

folder_with_output_files = 'data'
dirname = os.path.dirname(__file__)

UK_installed_panels_summary = pd.read_json(os.path.join(dirname, folder_with_output_files, "UK_Installed_pannels_summary.json"), typ='series')
UK_OSM_panels = pd.read_json(os.path.join(dirname, folder_with_output_files, "UK_OSM_panels.json"), typ='series')

# Calculate statistics for panels not placed on OSM map
nominal = {key: UK_installed_panels_summary[key] - UK_OSM_panels.get(key, 0) for key in UK_installed_panels_summary.keys()}
percent = {key: nominal[key] / UK_installed_panels_summary[key] for key in UK_installed_panels_summary.keys()}
panels_not_plotted_on_OSM = {"nominal": {k: int(v) for k, v in nominal.items()}, "percent": percent}

#TODO: Deal with UNKNOWN in UK_installed_panels_summary ?
with open(os.path.join(dirname, folder_with_output_files, "panels_not_plotted_on_OSM.json"), 'w') as fp:
    json.dump(panels_not_plotted_on_OSM, fp)



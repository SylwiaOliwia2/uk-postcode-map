import os
import pandas as pd

folder_with_input_files = 'UK_Installed_pannels'
folder_with_output_files = 'data'

dirname = os.path.dirname(__file__)
folder = os.path.join(dirname, folder_with_input_files)
# source : https://www.ofgem.gov.uk/publications-and-updates/feed-tariff-installation-report-31-march-2019
# data preprocessed in excel(compuder crashed when tried to load xlsx file),pivot table with number of solar panels per post code
post_code_stats_files = [filename for filename in os.listdir(folder) if filename.endswith(".csv")]

installed_panels_locations = []
for n, file in enumerate(post_code_stats_files):
    panels_per_minor_postcode = pd.read_csv(folder + "/" + file, header=0, index_col=0).reset_index()
    panels_per_minor_postcode.ix[:, 0] = panels_per_minor_postcode.ix[:, 0].str.upper().replace(to_replace=r'\d.*', value='', regex=True).str.strip()
    panels_per_major_postcode = panels_per_minor_postcode.pivot_table(index=panels_per_minor_postcode.columns[0]
                                                                      , values = panels_per_minor_postcode.columns[1], aggfunc='sum')
    installed_panels_locations.append(panels_per_major_postcode)

number_of_panels = pd.concat(installed_panels_locations, axis=1, sort=True).fillna(0).astype(int).sum(axis=1)
number_of_panels.to_json(os.path.join(dirname, folder_with_output_files, "UK_Installed_pannels_summary.json"))

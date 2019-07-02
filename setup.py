from setuptools import setup

setup(
    name='uk-solar-panels',
    version='1.0',
    install_requires=['requests', 'pandas'],
    url='https://sylwia.hs3.linux.pl/my_files/uk_photovoltaics_map/frontend/mapbox_uk.html',
    license='MIT',
    author='Sylwia Mielnicka',
    author_email='hello@sylwiamielnicka.com',
    description='Daily pull UK solar panels data and visualise them using Mapbox & Leaflet.'
)

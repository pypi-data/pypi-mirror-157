# dgf_translate

This Python Library deals with reading DGF Files and converting them into a usable GIS File format that can be imported into GDAL, Fiona and other Geospatial libraries. 


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install dgf_translate
```

## Usage

```python
from dgf_translate import dgf_to_geojson


# returns geojson file path
dgf_to_geojson('/home/usr/file.geojson', '/home/usr/file.geojson', in_crs=25833)


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

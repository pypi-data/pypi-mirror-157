from geojson import dump
from pyproj import Transformer
import re


def write_to_file(geojson_object, fn):
    with open(fn, 'w') as f:
        dump(geojson_object, f)
        return fn


def transform_point(x, y, transformer):
    return transformer.transform(x, y)


def dgf_to_geojson(input_fp, output_fp, in_crs=4326, out_crs=3857):
    """
    Returns a Geojson Format Feature Collection. Only Valid for Point data at the moment
    :param input_fp: (Str)
    :param output_fp: (Str) Absolute/Relative Path for output file
    :param in_crs: (Int) EPSG value for CRS of Input.
    :param out_crs: (Int) EPSG value for CRS of output. Default is Web Mercator
    :return: (Str) Output File path
    """
    geojson_object = {"type": "FeatureCollection", "features": []}

    formats = ('drf', 'dfr', 'wse', 'wp8', 'f', 'docx', 'dc5', 'rdf', 'drx', 'dwf', 'drs', 'doc', 'txt')
    if input_fp.lower().endswith(formats):
        with open(input_fp) as dgf:
            content = dgf.read()
        columns = [x.split(',')[0] for x in re.findall(r'COLUMN = (.*);', content)]
        data_arr = [x.split(',') for x in re.findall(r'DATA = (.*);', content)]
        point_arr = [x.split(',') for x in re.findall(r'POINT = (.*);', content)]
        geom_type = re.findall(r'TYPE = [a-zA-Z]+;', content)[0]
        features_raw = zip(point_arr, data_arr)
        transformer = Transformer.from_crs(f"epsg:{in_crs}", f"epsg:{out_crs}")

        if data_arr and geom_type == 'TYPE = POINT;':
            if len(data_arr[0]) == len(columns):
                for point, data in features_raw:
                    point = transform_point(float(point[0]), float(point[1]), transformer)
                    print(point)
                    geometry = {"type": "Point", "coordinates": point}
                    properties = dict(zip(columns, data))
                    geojson_object['features'].append(
                        {"type": "Feature", "geometry": geometry, "properties": properties})
        return write_to_file(geojson_object, output_fp)

    else:
        raise Exception('Invalid File format. Use any of the following files: ', formats)


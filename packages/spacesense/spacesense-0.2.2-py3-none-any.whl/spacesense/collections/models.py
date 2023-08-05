import json
from enum import Enum
from urllib.request import urlopen

import pandas as pd
from satstac import Collection, Item, ItemCollection


class Sentinel1Band(Enum):
    """
    Sentinel-1 bands
    """

    VH = "VH"
    VV = "VV"
    LIA = "LIA"
    MASK = "MASK"


class Sentinel2Band(Enum):
    """
    Sentinel-2 bands
    """

    B01 = "B01"
    B02 = "B02"
    B03 = "B03"
    B04 = "B04"
    B05 = "B05"
    B06 = "B06"
    B07 = "B07"
    B08 = "B08"
    B8A = "B8A"
    B09 = "B09"
    B11 = "B11"
    B12 = "B12"
    SCL = "SCL"
    CLOUD_SHADOWS = "CLOUD_SHADOWS"
    CLOUD_HIGH_PROBABILITY = "CLOUD_HIGH_PROBABILITY"


class Sentinel1:
    bands = [b.value for b in Sentinel1Band]


class Sentinel2:
    bands = [b.value for b in Sentinel2Band]


class Sentinel1SearchResult:
    def __init__(self, aoi, data_coverage, dataframe):
        """
        Create an instance of the Sentinel-1 Search Result class :py:class:`models

        Attributes:
            aoi (str): A GeoJSON polygon
            output_bands (str, optional): List of strings specifying the names of output bands from the following list of Sentinel-1 bands. By default, all bands are selected and fused. \n
                - VV
                - VH
                - LIA
                - MASK

        To learn more about SAR polarization (VV and VH) and LIA, please review the SAR basics page on the left hand side.

        Pre-processing steps are applied to the level 1 S1 data at this stage through the Snappy Graph Processing Framework (GPF) tool. Given here are the processing steps, and the GPF parameters used.

        | 1. Border noise removal
        |   GPF “Remove-GRD-Border-Noise” process set to True, with the “borderLimit” set to 2000, and the “trimThreshold” set to 0.5
        | 2. Thermal noise removal
        |   GPF “removeThermalNoise” process set to True
        | 3. Radiometric calibration
        |   GPF "outputSigmaBand" set to True, and "outputImageScaleInDb" set to False
        | 4. Terrain correction
        |    GPF options of:
        |        “demName" set to "SRTM 3Sec"
        |        "demResamplingMethod" set to "BILINEAR_INTERPOLATION"
        |        "imgResamplingMethod" set to "BILINEAR_INTERPOLATION"
        |        ”saveProjectedLocalIncidenceAngle" set to True
        |        "saveSelectedSourceBand" set to True
        |        "pixelSpacingInMeter" set to “resolution”)
        |        "alignToStandardGrid" set to True)
        |        "standardGridOriginX" and "standardGridOriginY" set to 0
        |    The “mapProjection” was set using the following projection:
        |        proj = (
        |        'GEOGCS["WGS84(DD)",'
        |        'DATUM["WGS84",'
        |        'SPHEROID["WGS84", 6378137.0, 298.257223563]],'
        |        'PRIMEM["Greenwich", 0.0],'
        |        'UNIT["degree", 0.017453292519943295],'
        |        'AXIS["Geodetic longitude", EAST],'
        |        'AXIS["Geodetic latitude", NORTH]]'
        |        )

        """
        self.aoi = aoi
        self.data_coverage = data_coverage
        self.dataframe = dataframe
        self.output_bands = Sentinel1.bands

    def has_results(self):
        return self.dataframe is not None and len(self.dataframe) > 0

    @property
    def to_dict(self):
        return self.dataframe.to_dict(orient="records")


class Sentinel2SearchResult:
    def __init__(self, aoi, item_collection: ItemCollection):
        """
        Create an instance of the Sentinel-2 Search Result class :py:class:`models.

        Attributes:
            aoi (str): A GeoJSON polygon
            output_bands (str, optional): List of strings specifying the names of output bands from the following list of Sentinel-2 bands. By default, all bands are selected and fused. \n
                - B01
                - B02
                - B03
                - B04
                - B05
                - B06
                - B07
                - B08
                - B08a
                - B09
                - B11
                - B12
                - SCL
                - CLOUD_SHADOWS
                - CLOUD_HIGH_PROBABILITY

        The Sentinel-2 data retrieved is L2A, meaning it represents the bottom of the atmosphere (BOA) reflectance values.
        The following table presents some basic information about the available S2 bands:

        +------------+------------+---------------------+--------------------------------------+
        | Band	     | Resolution | Central Wavelength  |Description                           |
        +============+============+=====================+======================================+
        | B01        | 60 m       | 443 nm              | Ultra Blue (Coastal and Aerosol)     |
        +------------+------------+---------------------+--------------------------------------+
        | B02        | 10 m       | 490 nm              | Blue                                 |
        +------------+------------+---------------------+--------------------------------------+
        | B03        | 10 m       | 560 nm              | Green                                |
        +------------+------------+---------------------+--------------------------------------+
        | B04        | 10 m       | 665 nm              | Red                                  |
        +------------+------------+---------------------+--------------------------------------+
        | B05        | 20 m       | 705 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B06        | 20 m       | 740 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B07        | 20 m       | 783 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B08        | 10 m       | 842 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B8a        | 20 m       | 865 nm              | Visible and Near Infrared (VNIR)     |
        +------------+------------+---------------------+--------------------------------------+
        | B09        | 60 m       | 940 nm              | Short Wave Infrared (SWIR)           |
        +------------+------------+---------------------+--------------------------------------+
        | B11        | 20 m       | 1610 nm             | Short Wave Infrared (SWIR)           |
        +------------+------------+---------------------+--------------------------------------+
        | B12        | 20 m       | 2190 nm             | Short Wave Infrared (SWIR)           |
        +------------+------------+---------------------+--------------------------------------+

        To learn more about Sentinel-2 bands, their details, and their uses, `this page <https://gisgeography.com/sentinel-2-bands-combinations/>`_ has many resources available.

        SCL or Scene Classification Layer, aims to provide pixel classification maps of clouds, cloud shadows,
        vegetation, soils/deserts, water, and snow, as well as defective, saturated, no data, or unclassified values. For more information about Sentinel-2's SCL band, please visit
        `this page describing the Sentinel-2 algorithm <https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/level-2a/algorithm/>`_.

        Please note, Band 10 is not available for level 2A Sentinel-2 data, as this band is used for atmospheric corrections only.

        The following Sentinel-2 properties are available in the S2 search result:

        - type
        - bbox
        - geometry
        - id
        - links
        - stac_version
        - assets
        - collection
        - properties
        - stac_extensions
        - properties.sentinel:boa_offset_applied
        - path
        - timestamp
        - utmZone
        - latitudeBand
        - gridSquare
        - datastrip
        - tileGeometry
        - tileDataGeometry
        - tileOrigin
        - productName
        - productPath
        - name
        - datatakeIdentifier
        - sciHubIngestion
        - s3Ingestion
        - tiles
        - datastrips
        - swathCoveragePercentage
        - validPixelPercentage
        - date
        - title

        **swathCoveragePercentage** is simply the percetage of data covered by the Sentinel-2 swath at the AOI level.

        **ValidPixelPercentage** is defined as a combination of SCL values of NO_DATA (0), CLOUD_SHADOWS (3), CLOUD_MEDIUM_PROBABILITY (8), CLOUD_HIGH_PROBABILITY (9), and SNOW or ICE (11) at the AOI level.
        This is a very useful property to use when determining if a Sentinel-2 scene clear of clouds and snow for vegetation and infrastructure monitoring.


        """
        self.aoi = aoi
        self._item_collection = item_collection
        self._dataframe = self.metadata_dataframe_from_item_collection(item_collection)
        self.output_bands = Sentinel2.bands

    def has_results(self):
        return self.dataframe is not None and len(self.dataframe) > 0

    def is_valid_output_bands(self):
        if all(b.upper() in self.output_bands for b in Sentinel2.bands):
            return (b.upper() for b in self.output_bands)
        else:
            raise ValueError("Invalid S2 output bands")

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        if type(dataframe) != pd.DataFrame:
            raise ValueError("dataframe should be a pandas.DataFrame")
        self._dataframe = dataframe
        self._item_collection = self.item_collection_from_metadata_dataframe()

    @property
    def item_collection(self):
        return self._item_collection

    @item_collection.setter
    def item_collection(self, item_collection: ItemCollection):
        if type(item_collection) != ItemCollection:
            raise ValueError("item_collection should be an ItemCollection")
        self._item_collection = item_collection
        self._dataframe = self.metadata_dataframe_from_item_collection()

    @property
    def to_dict(self):
        return self._item_collection.geojson()

    def metadata_dataframe_from_item_collection(self, item_collection: ItemCollection = None) -> pd.DataFrame:
        item_collection = item_collection or self._item_collection
        features = item_collection.geojson()["features"]
        meta = []
        for i, item in enumerate(item_collection):
            mjson = {}
            mjson.update(features[i])
            url = item.asset("info")["href"]
            response = urlopen(url)
            mjson.update(json.loads(response.read()))
            response = urlopen(f"https://roda.sentinel-hub.com/sentinel-s2-l2a/{mjson['productPath']}/productInfo.json")
            mjson.update(json.loads(response.read()))
            del mjson["dataCoveragePercentage"]
            del mjson["cloudyPixelPercentage"]
            mjson["swathCoveragePercentage"] = item.asset("info")["swath_coverage"]
            mjson["validPixelPercentage"] = item.asset("info")["valid_pixel_percentage"]
            mjson["date"] = item.date
            mjson["title"] = item.id
            meta.append(mjson)
        return pd.DataFrame(data=meta)

    def item_collection_from_metadata_dataframe(self):
        search_results_dict = self._dataframe.to_dict(orient="records")
        items = [Item(search_result_item) for search_result_item in search_results_dict]
        collections = [Collection(collection) for collection in self._item_collection.geojson()["collections"]]
        return ItemCollection(items, collections=collections)

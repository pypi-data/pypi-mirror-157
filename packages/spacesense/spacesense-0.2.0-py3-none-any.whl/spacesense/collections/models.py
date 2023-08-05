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

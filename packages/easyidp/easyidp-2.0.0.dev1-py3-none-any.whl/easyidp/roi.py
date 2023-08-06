import numpy as np

class ROI(object):
    """
    Summary APIs of each objects, often read from shp file.
    """

    def __init__(self) -> None:
        # if has CRS -> GPS coordiantes -> geo2pix convert
        self.CRS = None
        self.coords = {}

    def __getitem__(self, key):
        # groi["id"] -> value or groi[0] -> value
        pass

    def read_shp():
        # if geotiff_proj is not None and shp_proj is not None and shp_proj.name != geotiff_proj.name:
        # shp.convert_proj()
        pass

    def get_z_from_dsm(self, dsm_path):
        pass

    def clip(self, target):
        # call related function
        pass

    def back2raw(self, chunks):
        # call related function
        # need check alt exists, the alt is changing for different dsm?
        pass
import os
import pyproj
import numpy as np
import tifffile as tf

from pyproj.exceptions import CRSError

class GeoTiff(object):

    def __init__(self) -> None:
        pass

    def clip(self, roi):
        # roi: ROI class, with several roi lists
        pass

    def _clip_one_roi(self, roi, save_path=None):
        # roi = single polygon

        # if save_path is not None and is file path:
        #     save_geotiff()
        pass


    def _save_geotiff(imarray, offset, save_path):
        pass

    def _make_empty_container(self, h, w, layer_num=None):
        """
        Produce a empty image, suit the requirement for nodata
        """
        # possible dsm with only one band
        if self.header.band_num == 1:
            # old version: np.ones((self.img_depth, h, w, 1))
            empty_template = np.ones((h, w, 1)) * self.nodata
            
        # possible RGB band
        elif self.header.band_num == 3 and self.dtype==np.uint8:
            if layer_num == 4:
                # old version: np.ones((self.img_depth, h, w, 1))
                empty_template = np.ones((h, w, 4)).astype(np.uint8) * 255
                empty_template[:,:,3] = empty_template[:,:,3] * 0
            else:
                # old version: np.ones((self.img_depth, h, w, 1))
                empty_template = np.ones((h, w, 3)).astype(np.uint8) * 255
            
        # possible RGBA band, empty defined by alpha = 0
        elif self.header.band_num == 4 and self.dtype==np.uint8:
            # old version: np.ones((h, w, 1))
            empty_template = np.ones((h, w, 4)).astype(np.uint8) * 255
            empty_template[:,:,3] = empty_template[:,:,3] * 0
        else:
            raise ValueError('Current version only support DSM, RGB and RGBA images')
            
        return empty_template



def get_header(tif_path):
    with tf.TiffFile(tif_path) as tif:
        header = {'width': None, 'length': None, 'dim':1, 
                'scale': None, 'tie_point': None, 'nodata': None, 'proj': None}

        header["length"] = tif.pages[0].shape[0]
        header["width"] = tif.pages[0].shape[1]
        if len(tif.pages[0].shape) > 2:
            header["dim"] = tif.pages[0].shape[2] 
        header["nodata"] = tif.pages[0].nodata
        
        # tif.pages[0].geotiff_tags >>> 'ModelPixelScale': [0.0034900000000000005, 0.0034900000000000005, 0.0]
        header["scale"] = tif.pages[0].geotiff_tags["ModelPixelScale"][0:2]
        
        # tif.pages[0].geotiff_tags >>> 'ModelTiepoint': [0.0, 0.0, 0.0, 419509.89816000004, 3987344.8286, 0.0]
        header["tie_point"] = tif.pages[0].geotiff_tags["ModelTiepoint"][3:5]
        
        # pix4d:
        #    tif.pages[0].geotiff_tags >>> 'GTCitationGeoKey': 'WGS 84 / UTM zone 54N'
        if "GTCitationGeoKey" in tif.pages[0].geotiff_tags.keys():
            proj_str = tif.pages[0].geotiff_tags["GTCitationGeoKey"]
        # metashape:
        #     tif.pages[0].geotiff_tags >>> 'PCSCitationGeoKey': 'WGS 84 / UTM zone 54N'
        elif "PCSCitationGeoKey" in tif.pages[0].geotiff_tags.keys():
            proj_str = tif.pages[0].geotiff_tags["PCSCitationGeoKey"]
        else:
            raise KeyError("Can not find key 'GTCitationGeoKey' or 'PCSCitationGeoKey' in Geotiff tages")
        
        try:
            proj = pyproj.CRS.from_string(proj_str)
            header['proj'] = proj
        except CRSError as e:
            print(f'[io][geotiff][GeoCorrd] Generation failed, because [{e}], but you can manual specify it later by \n'
                    '>>> import pyproj \n'
                    '>>> proj = pyproj.CRS.from_epsg() # or from_string() or refer official documents:\n'
                    'https://pyproj4.github.io/pyproj/dev/api/crs/coordinate_operation.html')
            pass

    return header


def get_imarray(tif_path):
    """Read full map data as numpy array (time and RAM costy, not recommended)

    Parameters
    ----------
    geotiff_path
    geo_head

    Returns
    -------

    """
    with tf.TiffFile(tif_path) as tif:
        data = tif.pages[0].asarray()

    return data


def geo2pixel(points_hv, geo_head):
    '''
    convert point cloud xyz coordinate to geotiff pixel coordinate (horizontal, vertical)

    :param points_hv: numpy nx3 array, [x, y, z] points or nx2 array [x, y]
    :param geo_head: the geotiff head dictionary from io.geotiff.get_header() function

    :return: The ndarray pixel position of these points (horizontal, vertical)
        Please note: gis coordinate, horizontal is x axis, vertical is y axis, origin at left upper
        To clip image ndarray, the first columns is vertical pixel (along height),
            then second columns is horizontal pixel number (along width),
            the third columns is 3 or 4 bands (RGB, alpha),
            the x and y is reversed compared with gis coordinates.
            This function has already do this reverse, so that you can use the output directly.

        >>> geo_head = easyric.io.geotiff.get_header('dom_path.tiff')
        >>> gis_coord = np.asarray([(x1, y1), ..., (xn, yn)])  # x is horizonal, y is vertical
        >>> photo_ndarray = skimage.io.imread('img_path.jpg')
        (h, w, 4) ndarray  # please note the axes differences
        >>> pixel_coord = geo2pixel(gis_coord, geo_head)
        (horizontal, vertical) ndarray
        # then you can used the outputs with reverse 0 and 1 axis
        >>> region_of_interest = photo_ndarray[pixel_coord[:,1], pixel_coord[:,0], 0:3]
    '''

    gis_xmin = geo_head['tie_point'][0]
    #gis_xmax = geo_head['tie_point'][0] + geo_head['width'] * geo_head['scale'][0]
    #gis_ymin = geo_head['tie_point'][1] - geo_head['length'] * geo_head['scale'][1]
    gis_ymax = geo_head['tie_point'][1]

    gis_ph = points_hv[:, 0]
    gis_pv = points_hv[:, 1]

    # numpy_axis1 = x
    np_ax_h = (gis_ph - gis_xmin) // geo_head['scale'][0]
    # numpy_axis0 = y
    np_ax_v = (gis_ymax - gis_pv) // geo_head['scale'][1]

    pixel = np.concatenate([np_ax_h[:, None], np_ax_v[:, None]], axis=1)

    return pixel.astype(int)


def pixel2geo(points_hv, geo_head):
    '''
    convert  geotiff pixel coordinate (horizontal, vertical) to point cloud xyz coordinate (x, y, z)

    :param points_hv: numpy nx2 array, [horizontal, vertical] points
    :param geo_head: the geotiff head dictionary from io.geotiff.get_header() function

    :return: The ndarray pixel position of these points (horizontal, vertical)
    '''
    gis_xmin = geo_head['tie_point'][0]
    #gis_xmax = geo_head['tie_point'][0] + geo_head['width'] * geo_head['scale'][0]
    #gis_ymin = geo_head['tie_point'][1] - geo_head['length'] * geo_head['scale'][1]
    gis_ymax = geo_head['tie_point'][1]

    # remember the px is numpy axis0 (vertical, h), py is numpy axis1 (horizontal, w)
    pix_ph = points_hv[:, 0] + 0.5  # get the pixel center rather than edge
    pix_pv = points_hv[:, 1] + 0.5

    gis_px = gis_xmin + pix_ph * geo_head['scale'][0]
    gis_py = gis_ymax - pix_pv * geo_head['scale'][1]

    gis_geo = np.concatenate([gis_px[:, None], gis_py[:, None]], axis=1)

    return gis_geo


def geotiff_page_crop(page, top, left, h, w):  
    """
    Extract a crop from a TIFF image file directory (IFD).

    Only the tiles englobing the crop area are loaded and not the whole page.
    This is usefull for large Whole slide images that can't fit int RAM.

    (0,0)
      o--------------------------
      |           ^
      |           | top
      |           v
      | <-------> o=============o  ^
      |   left    |<---- w ---->|  |
      |           |             |  h
      |           |             |  |
      |           o=============o  v

    Modified from: 
    https://gist.github.com/rfezzani/b4b8852c5a48a901c1e94e09feb34743#file-get_crop-py-L60

    Previous version: 
    caas_lite.get_crop(page, i0, j0, h, w)
    
    Parameters
    ----------
    page : TiffPage
        TIFF image file directory (IFD) from which the crop must be extracted.
    top, left: int
        Coordinates of the top left corner of the desired crop.
        top = i0 = height_st
        left = j0 = w_st
    h: int
        Desired crop height.
    w: int
        Desired crop width.
        
    Returns
    -------
    out : ndarray of shape (h, w, sampleperpixel)
        Extracted crop.""
    """
    if page.is_tiled:
        out = _get_tiled_crop(page, top, left, h, w)
    else:
        out = _get_untiled_crop(page, top, left, h, w)

    return out


def _get_tiled_crop(page, i0, j0, h, w):
    """
    The submodule of self.get_crop() for those tiled geotiff

    Copied from: 
    https://gist.github.com/rfezzani/b4b8852c5a48a901c1e94e09feb34743#file-get_crop-py-L60
    """
    if not page.is_tiled:
        raise ValueError("Input page must be tiled")

    im_width = page.imagewidth
    im_height = page.imagelength

    if h < 1 or w < 1:
        raise ValueError("h and w must be strictly positive.")
        
    i1, j1 = i0 + h, j0 + w
    if i0 < 0 or j0 < 0 or i1 >= im_height or j1 >= im_width:
        raise ValueError(f"Requested crop area is out of image bounds.{i0}_{i1}_{im_height}, {j0}_{j1}_{im_width}")

    tile_width, tile_height = page.tilewidth, page.tilelength

    tile_i0, tile_j0 = i0 // tile_height, j0 // tile_width
    tile_i1, tile_j1 = np.ceil([i1 / tile_height, j1 / tile_width]).astype(int)

    tile_per_line = int(np.ceil(im_width / tile_width))

    # older version: (img_depth, h, w, dim)
    out = np.empty((page.imagedepth,
                    (tile_i1 - tile_i0) * tile_height,
                    (tile_j1 - tile_j0) * tile_width,
                    page.samplesperpixel), dtype=page.dtype)

    fh = page.parent.filehandle

    for i in range(tile_i0, tile_i1):
        for j in range(tile_j0, tile_j1):
            index = int(i * tile_per_line + j)

            offset = page.dataoffsets[index]
            bytecount = page.databytecounts[index]

            fh.seek(offset)
            data = fh.read(bytecount)
            tile, indices, shape = page.decode(data, index)

            im_i = (i - tile_i0) * tile_height
            im_j = (j - tile_j0) * tile_width
            out[:, im_i: im_i + tile_height, im_j: im_j + tile_width, :] = tile

    im_i0 = i0 - tile_i0 * tile_height
    im_j0 = j0 - tile_j0 * tile_width

    # old version: out[:, im_i0: im_i0 + h, im_j0: im_j0 + w, :]
    return out[0, im_i0: im_i0 + h, im_j0: im_j0 + w, :]

def _get_untiled_crop(page, i0, j0, h, w):
    """
    The submodule of self.get_crop(), for those untiled geotiff

    Copied from: 
    https://gist.github.com/rfezzani/b4b8852c5a48a901c1e94e09feb34743#file-get_crop-py-L60
    """
    if page.is_tiled:
        raise ValueError("Input page must not be tiled")

    im_width = page.imagewidth
    im_height = page.imagelength

    if h < 1 or w < 1:
        raise ValueError("h and w must be strictly positive.")

    i1, j1 = i0 + h, j0 + w
    if i0 < 0 or j0 < 0 or i1 >= im_height or j1 >= im_width:
        raise ValueError(f"Requested crop area is out of image bounds.{i0}_{i1}_{im_height}, {j0}_{j1}_{im_width}")
    
    out = np.empty((page.imagedepth, h, w, page.samplesperpixel), dtype=page.dtype)
    fh = page.parent.filehandle

    for index in range(i0, i1):
        offset = page.dataoffsets[index]
        bytecount = page.databytecounts[index]

        fh.seek(offset)
        data = fh.read(bytecount)

        tile, indices, shape = page.decode(data, index)

        out[:,index-i0,:,:] = tile[:,:,j0:j1,:]

    return out[0,:,:,:]


def point_query(page, point_hv):
    pass


def imarray_clip_roi(imarray, roi):  # clip roi

    # no need skimage, use shapely.polygon instead
    # https://stackoverflow.com/questions/58288587/get-values-only-within-the-shape-geopandas
    # >>> from shapely.geometry import Polygon
    # >>> turin_final = Polygon([[p.x, p.y] for p in border_point.geometry])
    # >>> within_turin = turin_point[turin_point.geometry.within(turin_final)]
    pass




import numpy as np
from shapely.geometry import MultiPoint, Polygon

from easyidp.visualize import _view_poly2mask

# ignore the warning of shapely convert coordiante
import warnings
warnings.filterwarnings("ignore")


def _my_poly2mask(image_shape, poly_coord, plot=False):
    """convert vector polygon to raster masks
    
    Notes
    -----
    This code is inspired from here:
    https://stackoverflow.com/questions/62280398/checking-if-a-point-is-contained-in-a-polygon-multipolygon-for-many-points

    Parameters
    ----------
    image_shape : tuple with 2 element
        (horizontal, vertical) = (width, height)
        !!! it is reversed with numpy index order !!!
    poly_coord : np.ndarray -> dtype = int or float
        (horizontal, vertical) = (width, height)
        !!! it is reversed with numpy index order !!!

        If dtype is int -> view coord as pixel index number
            Will + 0.5 to coords (pixel center) as judge point
        if dtype is float -> view coords as real coord
            (0,0) will be the left upper corner of pixel square
    plot : bool, optional
        whether show generated results, by default False

    Returns
    -------
    mask : numpy.ndarray
        the generated binary mask
    """

    # check the type of input
    if not isinstance(poly_coord, np.ndarray):
        raise TypeError(f"The `poly_coord` only accept numpy ndarray integer and float types")

    if len(poly_coord.shape)!=2 or poly_coord.shape[1] != 2:
        raise AttributeError(f"Only nx2 ndarray are accepted, not {poly_coord.shape}")

    w, h = image_shape

    # check whether the poly_coords out of mask boundary
    xmin, ymin = poly_coord.min(axis=0)
    xmax, ymax = poly_coord.max(axis=0)

    if xmin < 0 or ymin < 0 or xmax >= w or ymax >= h:
        raise ValueError(f"The polygon coords ({xmin}, {ymin}, {xmax}, {ymax}) is out of mask boundary [0, 0, {w}, {h}]")

    mask = np.zeros((h, w), dtype=bool)

    # use the pixel center as judgement points
    x = np.arange(0, w) + 0.5
    y = np.arange(0, h) + 0.5

    xx, yy = np.meshgrid(x, y)

    # get the coordinates of all pixel points
    # it is reversed with numpy index order -> [vertical, horizontal]
    pts = np.array([yy.ravel(), xx.ravel()]).T
    points = MultiPoint(pts)

    # judge the type of polygon coordinates
    if np.issubdtype(poly_coord.dtype, np.integer):
        # is int type, mainly means it represent
        # the id of int rather than coords xy values
        # -> shift 0.5 as the pixel center
        poly = Polygon(poly_coord + 0.5)
    elif np.issubdtype(poly_coord.dtype, np.floating):
        poly = Polygon(poly_coord)
    else:
        raise TypeError(f"The `poly_coord` only accept numpy ndarray integer and float types")

    points_in = points.intersection(poly)

    # here will raise warning when obtain coords from shapely multipoints
    # -0.5 turns points center coords to point id
    # here are point index of "masked" pixels
    idx = (np.array(points_in) - 0.5).astype(int)

    # turn to masks
    # idx -> (pixel horizontal, pixel vertical)
    # it is reversed with numpy index order -> [vertical, horizontal]
    mask[idx[:,1], idx[:,0]] = True

    if plot:
        _view_poly2mask(np.array(poly.exterior.coords), mask, pts, np.array(points_in))

    return mask
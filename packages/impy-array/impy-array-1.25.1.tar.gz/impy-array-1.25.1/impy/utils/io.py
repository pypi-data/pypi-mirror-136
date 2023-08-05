from __future__ import annotations
from typing import TYPE_CHECKING
from tifffile import TiffFile, imwrite, memmap
import json
import re
import warnings
import os
import numpy as np
from .._cupy import xp

from ..axes import ImageAxesError
from .axesop import complement_axes
from ..utils.axesop import switch_slice

if TYPE_CHECKING:
    from ..arrays.bases import HistoryArray

__all__ = ["imwrite", 
           "memmap",
           "open_tif", 
           "open_mrc",
           "open_img",
           "open_as_dask",
           "get_scale_from_meta", 
           "get_imsave_meta_from_img"]

def load_json(s: str):
    return json.loads(re.sub("'", '"', s))

def open_tif(path: str, return_img: bool = False, memmap: bool = False):
    with TiffFile(path) as tif:
        ijmeta = tif.imagej_metadata
        series0 = tif.series[0]
    
        pagetag = series0.pages[0].tags
        
        hist = []
        if ijmeta is None:
            ijmeta = {}
        
        ijmeta.pop("ROI", None)
        
        if "Info" in ijmeta.keys():
            try:
                infodict = load_json(ijmeta["Info"])
            except:
                infodict = {}
            if "impyhist" in infodict.keys():
                hist = infodict["impyhist"].split("->")
        
        try:
            axes = series0.axes.lower()
        except:
            axes = None
        
        tags = {v.name: v.value for v in pagetag.values()}
        out = {"axes": axes, "ijmeta": ijmeta, "history": hist, "tags": tags}
        if return_img:
            if memmap:
                out["image"] = tif.asarray(out="memmap")
            else:
                out["image"] = tif.asarray()

    return out


def open_mrc(path: str, return_img: bool = False, memmap: bool = False):
    import mrcfile
    if memmap:
        open_func = mrcfile.mmap
    else:
        open_func = mrcfile.open
    
    with open_func(path, mode="r") as mrc:
        ijmeta = {"unit": "nm"}
        ndim = len(mrc.voxel_size.item())
        if ndim == 3:
            axes = "zyx"
            ijmeta["spacing"] = mrc.voxel_size.z/10
        elif ndim == 2:
            axes = "yx"
        else:
            raise RuntimeError(f"ndim = {ndim} not supported")
            
        tags = {}
        tags["XResolution"] = [1, mrc.voxel_size.x/10]
        tags["YResolution"] = [1, mrc.voxel_size.y/10]
        
        out = {"axes": axes, "ijmeta": ijmeta, "history": [], "tags": tags}
        if return_img:
            out["image"] = mrc.data
    
    return out


def open_as_dask(path: str, chunks):
    meta, img = open_img(path, memmap=True)
    axes = meta["axes"]
    if chunks == "default":
        chunks = switch_slice("yx", axes, ifin=img.shape, ifnot=("auto",)*img.ndim)
    if img.dtype == ">u2":
        img = img.astype(np.uint16)
    
    from dask import array as da
    img = da.from_array(img, chunks=chunks, meta=xp.array([])).map_blocks(
        xp.asarray, dtype=img.dtype)
    return meta, img


def open_img(path, memmap: bool = False):
    _, fext = os.path.splitext(os.path.basename(path))
    if fext in (".tif", ".tiff"):
        meta = open_tif(path, True, memmap=memmap)
        img = meta.pop("image")
    elif fext in (".mrc", ".rec", ".map"):
        meta = open_mrc(path, True, memmap=memmap)
        img = meta.pop("image")
    else:
        from skimage import io
        img = io.imread(path)
        if fext in (".png", ".jpg") and img.ndim == 3 and img.shape[-1] <= 4:
            meta = {"axes": "yxc", "ijmeta": {}, "history": []}
        else:
            meta = {"axes": None, "ijmeta": {}, "history": []}
    
    return meta, img


def get_scale_from_meta(meta: dict):
    scale = dict()
    dz = meta["ijmeta"].get("spacing", 1.0)
    try:
        # For MicroManager
        info = load_json(meta["ijmeta"]["Info"])
        dx = dy = info["PixelSize_um"]
    except Exception:
        try:
            tags = meta["tags"]
            xres = tags["XResolution"]
            yres = tags["YResolution"]
            dx = xres[1]/xres[0]
            dy = yres[1]/yres[0]
        except KeyError:
            dx = dy = dz
    
    scale["x"] = dx
    scale["y"] = dy
    # read z scale if needed
    if "z" in meta["axes"]:
        scale["z"] = dz
        
    return scale


def get_imsave_meta_from_img(img: HistoryArray, update_lut=True):
    metadata = img.metadata.copy()
    if update_lut:
        lut_min, lut_max = np.percentile(img, [1, 99])
        metadata.update({"min": lut_min, 
                         "max": lut_max})
    # set lateral scale
    try:
        res = (1/img.scale["x"], 1/img.scale["y"])
    except Exception:
        res = None
    # set z-scale
    if "z" in img.axes:
        metadata["spacing"] = img.scale["z"]
    else:
        metadata["spacing"] = img.scale["x"]
        
    # add history to Info
    try:
        info = load_json(metadata["Info"])
    except:
        info = {}
    info["impyhist"] = "->".join([img.name] + img.history)
    metadata["Info"] = str(info)
    # set axes in tiff metadata
    metadata["axes"] = str(img.axes).upper()
    if img.ndim > 3:
        metadata["hyperstack"] = True
    
    return dict(imagej=True, resolution=res, metadata=metadata)


def save_tif(path: str, img: HistoryArray):
    rest_axes = complement_axes(img.axes, "tzcyx")
    new_axes = ""
    for a in img.axes:
        if a in "tzcyx":
            new_axes += a
        else:
            if len(rest_axes) == 0:
                raise ImageAxesError(f"Cannot save image with axes {img.axes}")
            new_axes += rest_axes[0]
            rest_axes = rest_axes[1:]
    
    # make a copy of the image for saving
    if new_axes != img.axes:
        img_new = img.copy()
        img_new.axes = new_axes
        img_new.set_scale(img)
        img = img_new
        
        warnings.warn("Image axes changed", UserWarning)
    
    img = img.sort_axes()
    imsave_kwargs = get_imsave_meta_from_img(img, update_lut=True)
    imwrite(path, img, **imsave_kwargs)


def save_mrc(path: str, img: HistoryArray):
    if img.scale_unit and img.scale_unit != "nm":
        raise ValueError(
            f"Scale unit {img.scale_unit} is not supported. Convert to nm instead."
            )
        
    import mrcfile
    
    # get voxel_size
    if img.axes not in ("zyx", "yx"):
        raise ImageAxesError(
            f"Can only save zyx- or yx- image as a mrc file, but image has {img.axes} axes."
            )
    if os.path.exists(path):
        with mrcfile.open(path, mode="r+") as mrc:
            mrc.set_data(img.value)
            mrc.voxel_size = tuple(np.array(img.scale)[::-1] * 10)
            
    else:
        with mrcfile.new(path) as mrc:
            mrc.set_data(img.value)
            mrc.voxel_size = tuple(np.array(img.scale)[::-1] * 10)

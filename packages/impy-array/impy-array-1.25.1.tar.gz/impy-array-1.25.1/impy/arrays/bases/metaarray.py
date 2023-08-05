from __future__ import annotations
import numpy as np
from collections import namedtuple
from ..axesmixin import AxesMixin
from ..._types import *
from ...axes import ImageAxesError
from ..._cupy import xp, xp_ndarray, asnumpy
from ...utils.axesop import *
from ...utils.slicer import *
from ...collections import DataList


class MetaArray(AxesMixin, np.ndarray):
    additional_props = ["dirpath", "metadata", "name"]
    NP_DISPATCH = {}
    name: str
    dirpath: str
    
    def __new__(cls, obj, name=None, axes=None, dirpath=None, 
                metadata=None, dtype=None) -> MetaArray:
        if isinstance(obj, cls):
            return obj
        
        self = np.asarray(obj, dtype=dtype).view(cls)
        self.dirpath = dirpath
        self.name = name
        
        # MicroManager
        if isinstance(self.name, str) and self.name.endswith(".ome") and "_MMStack" in self.name:
            self.name = self.name.split("_MMStack")[0]
        
        self.axes = axes
        self.metadata = metadata
        return self
    
    @property
    def value(self) -> np.ndarray:
        return np.asarray(self)
    
    def _repr_dict_(self) -> dict[str, Any]:
        return {"    shape     ": self.shape_info,
                "    dtype     ": self.dtype,
                "  directory   ": self.dirpath,
                "original image": self.name}
    
    def __str__(self):
        return self.name
    
    @property
    def shape(self):
        try:
            tup = namedtuple("AxesShape", list(self.axes))
            return tup(*super().shape)
        except ImageAxesError:
            return super().shape
    

    def showinfo(self):
        print(repr(self))
        return None
    
    def _set_additional_props(self, other):
        # set additional properties
        # If `other` does not have it and `self` has, then the property will be inherited.
        for p in self.__class__.additional_props:
            setattr(self, p, getattr(other, p, 
                                     getattr(self, p, 
                                             None)))
    
    def _set_info(self, other, new_axes:str="inherit"):
        self._set_additional_props(other)
        # set axes
        try:
            if new_axes != "inherit":
                self.axes = new_axes
                self.set_scale(other)
            else:
                self.axes = other.axes.copy()
        except ImageAxesError:
            self.axes = None
        
        return None
    
    def __getitem__(self, key: int | str | slice | tuple) -> MetaArray:
        if isinstance(key, str):
            # img["t=2;z=4"] ... ImageJ-like, axis-targeted slicing
            sl = self._str_to_slice(key)
            return self.__getitem__(sl)

        if isinstance(key, np.ndarray):
            key = self._broadcast(key)
        
        out = super().__getitem__(key)         # get item as np.ndarray
        keystr = key_repr(key)                 # write down key e.g. "0,*,*"
        
        if isinstance(out, self.__class__):   # cannot set attribution to such as numpy.int32 
            if hasattr(key, "__array__") and key.size > 1:
                # fancy indexing will lose axes information
                new_axes = None
                
            elif "new" in keystr:
                # np.newaxis or None will add dimension
                new_axes = None
                
            elif not self.axes.is_none() and self.axes:
                del_list = [i for i, s in enumerate(keystr.split(",")) if s not in ("*", "")]
                new_axes = del_axis(self.axes, del_list)
            else:
                new_axes = None
                
            out._getitem_additional_set_info(self, keystr=keystr,
                                             new_axes=new_axes, key=key)
        
        return out
    
    def _getitem_additional_set_info(self, other: MetaArray, **kwargs):
        self._set_info(other, kwargs["new_axes"])
        return None
    
    def __setitem__(self, key: int | str | slice | tuple, value):
        if isinstance(key, str):
            # img["t=2;z=4"] ... ImageJ-like method
            sl = self._str_to_slice(key)
            return self.__setitem__(sl, value)
        
        if isinstance(key, MetaArray) and key.dtype == bool and not key.axes.is_none():
            key = add_axes(self.axes, self.shape, key, key.axes)
            
        elif isinstance(key, np.ndarray) and key.dtype == bool and key.ndim == 2:
            # img[arr] ... where arr is 2-D boolean array
            key = add_axes(self.axes, self.shape, key)

        super().__setitem__(key, value)
    
    
    def __array_finalize__(self, obj):
        """
        Every time an np.ndarray object is made by numpy functions inherited to ImgArray,
        this function will be called to set essential attributes. Therefore, you can use
        such as img.copy() and img.astype("int") without problems (maybe...).
        """
        if obj is None: return None
        self._set_additional_props(obj)

        try:
            self.axes = getattr(obj, "axes", None)
        except Exception:
            self.axes = None
        if not self.axes.is_none() and len(self.axes) != self.ndim:
            self.axes = None
        
    def __array_ufunc__(self, ufunc, method, *args, **kwargs):
        """
        Every time a numpy universal function (add, subtract, ...) is called,
        this function will be called to set/update essential attributes.
        """
        args_, _ = _replace_inputs(self, args, kwargs)

        result = getattr(ufunc, method)(*args_, **kwargs)

        if result is NotImplemented:
            return NotImplemented
        
        result = result.view(self.__class__)
        
        # in the case result is such as np.float64
        if not isinstance(result, self.__class__):
            return result
        
        result._process_output(ufunc, args, kwargs)
        return result
    
    def _inherit_meta(self, obj, ufunc, **kwargs):
        """
        Copy axis, history etc. from obj.
        This is called in __array_ufunc__(). Unlike _set_info(), keyword `axis` must be
        considered because it changes `ndim`.
        """
        if "axis" in kwargs.keys() and not obj.axes.is_none():
            new_axes = del_axis(obj.axes, kwargs["axis"])
        else:
            new_axes = "inherit"
        self._set_info(obj, new_axes=new_axes)
        return self
    
    def __array_function__(self, func, types, args, kwargs):
        """
        Every time a numpy function (np.mean...) is called, this function will be called. Essentially numpy
        function can be overloaded with this method.
        """
        if (func in self.__class__.NP_DISPATCH and 
            all(issubclass(t, MetaArray) for t in types)):
            return self.__class__.NP_DISPATCH[func](*args, **kwargs)
        
        args_, _ = _replace_inputs(self, args, kwargs)

        result = func(*args_, **kwargs)

        if result is NotImplemented:
            return NotImplemented
        
        if isinstance(result, (tuple, list)):
            _as_meta_array = lambda a: a.view(self.__class__)._process_output(func, args, kwargs) \
                if type(a) is np.ndarray else a
            result = DataList(_as_meta_array(r) for r in result)
            
        else:
            if isinstance(result, np.ndarray):
                result = result.view(self.__class__)
            # in the case result is such as np.float64
            if isinstance(result, self.__class__):
                result._process_output(func, args, kwargs)
        
        return result
    
    def _process_output(self, func, args, kwargs):
        # find the largest MetaArray. Largest because of broadcasting.
        arr = None
        for arg in args:
            if isinstance(arg, self.__class__):
                if arr is None or arr.ndim < arg.ndim:
                    arr = arg
                    
        if isinstance(arr, self.__class__):
            self._inherit_meta(arr, func, **kwargs)
        
        return self
        
    
    @classmethod
    def implements(cls, numpy_function):
        """
        Add functions to NP_DISPATCH so that numpy functions can be overloaded.
        """        
        def decorator(func):
            cls.NP_DISPATCH[numpy_function] = func
            func.__name__ = numpy_function.__name__
            return func
        return decorator
    
    def _str_to_slice(self, string: str):
        """
        get subslices using ImageJ-like format.
        e.g. 't=3:, z=1:5', 't=1, z=:7'
        """
        return axis_targeted_slicing(self.ndim, str(self.axes), string)
    
    def sort_axes(self) -> MetaArray:
        """
        Sort image dimensions to ptzcyx-order

        Returns
        -------
        MetaArray
            Sorted image
        """
        order = self.axes.argsort()
        return self.transpose(order)

    
    def apply_dask(self, 
                   func: Callable,
                   c_axes: str | None = None,
                   drop_axis: Iterable[int] = [], 
                   new_axis: Iterable[int] = None, 
                   dtype = np.float32, 
                   out_chunks: tuple[int, ...] = None,
                   args: tuple[Any] = None,
                   kwargs: dict[str, Any] = None
                   ) -> MetaArray:
        """
        Convert array into dask array and run a batch process in parallel. In many cases batch process 
        in this way is faster than `multiprocess` module.

        Parameters
        ----------
        func : callable
            Function to apply.
        c_axes : str, optional
            Axes to iterate.
        drop_axis : Iterable[int], optional
            Passed to map_blocks.
        new_axis : Iterable[int], optional
            Passed to map_blocks.
        dtype : any that can be converted to np.dtype object, default is np.float32
            Output data type.
        out_chunks : tuple of int, optional
            Output chunks. This argument is important when the output shape will change.
        args : tuple, optional
            Arguments that will passed to `func`.
        kwargs : dict
            Keyword arguments that will passed to `func`.

        Returns
        -------
        MetaArray
            Processed array.
        """        
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()
        
        if len(c_axes) == 0:
            # Do not construct dask tasks if it is not needed.
            out = asnumpy(func(self.value, *args, **kwargs), dtype=dtype)
        else:
            from dask import array as da
            new_axis = _list_of_axes(self, new_axis)
            drop_axis = _list_of_axes(self, drop_axis)
                
            # determine chunk size and slices
            chunks = switch_slice(c_axes, self.axes, ifin=1, ifnot=self.shape)
            slice_in = []
            slice_out = []
            for i, a in enumerate(self.axes):
                if a in c_axes:
                    slice_in.append(0)
                    slice_out.append(np.newaxis)
                else:
                    slice_in.append(slice(None))
                    slice_out.append(slice(None))
                
                if i in drop_axis:
                    slice_out.pop(-1)
                if i in new_axis:
                    slice_in.append(np.newaxis)
                    
            slice_in = tuple(slice_in)
            slice_out = tuple(slice_out)
            
            all_args = (self.value,) + args
            img_idx = []
            args = []
            for i, arg in enumerate(all_args):
                if isinstance(arg, (np.ndarray, xp_ndarray)) and arg.shape == self.shape:
                    args.append(da.from_array(arg, chunks=chunks))
                    img_idx.append(i)
                else:
                    args.append(arg)
                    
            def _func(*args, **kwargs):
                args = list(args)
                for i in img_idx:
                    if args[i].ndim < len(slice_in):
                        continue
                    args[i] = args[i][slice_in]
                out = func(*args, **kwargs)
                return asnumpy(out[slice_out])
            
            out = da.map_blocks(_func, 
                                *args, 
                                drop_axis=drop_axis,
                                new_axis=new_axis, 
                                meta=xp.array([], dtype=dtype), 
                                chunks=out_chunks,
                                **kwargs
                                )
            
            out = out.compute()
            
        out = out.view(self.__class__)
        
        return out
    
    def transpose(self, axes):
        """
        change the order of image dimensions.
        'axes' will also be arranged.
        """
        out = super().transpose(axes)
        if self.axes.is_none():
            new_axes = None
        else:
            new_axes = "".join([self.axes[i] for i in list(axes)])
        out._set_info(self, new_axes=new_axes)
        return out
    
    def _broadcast(self, value):
        """
        More flexible broadcasting. If `self` has "zcyx"-axes and `value` has "zyx"-axes, then
        they should be broadcasted by stacking `value` along "c"-axes
        """        
        if isinstance(value, MetaArray) and not value.axes.is_none():
            value = add_axes(self.axes, self.shape, value, value.axes)
        elif isinstance(value, np.ndarray):
            try:
                if self.sizesof("yx") == value.shape:
                    value = add_axes(self.axes, self.shape, value)
            except AttributeError:
                pass
        return value
    
    def __add__(self, value):
        value = self._broadcast(value)
        return super().__add__(value)
    
    def __sub__(self, value):
        value = self._broadcast(value)
        return super().__sub__(value)
    
    def __mul__(self, value):
        value = self._broadcast(value)
        return super().__mul__(value)
    
    def __truediv__(self, value):
        value = self._broadcast(value)
        return super().__truediv__(value)

def _list_of_axes(img, axis):
    if axis is None:
        axis = []
    elif isinstance(axis, str):
        axis = [img.axisof(a) for a in axis]
    elif np.isscalar(axis):
        axis = [axis]
    return axis
        
def _replace_inputs(img: MetaArray, args, kwargs):
    _as_np_ndarray = lambda a: a.value if isinstance(a, MetaArray) else a
    # convert arguments
    args = tuple(_as_np_ndarray(a) for a in args)
    if "axis" in kwargs:
        axis = kwargs["axis"]
        if isinstance(axis, str):
            _axis = tuple(map(img.axisof, axis))
            if len(_axis) == 1:
                _axis = _axis[0]
            kwargs["axis"] = _axis
    
    if "out" in kwargs:
        kwargs["out"] = tuple(_as_np_ndarray(a) for a in kwargs["out"])
    
    return args, kwargs
import numpy as np
import pandas as pd
import warnings

from abc import ABC, abstractmethod
from functools import lru_cache
from teaspoon.plots.static import ensemble_series
from teaspoon import TSP

try:
    import netCDF4 as nc
except ModuleNotFoundError:
    warnings.warn("Missing netCDF4 library. Some functionality will be limited.")


if False:  # work-around for type hints error (F821 undefined name)
    import matplotlib


""" Ensemble rules and assumptions

- time 'dimension' must be identical for all TSPs ? Or if its not, can't access certain functionality?  
    - method to standardize/ interpolate to common grid?
- depth 'dimension' must be identical?

- 'values' returns array with shape N,T,Z
"""
class AbstractEnsemble(ABC):

    @property
    @abstractmethod
    def values(self) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def times(self) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def depths(self) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def attributes(self) -> np.ndarray:
        pass

    @abstractmethod
    def get(self, i) -> TSP:
        pass

class Ensemble(AbstractEnsemble):

    def __init__(self, tsp_list: "list[TSP]"):
        self.tsp = tsp_list  
    

class GtpemEnsemble(AbstractEnsemble):

    def __init__(self, gtpem_file, metadata_variables=['simulation', 'model']):
        self.ncdf = nc.Dataset(gtpem_file)
        self._mv = metadata_variables

    def __del__(self):
        self.ncdf.close()

    def get(self, i) -> TSP:
        times = self.times
        depths = self.depths
        values = self.values[i,:,:]
        metadata = self.get_attributes(i).to_dict()
        
        tsp = TSP(times=times, depths=depths, values=values, metadata=metadata)
        
        return tsp

    def get_attributes(self, i) -> pd.DataFrame:
        return self.attributes.loc[i,:]

    @property
    @lru_cache
    def times(self) -> np.ndarray:
        warnings.warn("I'm only using geotop model results")
        date = self.ncdf['geotop']['Date']
        # TODO: improve time handling (or in GTPEM)
        times = nc.num2date(date[:], units=date.units, calendar=date.calendar,
                            only_use_python_datetimes=True)
        times = pd.to_datetime([t.isoformat() for t in times.data])

        return times

    @property
    @lru_cache
    def depths(self) -> np.ndarray:
        warnings.warn("I'm only using geotop model results")
        depth = self.ncdf['geotop']['soil_depth'][:]

        return depth

    @property
    @lru_cache
    def values(self) -> np.ndarray:
        warnings.warn("I'm only using geotop model results")
        depth = self.ncdf['geotop']['Tg'][:]

        return depth
    
    @property
    def attributes(self) -> pd.DataFrame:
        attrs = np.array([self.ncdf['geotop'][attr][:] for attr in self._mv])
        attrs = pd.DataFrame(attrs.transpose())
        attrs.columns = self._mv
        
        return attrs

    def plot_ensemble(self, depth, groups:"np.ndarray" = None, **kwargs) -> "matplotlib.figure.Figure":
        if groups is None:
            groups = self.attributes['simulation'].str.slice(22, 26).values
        
        values = self.values[:,:,depth].transpose()

        fig = ensemble_series(times = self.times, 
                              values=values,
                              groups=groups, **kwargs)
        fig.show()

        return fig

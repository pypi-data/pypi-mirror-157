import datetime
import numpy as np
import pandas as pd
import netCDF4 as nc
import re
import warnings

from pathlib import Path
from typing import Union, Optional

from teaspoon.dataloggers.Geoprecision import detect_geoprecision_type
from teaspoon.dataloggers.HOBO import HOBO, HOBOProperties

from teaspoon.tsp import TSP, IndexedTSP
from teaspoon.misc import _is_depth_column


def read_csv(filepath: str,
              datecol: "Union[str, int]",
              datefmt:str = "%Y-%m-%d %H:%M:%S",
              depth_pattern: str = r"^(-?[0-9\.]+)$",
              na_values:list = [],
              **kwargs) -> TSP:
    r"""Read an arbitrary CSV file 
   
    Date and time must be in a single column, and the csv must be in the
    'wide' data format (each depth is a separate column)

    Parameters
    ----------
    filepath : str
        Path to csv file
    datecol : Union[str, int]
        Either the numeric index (starting at 0) of date column (if int) or name of date column or regular expression (if str)
    datefmt : str, optional
        The format of the datetime values. Use `python strftime format codes <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_, 
        by default ``"%Y-%m-%d %H:%M:%S"``
    depth_pattern : str, optional
        A regular expression that matches the column names with depths. The regular expression must
        have a single capture group that extracts just the numeric part of the column header, by default r"^(-?[0-9\.]+)$".
        If column names were in the form ``"+/-1.0_m"`` (i.e. included 'm' to denote units), you could use the regular expression ``r"^(-?[0-9\.]+)_m$"``
    na_values : list, optional
        Additional strings to recognize as NA. Passed to pandas.read_csv, by default []

    Returns
    -------
    TSP
        A teaspoon time series profile object.
    """
    
    raw = pd.read_csv(filepath, na_values=na_values, **kwargs)
    
    if not datecol in raw.columns and isinstance(datecol, str):
        datecol = [re.search(datecol, c).group(1) for c in raw.columns if re.search(datecol, c)][0]
    
    time = pd.to_datetime(raw[datecol], format=datefmt).to_numpy()

    depth = [re.search(depth_pattern, c).group(1) for c in raw.columns if _is_depth_column(c, depth_pattern)]
    depth_numeric = np.array([float(d) for d in depth])

    values = raw.loc[:, depth].to_numpy()

    tsp = TSP(time, depth_numeric, values)

    return tsp


def read_gtnp(filename: str, metadata_filepath=None) -> TSP:
    """Read test file from GTN-P database export

    Parameters
    ----------
    filename : str
        Path to file.
    metadata_file : str, optional
        Path to GTN-P metadata file, by default None

    Returns
    -------
    TSP
        A teaspoon time series profile object.
    """
    tsp = read_csv(filename,
                   na_values=[-999.0],
                   datecol="Date/Depth",
                   datefmt="%Y-%m-%d %H:%M:%S",
                   depth_pattern=r"^(-?[0-9\.]+)$")

    return tsp


def read_geotop(file: str) -> TSP:
    """Read a GEOtop soil temperature output file

    Parameters
    ----------
    file : str
        Path to file.

    Returns
    -------
    TSP
        A teaspoon time series profile object.
    """
    tsp = read_csv(file,
                   na_values=[-9999.0],
                   datecol="^(Date.*)",
                   datefmt=r"%d/%m/%Y %H:%M",
                   depth_pattern=r"^(-?[0-9\.]+)$")
    
    tsp._depths *= 0.001  # Convert to [m]

    return tsp


def read_gtpem(file: str) -> "list[TSP]":
    output = list()
    try:
        with nc.Dataset(file) as ncdf:
            n_sim = len(ncdf['geotop']['sitename'][:])
            time = 1
            for i, name in enumerate(ncdf['geotop']['sitename'][:]):
                pass
                #tsp = TSP()
    except NameError:
        warnings.warn("netCDF4 library must be installed.")
    
    return output


def read_ntgs(filename: str) -> TSP:
    """Read a file from the NTGS permafrost database

    Parameters
    ----------
    filename : str
        Path to file.

    Returns
    -------
    TSP
        A teaspoon time series profile object.
    """
    if Path(filename).suffix == ".csv":
        try:
            raw = pd.read_csv(filename, keep_default_na=False,na_values=[''], parse_dates={"time": [4,5]}, date_parser=__nt_date_parser)
        except IndexError:
            raise IndexError("There are insufficient columns, the file format is invalid.")
    elif Path(filename).suffix in [".xls", ".xlsx"]:
        raise NotImplementedError("Convert to CSV")
        #try:
        #    raw = pd.read_excel(filename, keep_default_na=False, parse_dates={"time": [4,5]}, date_parser=self.getISOFormat)
        #except IndexError:
        #    raise IndexError("There are insufficient columns, the file format is invalid.") 
    else:
        raise TypeError("Unsupported file extension.")

    metadata = {
                'project_name': raw['project_name'][0],
                'site_id': raw['site_id']
                }
    match_depths = [c for c in [re.search(r"(-?[0-9\.]+)_m$", C) for C in raw.columns] if c]
    values = raw.loc[:, [d.group(0) for d in match_depths]].values
    times = raw['time'].dt.to_pydatetime()
        
    tsp = TSP(times=times,
              depths=[float(d.group(1)) for d in match_depths],
              values=values,
              latitude=raw['latitude'].values[0],
              longitude=raw['longitude'].values[0],
              metadata=metadata)

    return tsp


def __nt_date_parser(date, time) -> datetime.datetime:
        if isinstance(date, str):
            # Case from CSV files where the date is string
            try:
                year, month, day = [int(dateVal) for dateVal in date.split("-")]
            except ValueError:
                raise ValueError(f"The date {date} was unable to be parsed. The format required is YYYY-MM-DD.")
        elif isinstance(date, datetime.datetime):
            # Case XLSX files - are "timestamp" objects
            year, month, day = date.year, date.month, date.day
        else:
            raise ValueError(f"The date {date} was unable to be parsed.")
            
        if isinstance(time, str):
            try:
                h, m, s = [int(timeVal) for timeVal in time.split(":")]
            except ValueError:
                raise ValueError(f"The time {time} was unable to be parsed. The format required is (H)H:MM:SS.")
        
        elif isinstance(time, datetime.time):
            h, m, s = int(time.hour), time.minute, time.second
        
        else:
            raise ValueError(f"The time {time} was unable to be parsed.")
        
        return datetime.datetime(year, month, day, hour=h, minute=m, second=s)


def read_geoprecision(filepath: str) -> IndexedTSP:
    """Read a Geoprecision datalogger export (text file)

    Reads GP5W- and FG2-style files from geoprecision.

    Parameters
    ----------
    filepath : str
        Path to file.

    Returns
    -------
    IndexedTSP
        A teaspoon indexed time series profile
    """
    reader = detect_geoprecision_type(filepath)
    
    if reader is None:
        raise RuntimeError("Could not detect type of geoprecision file (GP5W or FG2 missing from header")

    data = reader().read(filepath)

    tsp = IndexedTSP(times=data['TIME'].dt.to_pydatetime(),
                     values=data.drop("TIME", axis=1).values)

    return tsp



def read_hoboware(filepath: str, hoboware_config: Optional[HOBOProperties]=None) -> IndexedTSP:
    """Read Onset HoboWare datalogger exports

    Parameters
    ----------
    filepath : str
        Path to a file
    hoboware_config : HOBOProperties, optional
        A HOBOProperties object with information about how the file is configured. If not 
        provided, the configuration will be automatically detected if possible, by default None

    Returns
    -------
    IndexedTSP
        A teaspoon indexed time series profile. Use the `set_depths` method to provide depth information
    """
    reader = HOBO(properties=hoboware_config)
    data = reader.read(filepath)

    tsp = IndexedTSP(times=data['TIME'].dt.to_pydatetime(),
                     values=data.drop("TIME", axis=1).values)

    return tsp

from multiprocessing import Pool
from pandas.core.apply import frame_apply
import pandas as pd
from pandas._libs import lib
import numpy as np


def apply_standard(func):
    '''
    map function using pandas lib map_infer for pandas.series alike object
    '''
    global _func_
    _func_ = lambda x: lib.map_infer(x, func, convert=True)


def FramColumnApply(func):
    '''
    map function for column's apply (i.e., axis = 1) to pandas.DataFrame
    '''
    global _func_
    _func_ = lambda x: frame_apply(x, func, axis=1, convert_dtype=True).apply()


def pipe_apply(x):
    '''pipe pandas lib function'''
    return _func_(x)


def split_dataframe_by_position(df: pd.DataFrame, splits: int) -> pd.DataFrame:
    """
    Cut a pd.dataframe into an integer mutiple of the pd.DataFrame splits
    Returns a list of dataframes.
    """
    dfs = []
    increments = len(df) // splits
    ind_start = 0
    ind_end = ind_start + increments
    for split in range(splits):
        temp = df.iloc[ind_start:ind_end, :]
        dfs.append(temp)
        ind_start += increments
        ind_end += increments

    if len(df) % splits == 0:
        return dfs
    else:
        dfs.append(dfs.iloc[ind_start::, :])
        return dfs


def series_mapply(self, func, ncpus=2):
    all_data = np.array_split(self.values, ncpus)

    with Pool(ncpus, initializer=apply_standard, initargs=(func,)) as p:
        result_objects = p.map(pipe_apply, all_data)

    if isinstance(result_objects[0], pd.DataFrame):
        return pd.DataFrame.from_items(zip(self.index.name, result_objects))
    else:
        return np.concatenate(result_objects)



def frame_mapply(self, func, ncpus=2, axis=0):
    assert axis in [0, 1]
    if axis == 0:
        all_data = np.array_split(self.values, ncpus)
        initializer = apply_standard
    else:  # axis == 1
        all_data = split_dataframe_by_position(self, ncpus)
        initializer = FramColumnApply

    with Pool(ncpus, initializer=initializer, initargs=(func,)) as p:
        result_objects = p.map(pipe_apply, all_data)

    if isinstance(result_objects[0], pd.DataFrame):
        return pd.DataFrame.from_items(zip(self.index.name, result_objects))
    else:
        return np.concatenate(result_objects)


def apply_plain(func):
    '''
    map function
    '''
    global _func_
    _func_ = lambda x: func(x)


def groupby_mapply(self, func, ncpus=2):
    indices = list(self.indices.keys())
    grouper = [group.values for ind, group in self]

    with Pool(ncpus, initializer=apply_plain, initargs=(func,)) as p:
        result_objects = p.map(pipe_apply, grouper)

    if isinstance(result_objects[0], pd.DataFrame):
        return pd.DataFrame.from_items(zip(self.dtype.name, result_objects)).set_index(indices)
    else:
        return pd.DataFrame(result_objects, columns=[self.dtype.name], index=indices)


pd.core.groupby.generic.SeriesGroupBy.mapply = groupby_mapply
pd.core.frame.DataFrame.mapply = frame_mapply
pd.core.series.Series.mapply = series_mapply

# to do list
# pd.core.groupby.generic.DataFrameGroupBy.mapply = groupby_mapply
# resample apply
# read csv excel
if __name__ == '__main__':
    pass
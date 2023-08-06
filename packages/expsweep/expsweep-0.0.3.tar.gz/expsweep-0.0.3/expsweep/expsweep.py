#!/usr/bin/env python3

from functools import reduce
from itertools import product
from operator import mul
from multiprocessing import cpu_count as cpus
import pandas as pd

def experiment(func, disable_print=False, repeat=1, merge=False, cpu_count=None,
               backend='processes', pqdm_kwargs={}, **kwargs):
    """
    Run `func` with all combinations of input parameters and return results in
    dataframe

    Args:
        func (function): function which returns a dict of results
            use `return dict(**locals())` to return all function variables
        disable_print (boolean): disable tqdm printing
        repeat (int): number of repetitions for each combination of parameters
        merge (boolean): whether to merge experiment results into a single column
        cpu_count (int): number of cores/cpus to use (default: use all but 1 core)
        backend ('str'): pqdm backend to use (default: 'processes')
        pqdm_kwargs (dict): dict of keyword args to pass to pqdm
        kwargs: keyword arguments that will be passed to `func`
    """

    # clear any left over progressbars if in ipython
    # https://github.com/tqdm/tqdm/issues/375#issuecomment-576863223
    # getattr(tqdm, '_instances', {}).clear()


    # make non-interable kwargs iterable
    iterables = []
    for val in kwargs.values():
        try:
            iter(val)
            iterables.append(val)
        except TypeError:
            iterables.append([val])
    # turn parameters into list of dicts to pass to pqdm
    param_dicts = []
    for params in product(*iterables):
        param_dict = dict(zip(kwargs.keys(), params))
        param_dicts += [param_dict] * repeat

    if cpu_count is None:
        cpu_count = cpus() - 1
    if backend == 'processes':
        from pqdm.processes import pqdm
    elif backend == 'threads':
        from pqdm.threads import pqdm
    else:
        raise Exception("Unsupported backend: " + str(backend))

    return_values = pqdm(
        param_dicts,
        func,
        n_jobs=cpu_count,
        argument_type='kwargs',
        disable=disable_print,
        **pqdm_kwargs
    )

    for retval in return_values:
        if isinstance(retval, Exception):
            raise retval

    # insert function arguments into table
    results = pd.concat(
        [
            pd.DataFrame(param_dicts),
            pd.DataFrame(return_values),
        ],
        axis=1
    )

    # melt result columns together and create new categorical column
    # if category_name is not None and value_name is not None:
    if merge:
        results = merge_columns(
            results,
            return_values[0].keys(),
            "experiment",
            "result"
            # category_name,
            # value_name
        )

    return results

    # results = []
    # with tqdm(desc='Trials', total=total, leave=None, disable=disable_print) as tqdm_bar:
    #     for values in product(*kwargs.values()):
    #         for _ in range(repeat):
    #             func_kwargs = dict(zip(kwargs.keys(), values))
    #             result = func(**func_kwargs)
    #             tqdm_bar.update(1)

    #             if type(result) is not dict:
    #                 result = {'result': result}

    #             results.append({**result, **func_kwargs})

    # return pd.DataFrame(results)


def merge_columns(table, columns, var_name, value_name):
    """
    Use pd.melt to combine results from two different columns for ease of plotting
    in seaborn

    BEFORE
    >>> table
       method1  method2
    0   18.748   23.263
    1   20.657   24.003
    2   19.405   22.212
    3   19.793   22.463
    4   18.116   22.382

    AFTER
    >>> merge_colums(table, ['method1_snr', 'method2_snr'], 'method', 'snr')
        method     snr
    0  method1  18.748
    1  method1  20.657
    2  method1  19.405
    3  method1  19.793
    4  method1  18.116
    5  method2  23.263
    6  method2  24.003
    7  method2  22.212
    8  method2  22.463
    9  method2  22.382

    Args:
        table (pd.DataFrame): table with columsn to merge
        columns (list): list of column names to merge
        var_name (str): new name of categorical column
        value_name 9str): new name of data column

    """
    merged = pd.melt(
        table,
        id_vars=table.columns.difference(columns),
        value_vars=columns,
        var_name=var_name,
        value_name=value_name,
    )

    return merged

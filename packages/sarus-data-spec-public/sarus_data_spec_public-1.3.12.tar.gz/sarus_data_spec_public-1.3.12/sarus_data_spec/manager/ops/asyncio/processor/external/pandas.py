from typing import Any, List, Tuple, Union
import logging

import pandas as pd

from .utils import sarus_external_op

logger = logging.getLogger(__name__)


@sarus_external_op
async def pd_loc(
    parent_val: Any, key: Tuple[Union[str, slice, List[str]], ...]
) -> pd.DataFrame:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return pd.core.indexing._LocIndexer.__getitem__(parent_val.loc, key)


@sarus_external_op
async def pd_eq(val_1: Any, val_2: Any) -> pd.DataFrame:
    return val_1 == val_2


@sarus_external_op
async def pd_mean(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.mean(*args, **kwargs)


@sarus_external_op
async def pd_std(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.std(*args, **kwargs)


@sarus_external_op
async def pd_any(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.any(*args, **kwargs)


@sarus_external_op
async def pd_describe(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.describe(*args, **kwargs)


@sarus_external_op
async def pd_select_dtypes(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.select_dtypes(*args, **kwargs)


@sarus_external_op
async def pd_quantile(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.quantile(*args, **kwargs)


@sarus_external_op
async def pd_sum(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.sum(*args, **kwargs)


@sarus_external_op
async def pd_fillna(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.fillna(*args, **kwargs)


@sarus_external_op
async def pd_round(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.round(*args, **kwargs)


@sarus_external_op
async def pd_rename(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.rename(*args, **kwargs)


@sarus_external_op
async def pd_count(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.count(*args, **kwargs)


@sarus_external_op
async def pd_transpose(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.transpose(*args, **kwargs)


@sarus_external_op
async def pd_unique(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.unique(*args, **kwargs)


@sarus_external_op
async def pd_value_counts(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.value_counts(*args, **kwargs)


@sarus_external_op
async def pd_to_dict(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.to_dict(*args, **kwargs)


@sarus_external_op
async def pd_apply(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.apply(*args, **kwargs)


@sarus_external_op
async def pd_median(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.median(*args, **kwargs)


@sarus_external_op
async def pd_abs(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.abs(*args, **kwargs)


@sarus_external_op
async def pd_mad(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.mad(*args, **kwargs)


@sarus_external_op
async def pd_skew(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.skew(*args, **kwargs)


@sarus_external_op
async def pd_kurtosis(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.kurtosis(*args, **kwargs)


@sarus_external_op
async def pd_agg(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.agg(*args, **kwargs)


@sarus_external_op
async def pd_droplevel(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.droplevel(*args, **kwargs)


@sarus_external_op
async def pd_sort_values(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.sort_values(*args, **kwargs)


@sarus_external_op
async def pd_drop(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.drop(*args, **kwargs)


@sarus_external_op
async def pd_corr(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return parent_val.corr(*args, **kwargs)


@sarus_external_op
async def pd_get_dummies(parent_val: Any, *args: Any, **kwargs: Any) -> Any:
    assert type(parent_val) in [pd.Series, pd.DataFrame]
    return pd.get_dummies(parent_val, *args, **kwargs)


@sarus_external_op
async def pd_join(val1: Any, val2: Any) -> Any:
    return val1.join(val2)


async def pd_concat(objs: list, *args: Any, **kwargs: Any) -> Any:
    """TODO: How to input a list ?"""
    raise NotImplementedError

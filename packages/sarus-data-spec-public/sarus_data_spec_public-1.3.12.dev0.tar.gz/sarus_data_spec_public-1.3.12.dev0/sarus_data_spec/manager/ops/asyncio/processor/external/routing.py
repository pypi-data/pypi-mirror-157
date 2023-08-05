from typing import Any, AsyncIterator
import importlib
import os
import pickle as pkl

import pandas as pd
import pyarrow as pa
import yaml

from sarus_data_spec.manager.asyncio.utils import async_iter
from sarus_data_spec.transform import transform_id
import sarus_data_spec.typing as st

routing_file = os.path.join(os.path.dirname(__file__), "routing.yaml")
with open(routing_file) as f:
    routing = yaml.load(f.read(), Loader=yaml.Loader)


async def arrow_external(
    dataset: st.Dataset, batch_size: int
) -> AsyncIterator[pa.RecordBatch]:
    """Call external and convert the result to a RecordBatch iterator.

    We consider that external ops results are Datasets. For now, we consider
    that pandas.DataFrame are Datasets. For instance, the pd.loc operation only
    selects a subset of a Dataset and so is a Dataset.

    We call the implementation of `external` which returns arbitrary values,
    check that the result is indeed a DataFrame and convert it to a RecordBatch
    iterator.
    """
    val = await external(dataset)
    if isinstance(val, pd.DataFrame):
        return async_iter(
            pa.Table.from_pandas(val).to_batches(max_chunksize=batch_size)
        )

    else:
        raise TypeError(f"Cannot convert {type(val)} to Arrow batches.")


async def external(dataspec: st.DataSpec) -> Any:
    """Route an externally transformed Dataspec to its implementation."""
    transform_name = transform_id(dataspec.transform())
    library, op_name = transform_name.split(".")
    if op_name not in routing["external"][library]:
        raise NotImplementedError(
            f"Routing: {op_name} not in {list(routing['external'][library].keys())}"
        )

    transform_spec = dataspec.transform().protobuf().spec
    args = pkl.loads(transform_spec.external.arguments)
    kwargs = pkl.loads(transform_spec.external.named_arguments)

    func_name = routing["external"][library][op_name]
    module = importlib.import_module(
        f"sarus_data_spec.manager.ops.asyncio.processor.external.{library}"
    )
    func = getattr(module, func_name)

    return await func(dataspec, *args, **kwargs)

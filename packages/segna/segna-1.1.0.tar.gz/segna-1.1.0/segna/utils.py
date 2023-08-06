import json

import pandas as pd

from segna.base import SEGNA_CREDENTIALS
from functools import wraps


def dataframe_to_datatable_and_dtypes(dataframe):
    dtypes = dataframe.dtypes.apply(lambda x: x.name).to_dict()
    no_col_dataframe = dataframe.T.reset_index().T
    no_col_dataframe = no_col_dataframe.astype(str)
    json_df = no_col_dataframe.to_json(orient='values')
    return json.loads(json_df), dtypes


def datatable_and_dtypes_to_dataframe_with_index(list_data, dtypes):
    columns = list_data.pop(0)
    df = pd.DataFrame(list_data, columns=columns)
    df = df.astype(dtypes)
    df = df.set_index(df.columns[0])
    return df


def auth_check_wrapper(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if SEGNA_CREDENTIALS.access_key is None or SEGNA_CREDENTIALS.secret_key is None:
            raise ValueError('Please specify your access and secret key by calling segna.init')
        return func(*args, **kwargs)
    return inner

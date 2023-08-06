import requests
from pandas import DataFrame

from segna.base import SEGNA_CREDENTIALS, BASE_URL
import segna.platform_utils_constants as ucst
from segna.utils import dataframe_to_datatable_and_dtypes, datatable_and_dtypes_to_dataframe_with_index, \
    auth_check_wrapper


@auth_check_wrapper
def get_field_mapping(pipeline_id: str, dataframes: list[DataFrame], dataframe_names: list[str] = None,
                      sample_size: int = None):

    if pipeline_id is None:
        raise ValueError('Please specify a pipeline id')

    if dataframe_names is None:
        dataframe_names = ['df'+str(i) for i in range(0, len(dataframes))]
    else:
        if len(dataframes) != len(dataframe_names):
            raise ValueError('The number of dataframes and dataframe names do not match')

    dataframes_dict = {}
    column_dtypes_dict = {}

    for index, dataframe in enumerate(dataframes):
        datatable, df_dtypes = dataframe_to_datatable_and_dtypes(dataframe)
        dataframes_dict[dataframe_names[index]] = datatable
        column_dtypes_dict[dataframe_names[index]] = df_dtypes

    payload = {
        'dataframes': dataframes_dict,
        'column_dtypes': column_dtypes_dict,
        'pipeline_id': pipeline_id,
    }

    r = requests.post(BASE_URL + ucst.API.FIELD_MAPPING,
                      auth=(SEGNA_CREDENTIALS.access_key, SEGNA_CREDENTIALS.secret_key),
                      json=payload)
    r.raise_for_status()

    response_data = r.json()

    return response_data['input_columns'], response_data['expected_fields'], response_data['column_field_mapping']


@auth_check_wrapper
def get_data_similarity(dataframes: list[DataFrame], dataframe_names: list[str] = None, sample_size: int = None):
    if len(dataframes) < 2:
        raise ValueError('You must pass in two or more dataframes')

    if dataframe_names is None:
        dataframe_names = ['df'+str(i) for i in range(0, len(dataframes))]
    else:
        if len(dataframes) != len(dataframe_names):
            raise ValueError('The number of dataframes and dataframe names do not match')

    dataframes_dict = {}
    column_dtypes_dict = {}

    for index, dataframe in enumerate(dataframes):
        datatable, df_dtypes = dataframe_to_datatable_and_dtypes(dataframe)
        dataframes_dict[dataframe_names[index]] = datatable
        column_dtypes_dict[dataframe_names[index]] = df_dtypes

    payload = {
        'dataframes': dataframes_dict,
        'column_dtypes': column_dtypes_dict,
    }

    r = requests.post(BASE_URL + ucst.API.DATA_SIMILARITY,
                      auth=(SEGNA_CREDENTIALS.access_key, SEGNA_CREDENTIALS.secret_key),
                      json=payload)
    r.raise_for_status()

    response_data = r.json()

    data_similarity_dataframes = {}

    for data_source_id, data_similarity_mapping in response_data.items():
        data_similarity_dataframes[data_source_id] = {}
        for other_data_source_id, data_table_and_dtypes_list in data_similarity_mapping.items():
            data_similarity_dataframes[data_source_id][
                other_data_source_id] = datatable_and_dtypes_to_dataframe_with_index(
                data_table_and_dtypes_list[0], data_table_and_dtypes_list[1])

    return data_similarity_dataframes

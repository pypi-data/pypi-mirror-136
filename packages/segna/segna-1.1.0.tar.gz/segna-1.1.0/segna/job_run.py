import pandas as pd
import requests

from segna.base import SEGNA_CREDENTIALS, BASE_URL
import segna.constants as cst
from segna.job_config import JobConfig
from segna.utils import auth_check_wrapper


def configure_job(pipeline_id, job_name='temp_job') -> JobConfig:
    return JobConfig(pipeline_id, job_name)


@auth_check_wrapper
def run_job(config_obj: JobConfig) -> str:
    r = requests.post(BASE_URL + cst.API.RUN_JOB,
                      json=config_obj.to_json(),
                      auth=(SEGNA_CREDENTIALS.access_key, SEGNA_CREDENTIALS.secret_key))
    r.raise_for_status()
    job_id = r.json()[cst.Response.JOB_ID]
    return job_id


@auth_check_wrapper
def get_job_data(job_id) -> pd.DataFrame:
    payload = {cst.Request.DATA_TYPE: cst.Request.DataTypeFormats.DATAFRAME}
    r = requests.get(BASE_URL + cst.API.JOB_DATA + f'/{job_id}',
                     auth=(SEGNA_CREDENTIALS.access_key, SEGNA_CREDENTIALS.secret_key),
                     params=payload)
    response_data = r.json()
    try:
        r.raise_for_status()
    finally:
        error_message = response_data.get(cst.Response.ERROR)
        if error_message:
            print("ERROR: " + error_message)

    list_data = response_data[cst.Response.DATA]
    dtypes = response_data[cst.Response.DATA_TYPES]
    columns = list_data.pop(0)
    data = pd.DataFrame(list_data, columns=columns)
    data = data.astype(dtypes)
    return data

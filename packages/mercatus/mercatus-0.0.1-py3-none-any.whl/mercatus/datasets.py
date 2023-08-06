import logging
import os
import time

import pandas as pd


logger = logging.getLogger(__name__)

RESOURCES_ROOT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "resources")
)
logger.info(f'RESOURCES_ROOT_PATH = "{RESOURCES_ROOT_PATH}"')


def get_resource_path(sub_path):
    return os.path.join(
        RESOURCES_ROOT_PATH, sub_path.replace("{ts}", time.strftime("(%y%m%d.%H%M%S)"))
    )


def load_traces(filename=get_resource_path("traces.csv")):
    logger.info(f"Loading {filename}..")
    parsley = pd.read_csv(filename, parse_dates=["timestamp"])

    return parsley

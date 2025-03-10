import os
import time
from contextlib import contextmanager
from functools import wraps
from unittest import mock

import pytest

from unitycatalog.ai.core.base import set_uc_function_client
from unitycatalog.ai.core.databricks import DatabricksFunctionClient

USE_SERVERLESS = "USE_SERVERLESS"
TEST_IN_DATABRICKS = os.environ.get("TEST_IN_DATABRICKS", "false").lower() == "true"
WAREHOUSE_ID = os.environ.get("WAREHOUSE_ID", "warehouse_id")
PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE")


def use_serverless():
    return os.environ.get(USE_SERVERLESS, "false").lower() == "true"


def requires_databricks(test_func):
    return pytest.mark.skipif(
        not TEST_IN_DATABRICKS,
        reason="This function test relies on connecting to a databricks workspace",
    )(test_func)


# TODO: CI -- only support python 3.10, test with databricks-connect 15.1.0 + serverless
@pytest.fixture
def client() -> DatabricksFunctionClient:
    if TEST_IN_DATABRICKS:
        return DatabricksFunctionClient(warehouse_id=WAREHOUSE_ID, profile=PROFILE)
    else:
        with mock.patch(
            "unitycatalog.ai.core.databricks.get_default_databricks_workspace_client",
            return_value=mock.Mock(),
        ):
            return DatabricksFunctionClient(warehouse_id=WAREHOUSE_ID)


@pytest.fixture
def serverless_client() -> DatabricksFunctionClient:
    return DatabricksFunctionClient(profile=PROFILE)


def get_client() -> DatabricksFunctionClient:
    if TEST_IN_DATABRICKS:
        return (
            DatabricksFunctionClient(profile=PROFILE)
            if use_serverless()
            else DatabricksFunctionClient(warehouse_id=WAREHOUSE_ID, profile=PROFILE)
        )
    else:
        with mock.patch(
            "unitycatalog.ai.core.databricks.get_default_databricks_workspace_client",
            return_value=mock.Mock(),
        ):
            return (
                DatabricksFunctionClient()
                if use_serverless()
                else DatabricksFunctionClient(warehouse_id=WAREHOUSE_ID)
            )


@contextmanager
def set_default_client(client: DatabricksFunctionClient):
    try:
        set_uc_function_client(client)
        yield
    finally:
        set_uc_function_client(None)


def retry_flaky_test(tries=3):
    """Retries a flaky test a specified number of times."""

    def flaky_test_func(test_func):
        @wraps(test_func)
        def decorated_func(*args, **kwargs):
            for i in range(tries):
                try:
                    return test_func(*args, **kwargs)
                except Exception as e:
                    if i == tries - 1:
                        raise e
                    time.sleep(2)

        return decorated_func

    return flaky_test_func

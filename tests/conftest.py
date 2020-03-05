import os
import yaml

import pytest


@pytest.fixture(scope="session")
def config_dict():
    with open(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "configuration",
            f"kkr_file_system_monitor_test.yml",
        )
    ) as config_fh:
        config = yaml.load(config_fh, Loader=yaml.FullLoader)

    return config

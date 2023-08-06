# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['climetlab_maelstrom_power_production',
 'climetlab_maelstrom_power_production.constants',
 'climetlab_maelstrom_power_production.production',
 'climetlab_maelstrom_power_production.weather']

package_data = \
{'': ['*']}

install_requires = \
['climetlab>=0.11.9,<0.12.0']

extras_require = \
{'ci-tests': ['pytest-custom-exit-code>=0.3.0,<0.4.0'],
 'notebooks': ['matplotlib>=3.5.1,<4.0.0', 'scikit-learn>=1.0.2,<2.0.0']}

entry_points = \
{'climetlab.datasets': ['maelstrom-constants-a-b = '
                        'climetlab_maelstrom_power_production.constants.a_b:ABConstants',
                        'maelstrom-power-production = '
                        'climetlab_maelstrom_power_production.production.production:Production',
                        'maelstrom-weather-model-level = '
                        'climetlab_maelstrom_power_production.weather.model_level:ModelLevelWeather',
                        'maelstrom-weather-pressure-level = '
                        'climetlab_maelstrom_power_production.weather.pressure_level:PressureLevelWeather',
                        'maelstrom-weather-surface-level = '
                        'climetlab_maelstrom_power_production.weather.surface_level:SurfaceLevelWeather']}

setup_kwargs = {
    'name': 'climetlab-maelstrom-power-production',
    'version': '0.2.1',
    'description': 'CliMetLab plugin for the dataset climetlab-plugin-a6/maelstrom-production-forecasts.',
    'long_description': '## climetlab-power-production\n[![PyPI version](https://badge.fury.io/py/climetlab-maelstrom-power-production.svg)](https://badge.fury.io/py/climetlab-maelstrom-power-production)\n![workflow](https://github.com/faemmi/climetlab-plugin-a6/actions/workflows/check-and-publish.yml/badge.svg)\n[![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nA dataset plugin for climetlab for the dataset climetlab-plugin-a6/maelstrom-production-forecasts.\n\n\nFeatures\n--------\n\nIn this README is a description of how to get the CliMetLab Plugin for A6.\n\n## Installation\nVia `pip`\n```commandline\npip install climetlab-maelstrom-power-production\n```\nor via [`poetry`](https://python-poetry.org/)\n```\ngit clone git@github.com:4castRenewables/climetlab-plugin-a6.git\ncd climetlab-plugin-a6\npoetry install --no-dev\n```\n\n## Datasets description\n\nThere are five datasets:\n- `maelstrom-constants-a-b`\n- `maelstrom-power-production`\n- `maelstrom-weather-model-level`\n- `maelstrom-weather-pressure-level`\n- `maelstrom-weather-surface-level`\n\nA detailed description of each dataset (variables, meta data etc.) is available [here](https://www.maelstrom-eurohpc.eu/content/docs/uploads/doc6.pdf) (see Section 3.6).\n\n### `maelstrom-constants-a-b`\nConstants used for calculation of pressure at intermediate model levels.\n\n#### Usage\n\n```Python\nimport climetlab as cml\nproduction_data = cml.load_dataset("maelstrom-constants-a-b")\n```\n\n#### References\nIFS Documentation – Cy47r1, Operational implementation 30 June 2020, Part III: Dynamics and Numerical Procedures, ECMWF, 2020, p. 6, Eq. 2.11\n\n### `maelstrom-power-production`\nPower production data of wind turbines located in various regions of Germany.\n\nThe data were provided by [NOTUS energy GmbH & Co. KG](https://www.notus.de).\nFor a detailed description see the link above.\n\n#### Usage\n\n```Python\nimport climetlab as cml\nproduction_data = cml.load_dataset("maelstrom-power-production", wind_turbine_id=1)\n```\n\nThe `wind_turbine_id` is a number `1` to `N`, where `N` is the maximum number of currently available wind turbines.\n\nCurrently available: 45 wind turbines.\n\n### `maelstrom-weather-model-level`\n[ECMWF](https://www.ecmwf.int) IFS HRES model level data for whole Europe.\n\nFor a detailed description see the link above.\n\n#### Usage\n\n```Python\nimport climetlab as cml\nweather_ml = cml.load_dataset("maelstrom-weather-model-level", date="2019-01-01")\n```\n\nCurrently available dates:\n- `2017-01-01` until `2020-12-31`\n\n### `maelstrom-weather-pressure-level`\n[ECMWF](https://www.ecmwf.int) IF HRES pressure level data for whole Europe.\n\nFor a detailed description see the link above.\n\n#### Usage\n\n```Python\nimport climetlab as cml\nweather_pl = cml.load_dataset("maelstrom-weather-pressure-level", date="2019-01-01")\n```\n\nCurrently available dates:\n- `2017-01-01` until `2020-12-31`\n\n### `maelstrom-weather-surface-level`\n[ECMWF](https://www.ecmwf.int) IFS HRES surface level data for whole Europe.\n\nFor a detailed description see the link above.\n\n#### Usage\n\n```Python\nimport climetlab as cml\nweather_pl = cml.load_dataset("maelstrom-weather-surface-level", date="2019-01-01")\n```\n\nCurrently available dates:\n- `2017-01-01` until `2020-12-31`\n\n## Using climetlab to access the data (supports grib, netcdf and zarr)\n\nSee the demo notebooks [here](https://github.com/faemmi/climetlab-plugin-a6/tree/main/notebooks).\n\nThe climetlab python package allows easy access to the data with a few lines of code such as:\n```Python\n!pip install climetlab climetlab-maelstrom-power-production\nimport climetlab as cml\ndata = cml.load_dataset("maelstrom-power-production", date="2019-01-01")\ndata.to_xarray()\n```\n\n\n### Executing the notebooks\n\nBefore executing the notebooks, make sure to install the project and the\nnotebook dependencies correctly\n```commandline\npoetry install --extras notebooks\n```\n',
    'author': 'Fabian Emmerich',
    'author_email': 'fabian.emmerich@4-cast.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://climetlab.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)

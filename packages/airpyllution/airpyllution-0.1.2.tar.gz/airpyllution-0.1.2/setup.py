# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['airpyllution']

package_data = \
{'': ['*']}

install_requires = \
['DateTime>=4.3,<5.0',
 'altair-viewer>=0.4.0,<0.5.0',
 'altair>=4.2.0,<5.0.0',
 'mock>=4.0.3,<5.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'plotly>=5.5.0,<6.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'requests>=2.27.1,<3.0.0',
 'responses>=0.17.0,<0.18.0',
 'vega-datasets>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'airpyllution',
    'version': '0.1.2',
    'description': 'A package which  provides various functionalities on air pollution data.',
    'long_description': '# airpyllution\nA package for visualizing or obtaining future, historic and current air pollution data using the [OpenWeather API](https://openweathermap.org).\n\n## Summary\nThis package enables users to explore air pollution levels in locations around the world.\nUsing the [Air Pollution API](https://openweathermap.org/api/air-pollution), this package provides 3 functions that help to visualise present, future and historic air pollution data.  \n\nThe data returned from the API includes the polluting gases such as Carbon monoxide (CO), Nitrogen monoxide (NO), Nitrogen dioxide (NO2), Ozone (O3), Sulphur dioxide (SO2), Ammonia (NH3), and particulates (PM2.5 and PM10).\n\nUsing the OpenWeatherMap API requires sign up to gain access to an API key.   \nFor more information about API call limits and API care recommendations please visit the [OpenWeather how to start](https://openweathermap.org/appid) page.\n## Functions\nThe functions are as follows:\n- `get_air_pollution()`\n- `get_pollution_history()`\n- `get_pollution_forecast()`\n\n### `get_air_pollution()`\nFetches the air pollution levels based on a location. Based on the values of the polluting gases, this package uses the [Air Quality Index](https://en.wikipedia.org/wiki/Air_quality_index#CAQI) to determine the level of pollution for the location and produces a coloured map of the area displaying the varying regions of air quality.\n\n### `get_pollution_history()`\nRequires a start and end date and fetches historic air pollution data for a specific location. The function returns a data frame with the values of the polluting gases over the specified date range.\n\n### `get_pollution_forecast()`\nFetches air pollution data for the next 5 days for a specific location. The function returns a time series plot of the predicted pollution levels.\n\n\nAlthough there is an abundance of python weather packages and APIs in the Python ecosystem (e.g. [python-weather](https://pypi.org/project/python-weather/), [weather-forecast](https://pypi.org/project/weather-forecast/)), this particular package looks at specifically air pollution data and uses the Air Pollution API from OpenWeather. This is a unique package with functionality that (we believe) has not been made before.\n\n## Installation\n\n```bash\n$ pip install airpyllution\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\nContributors \n- Christopher Alexander (@christopheralex)\n- Daniel King (@danfke)\n- Mel Liow (@mel-liow)\n\n## License\n\n`airpyllution` was created by Christopher Alexander, Daniel King, Mel Liow. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`airpyllution` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Christopher Alexander, Daniel King, Mel Liow',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

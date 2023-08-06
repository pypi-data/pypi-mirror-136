# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ausdex', 'ausdex.seifa_vic']

package_data = \
{'': ['*'], 'ausdex.seifa_vic': ['metadata/*']}

install_requires = \
['OWSLib>=0.25.0,<0.26.0',
 'appdirs>=1.4.4,<2.0.0',
 'cached-property>=1.5.2,<2.0.0',
 'geopandas>=0.10.0,<0.11.0',
 'importlib-metadata<4.3',
 'modin>=0.10.2,<0.11.0',
 'openpyxl>=3.0.0,<4.0.0',
 'pandas>=1.3.2,<2.0.0',
 'plotly>=5.4.0,<6.0.0',
 'pygeos>=0.10.2,<0.11.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'scipy>=1.7.1,<2.0.0',
 'typer>=0.3.2,<0.4.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['ausdex = ausdex.main:app']}

setup_kwargs = {
    'name': 'ausdex',
    'version': '0.2.2',
    'description': 'An interface for several Australian socio-economic indices.',
    'long_description': '# ausdex\n\n![pipline](https://github.com/rbturnbull/ausdex/actions/workflows/coverage.yml/badge.svg)\n[<img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/49262550cc8b0fb671d46df58de213d4/raw/coverage-badge.json">](<https://rbturnbull.github.io/ausdex/coverage/>)\n[<img src="https://github.com/rbturnbull/ausdex/actions/workflows/docs.yml/badge.svg">](<https://rbturnbull.github.io/ausdex/>)\n[<img src="https://img.shields.io/badge/code%20style-black-000000.svg">](<https://github.com/psf/black>)\n\nAn interface for several Australian socio-economic indices.\n\nThe Australian Bureau of Statistics (ABS) publishes a variety of indexes for the Australian\neconomic environment. These include the Consumer Price Index (CPI) used for calculating inflation\nand a variety of indexes designed to measure socio-economic advantage. `ausdex` makes these data\navailable in a convenient Python package with a simple programatic and command line interfaces. \n\n## Installation\n\nYou can install `ausdex` from the Python Package Index (PyPI):\n\n```\npip install ausdex\n```\n\n## Command Line Usage\n\nAdjust single values using the command line interface:\n```\nausdex inflation VALUE ORIGINAL_DATE\n```\nThis adjust the value from the original date to the equivalent in today\'s dollars.\n\nFor example, to adjust $26 from July 21, 1991 to today run:\n```\n$ ausdex inflation 26 "July 21 1991" \n$ 52.35\n```\n\nTo choose a different date for evaluation use the `--evaluation-date` option. e.g.\n```\n$ ausdex inflation 26 "July 21 1991"  --evaluation-date "Sep 1999"\n$ 30.27\n```\n\n### seifa_vic command line usage\nyouc an use the seifa-vic command to interpolate an ABS census derived Socio economic score for a given year, suburb, and SEIFA metric\n```\n$ ausdex seifa-vic 2020 footscray ier_score\n$ 861.68\n\n```\n\n## Module Usage\n\n```\n>>> import ausdex\n>>> ausdex.calc_inflation(26, "July 21 1991")\n52.35254237288135\n>>> ausdex.calc_inflation(26, "July 21 1991",evaluation_date="Sep 1999")\n30.27457627118644\n```\nThe dates can be as strings or Python datetime objects.\n\nThe values, the dates and the evaluation dates can be vectors by using NumPy arrays or Pandas Series. e.g.\n```\n>>> df = pd.DataFrame(data=[ [26, "July 21 1991"],[25,"Oct 1989"]], columns=["value","date"] )\n>>> df[\'adjusted\'] = ausdex.calc_inflation(df.value, df.date)\n>>> df\n   value          date   adjusted\n0     26  July 21 1991  52.352542\n1     25      Oct 1989  54.797048\n```\n### seifa_vic submodule\n\n```python\n>>> from ausdex.seifa_vic import interpolate_vic_suburb_seifa\n>>> interpolate_vic_suburb_seifa(2007, \'FOOTSCRAY\', \'ier_score\')\n874.1489807920245\n>>> interpolate_vic_suburb_seifa([2007, 2020], \'FOOTSCRAY\', \'ier_score\', fill_value=\'extrapolate\')\narray([874.14898079, 861.68112674])\n```\n\n## Dataset and Validation\n\n### Inflation datasets\nThe Consumer Price Index dataset is taken from the [Australian Bureau of Statistics](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia). It uses the nation-wide CPI value. The validation examples in the tests are taken from the [Australian Reserve Bank\'s inflation calculator](https://www.rba.gov.au/calculator/). This will automatically update each quarter as the new datasets are released.\n\nThe CPI data goes back to 1948. Using dates before this will result in a NaN.\n\n### seifa_vic datasets\nData for the socio economic scores by suburbs comes from a variety of sources, and goes between 1986 to 2016 for the index of economic resources, and the index of education and opportunity, other indices are only available for a subset of census years\n\nWhen this module is first used, data will be downloaded and preprocessed from several locations. Access to the AURIN API is necessary via this [form](https://aurin.org.au/resources/aurin-apis/sign-up/). You will be prompted to enter the username and password when you first run the submodule. This will be saved in the app user directory for future use. You can also create a config.ini file in the repository folder with the following:\n\n```toml\n[aurin]\nusername = {aurin_api_username}\npassword = {aurin_api_password}\n```\n\n## Development\n\nTo devlop ausdex, clone the repo and install the dependencies using [poetry](https://python-poetry.org/):\n\n```\ngit clone https://github.com/rbturnbull/ausdex.git\ncd ausdex\npoetry install\n```\n\nYou can enter the environment by running:\n\n```\npoetry shell\n```\n\nThe tests can be run using `pytest`.\n\n## Credits\n\nausdex was written by [Dr Robert Turnbull](https://findanexpert.unimelb.edu.au/profile/877006-robert-turnbull) and [Dr Jonathan Garber](https://findanexpert.unimelb.edu.au/profile/787135-jonathan-garber) from the [Melbourne Data Analytics Platform](https://mdap.unimelb.edu.au/).\n\nPlease cite from the article when it is released. Details to come soon.\n\n## Acknowledgements\n\nThis project came about through a research collaboration with [Dr Vidal Paton-Cole](https://findanexpert.unimelb.edu.au/profile/234417-vidal-paton-cole) and [A/Prof Robert Crawford](https://findanexpert.unimelb.edu.au/profile/174016-robert-crawford). We acknowledge the support of our colleagues at the Melbourne Data Analytics Platform: [Dr Aleksandra Michalewicz](https://findanexpert.unimelb.edu.au/profile/27349-aleks-michalewicz) and [Dr Emily Fitzgerald](https://findanexpert.unimelb.edu.au/profile/196181-emily-fitzgerald).\n',
    'author': 'Robert Turnbull',
    'author_email': 'robert.turnbull@unimelb.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rbturnbull/ausdex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)

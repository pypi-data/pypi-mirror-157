# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['npmpy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'npmpy',
    'version': '0.1.0',
    'description': 'Curate Neurophotometrics data for pMat',
    'long_description': '# Python code for curating Neurophotometrics data\n\nThis code was written to curate [Neurophotometrics (NPM)](https://neurophotometrics.com/) data for analysis in [pMat](https://github.com/djamesbarker/pMAT). In short, the NPM data is saved into two files: one containing the 415 control signals for every region recorded and the other the 470 gcamp signals for all regions recorded. However, pMat (currently) requires the opposite: one .csv files for each region that contains both the 415 and 470 signal. This requires quite a lot of copy and pasting which is tedious and prone to errors. This code was developed to automate this process.\n\n## How to use this code?\n\nA specific file structure is necessary for using the NPM python module for curating Neurophotometric data. The below example is a minimum necessary structure for the code to work. In short, you must input a directory that contains subdirectoriesfor each subject that contain the raw NPM data files (which also need to be renamed to .NPM.csv in order to be detected).\n\n```\nData/      <---- This is the directory (path) that should be input to the curate_NPM() function. \n|-- Rat1/\n|   |-- Rat1_415_data.npm.csv\n|   |-- Rat1_470_data.npm.csv\n|-- Rat2/\n|   |-- Rat2_415_data.npm.csv\n|   |-- Rat2_470_data.npm.csv\n| ...\n|-- RatN/\n|   |-- RatN_415_data.npm.csv\n|   |-- RatN_470_data.npm.csv\n```\n\n\nFor a more general project file tree, I highly recommend something like the following to keep all of the experimental days and freezing data organized.\n\n```\nData/\n|-- Day1/          <---- This is the directory (path) that should be input to the "curated_NPM()" function. \n|   | -- Rat1/\n|   |   |-- Rat1_415_data.npm.csv\n|   |   |-- Rat1_470_data.npm.csv\n|   |   |-- Freezing data/\n|   |   |   |-- freezing_files       <---- Notice that freezing files are kept in their own folder\n|\n|-- Day2/           <---- This is the directory (path) that should be input to the "curated_NPM()" function. \n|   | -- Rat1/\n|   |   |-- Rat1_415_data.npm.csv\n|   |   |-- Rat1_470_data.npm.csv\n|   |   |-- Freezing data/\n|   |   |   |-- freezing_files\n```\n\n### General work flow\n\n1. Organize the data into the above file structure\n2. Rename all NPM data to have ".NPM.csv" at the end\n3. Open your desired IDE (jupyter, spyder, etc)\n4. Import this module \n    \n    ``` import NPMpy as NPM```\n    \n5. Run curate_NPM(path_to_your_data)\n6. Done!',
    'author': 'Michael Totty',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

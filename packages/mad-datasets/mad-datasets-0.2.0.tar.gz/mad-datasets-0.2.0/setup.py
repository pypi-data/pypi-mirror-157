# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mad_datasets',
 'mad_datasets.egait_parameter_validation_2013',
 'mad_datasets.egait_segmentation_validation_2014',
 'mad_datasets.stair_ambulation_healthy_2021',
 'mad_datasets.stair_ambulation_healthy_2021.scripts',
 'mad_datasets.utils']

package_data = \
{'': ['*']}

install_requires = \
['imucal>=2.2.1,<3.0.0',
 'joblib>=1.1.0,<2.0.0',
 'nilspodlib>=3.2.2,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'scipy>=1.8.1,<2.0.0',
 'tpcp>=0.7.0,<0.8.0']

setup_kwargs = {
    'name': 'mad-datasets',
    'version': '0.2.0',
    'description': 'Helper to access to open-source gait datasets of the MaD-Lab',
    'long_description': '[![Documentation status](https://img.shields.io/badge/docs-online-green)](https://mad-lab-fau.github.io/mad-datasets)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n# mad-datasets\n\nHelper to access to open-source gait datasets of the MaD-Lab\n\n\n## Testing\n\nThe `/tests` directory contains a set of tests to check the functionality of the library.\nHowever, most tests rely on the existence of the respective datasets in certain folders outside the library.\nTherefore, the tests can only be run locally and not on the CI server.\n\nTo run them locally, make sure datasets are downloaded into the correct folders and then run `poe test`.\n\n## Documentation (build instructions)\n\nLike the tests, the documentation requires the datasets to be downloaded into the correct folders to execute the \nexamples.\nTherefore, we can not build the docs automatically on RTD.\nInstead we host the docs via github pages.\nThe HTML source can be found in the `gh-pages` branch of this repo.\n\nTo make the deplowment as easy as possible, we "mounted" the `gh-pages` branch as a submodule in the `docs/_build/html`\nfolder.\nHence, before you attempt to build the docs, you need to initialize the submodule.\n\n```\ngit submodule update --init --recursive\n```\n\nAfter that you can run `poe docs` to build the docs and then `poe upload_docs` to push the changes to the gh-pages\nbranch.\nWe will always just update a single commit on the gh-pages branch to keep the effective file size small.\n\n**WARNING: ** Don\'t delete the `docs/_build` folder manually or by running the sphinx make file!\nThis will delete the submodule and might cause issues.\nThe `poe` task is configured to clean all relevant files in the `docs/_build` folder before each run.\n\nAfter a update of the documentation, you will see that you also need to make a commit in the main repo, as the commit \nhash of the docs submodule has changed.\n\nTo make sure you don\'t forget to update the docs, the `poe prepare_release` task will also build and upload the docs \nautomatically.',
    'author': 'Arne Küderle',
    'author_email': 'arne.kuederle@fau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mad-lab-fau/mad-datasets',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)

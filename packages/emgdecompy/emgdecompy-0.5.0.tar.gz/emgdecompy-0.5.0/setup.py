# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['emgdecompy']

package_data = \
{'': ['*']}

install_requires = \
['altair-data-server>=0.4.1,<0.5.0',
 'altair>=4.2.0,<5.0.0',
 'ipywidgets>=7.7.0,<8.0.0',
 'numpy>=1.22.3,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'panel>=0.13.1,<0.14.0',
 'scipy>=1.8.0,<2.0.0',
 'sklearn>=0.0,<0.1']

setup_kwargs = {
    'name': 'emgdecompy',
    'version': '0.5.0',
    'description': 'A package for decomposing multi-channel intramuscular and surface EMG signals into individual motor unit activity based off the blind source algorithm described in Francesco Negro et al 2016 J. Neural Eng. 13 026027.',
    'long_description': '# EMGdecomPy\n\n[![ci-cd](https://github.com/UBC-SPL-MDS/emgdecompy/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-SPL-MDS/emgdecompy/actions/workflows/ci-cd.yml)\n[![Documentation Status](https://readthedocs.org/projects/emgdecompy/badge/?version=latest)](https://emgdecompy.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/UBC-SPL-MDS/emgdecompy/branch/main/graph/badge.svg?token=78ZU40UEOE)](https://codecov.io/gh/UBC-SPL-MDS/emgdecompy)\n\nA package for decomposing multi-channel intramuscular and surface EMG signals into individual motor unit activity based off the blind source algorithm described in [`Negro et al. (2016)`](https://iopscience.iop.org/article/10.1088/1741-2560/13/2/026027/meta).\n\n## Proposal\n\nOur project proposal can be found [here](https://github.com/UBC-SPL-MDS/emg-decomPy/blob/main/docs/proposal/proposal.pdf).\n\nTo generate the proposal locally, run the following command from the root directory:\n\n```Rscript -e "rmarkdown::render(\'docs/proposal/proposal.Rmd\')"```\n\n## Installation\n\n```bash\npip install emgdecompy\n```\n\n## Usage\n\nAfter installing emgdecompy, refer to the [`EMGdecomPy` workflow notebook](https://github.com/UBC-SPL-MDS/EMGdecomPy/blob/main/notebooks/emgdecompy-worfklow.ipynb) for an example on how to use the package, from loading in the data to visualizing the decomposition results.\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`EMGdecomPy` was created by [Daniel King](github.com/danfke), [Jasmine Ortega](github.com/jasmineortega), [Rada Rudyak](github.com/Radascript), and [Rowan Sivanandam](github.com/Rowansiv). It is licensed under the terms of the GPLv3 license.\n\n## Credits\n\n`EMGdecomPy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n\nThe blind source separation algorithm in this package was based off of [`Negro et al. (2016)`](https://iopscience.iop.org/article/10.1088/1741-2560/13/2/026027/meta).\n\nThe data used for validation was obtained from [`Hug et al. (2021)`](https://figshare.com/articles/dataset/Analysis_of_motor_unit_spike_trains_estimated_from_high-density_surface_electromyography_is_highly_reliable_across_operators/13695937).\n\n[Guilherme Ricioli](https://github.com/guilhermerc) was consulted for his work on [`semg-decomposition`](https://github.com/guilhermerc/semg-decomposition).\n',
    'author': 'Daniel King',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)

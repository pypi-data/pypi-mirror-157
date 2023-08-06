# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mxfold2',
 'mxfold2.fold',
 'mxfold2.src.pybind11',
 'mxfold2.src.pybind11.docs',
 'mxfold2.src.pybind11.pybind11',
 'mxfold2.src.pybind11.tests',
 'mxfold2.src.pybind11.tests.test_cmake_build',
 'mxfold2.src.pybind11.tests.test_embed',
 'mxfold2.src.pybind11.tools',
 'mxfold2.src.pybind11.tools.clang',
 'mxfold2.utils']

package_data = \
{'': ['*'],
 'mxfold2': ['models/*', 'src/*', 'src/fold/*', 'src/param/*'],
 'mxfold2.src.pybind11': ['.github/workflows/*',
                          'include/pybind11/*',
                          'include/pybind11/detail/*'],
 'mxfold2.src.pybind11.docs': ['_static/*',
                               'advanced/*',
                               'advanced/cast/*',
                               'advanced/pycpp/*'],
 'mxfold2.src.pybind11.tests.test_cmake_build': ['installed_embed/*',
                                                 'installed_function/*',
                                                 'installed_target/*',
                                                 'subdirectory_embed/*',
                                                 'subdirectory_function/*',
                                                 'subdirectory_target/*']}

install_requires = \
['numpy>=1.18,<2.0',
 'torch>=1.4,<2.0',
 'torchvision>=0,<1',
 'tqdm>=4.40,<5.0',
 'wheel>=0.35.1,<0.36.0']

entry_points = \
{'console_scripts': ['mxfold2 = mxfold2.__main__:main']}

setup_kwargs = {
    'name': 'mxfold2',
    'version': '0.1.1',
    'description': 'RNA secondary structure prediction using deep neural networks with thermodynamic integrations',
    'long_description': "# MXfold2\nRNA secondary structure prediction using deep learning with thermodynamic integration\n\n## Installation\n\n### System requirements\n* python (>=3.7)\n* pytorch (>=1.4)\n* C++17 compatible compiler (tested on Apple clang version 12.0.0 and GCC version 7.4.0) (optional)\n* cmake (>=3.10) (optional)\n\n### Install from wheel\n\nWe provide the wheel python packages for several platforms at [the release](https://github.com/keio-bioinformatics/mxfold2/releases). You can download an appropriate package and install it as follows:\n\n    % pip3 install mxfold2-0.1.1-cp38-cp38-macosx_10_15_x86_64.whl\n\n### Install from sdist\n\nYou can build and install from the source distribution downloaded from [the release](https://github.com/keio-bioinformatics/mxfold2/releases) as follows:\n\n    % pip3 install mxfold2-0.1.1.tar.gz\n\nTo build MXfold2 from the source distribution, you need a C++17 compatible compiler and cmake.\n\n## Prediction\n\nYou can predict RNA secondary structures of given FASTA-formatted RNA sequences like:\n\n    % mxfold2 predict test.fa\n    >DS4440\n    GGAUGGAUGUCUGAGCGGUUGAAAGAGUCGGUCUUGAAAACCGAAGUAUUGAUAGGAAUACCGGGGGUUCGAAUCCCUCUCCAUCCG\n    (((((((........(((((..((((.....))))...)))))...................(((((.......)))))))))))). (24.8)\n\nBy default, MXfold2 employs the parameters trained from TrainSetA and TrainSetB (see our paper).\n\nWe provide other pre-trained models used in our paper. You can download [``models-0.1.0.tar.gz``](https://github.com/keio-bioinformatics/mxfold2/releases/download/v0.1.0/models-0.1.0.tar.gz) and extract the pre-trained models from it as follows:\n\n    % tar -zxvf models-0.1.0.tar.gz\n\nThen, you can predict RNA secondary structures of given FASTA-formatted RNA sequences like:\n\n    % mxfold2 predict @./models/TrainSetA.conf test.fa\n    >DS4440\n    GGAUGGAUGUCUGAGCGGUUGAAAGAGUCGGUCUUGAAAACCGAAGUAUUGAUAGGAAUACCGGGGGUUCGAAUCCCUCUCCAUCCG\n    (((((((.((....))...........(((((.......))))).(((((......))))).(((((.......)))))))))))). (24.3)\n\nHere, ``./models/TrainSetA.conf`` specifies a lot of parameters including hyper-parameters of DNN models.\n\n## Training\n\nMXfold2 can train its parameters from BPSEQ-formatted RNA sequences. You can also download the datasets used in our paper at [the release](https://github.com/keio-bioinformatics/mxfold2/releases/tag/v0.1.0). \n\n    % mxfold2 train --model MixC --param model.pth --save-config model.conf data/TrainSetA.lst\n\nYou can specify a lot of model's hyper-parameters. See ``mxfold2 train --help``. In this example, the model's hyper-parameters and the trained parameters are saved in ``model.conf`` and ``model.pth``, respectively.\n\n## Web server\n\nA web server is working at http://www.dna.bio.keio.ac.jp/mxfold2/.\n\n\n## References\n\n* Sato, K., Akiyama, M., Sakakibara, Y.: RNA secondary structure prediction using deep learning with thermodynamic integrations,  [preprint](https://doi.org/10.1101/2020.08.10.244442).\n",
    'author': 'Kengo Sato',
    'author_email': 'satoken@bio.keio.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/keio-bioinformatics/mxfold2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)

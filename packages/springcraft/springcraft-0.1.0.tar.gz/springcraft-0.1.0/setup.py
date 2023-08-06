# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['springcraft']

package_data = \
{'': ['*'], 'springcraft': ['data/*']}

install_requires = \
['biotite>=0.32', 'numpy>=1.15,<2.0']

setup_kwargs = {
    'name': 'springcraft',
    'version': '0.1.0',
    'description': 'Investigate molecular dynamics with elastic network models',
    'long_description': 'Springcraft\n===========\n\nThe project in the CBS Hackathon to compute *Elastic Network Models*\nwith *Biotite*.\n\nInstallation\n------------\n\nAll packages required for the development (including tests) are installed via\n\n.. code-block:: console\n\n   $ conda env create -f environment.yml\n\nif *Conda* installed.\nThe package is installed for development via\n\n.. code-block:: console\n\n   $ pip install -e .\n\nThis command requires a recent *pip* version.\n\nExample\n=======\n\n.. code-block:: python\n\n   import biotite.structure.io.mmtf as mmtf\n   import springcraft\n   import numpy as np\n   \n   \n   mmtf_file = mmtf.MMTFFile.read("path/to/1l2y.mmtf")\n   atoms = mmtf.get_structure(mmtf_file, model=1)\n   ca = atoms[(atoms.atom_name == "CA") & (atoms.element == "C")]\n   ff = springcraft.InvariantForceField()\n   hessian, pairs = springcraft.compute_hessian(ca.coord, ff, 7.0)\n   \n   np.set_printoptions(linewidth=100)\n   print(hessian)',
    'author': 'Patrick Kunzmann',
    'author_email': 'patrick.kunzm@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://springcraft.biotite-python.org',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

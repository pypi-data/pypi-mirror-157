# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kearsley', 'kearsley.tests']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.2,<2.0.0', 'pytest>=6.1.1,<7.0.0', 'scipy>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'kearsley',
    'version': '0.2.0',
    'description': 'Structural comparison of 3D points',
    'long_description': '# Kearsley algorithm\n\nThis module provides a class to perform the Kearsley algorithm for structural comparisons. The class calculates the rotation and translation that minimizes the root mean squared deviations for two sets of 3D points.\n\nOriginal paper by Simon K. Kearsley: _On the orthogonal transformation used for structural comparisons_ https://doi.org/10.1107/S0108767388010128.\n\n## Install\n\nInstall the package with:\n\n```\nuser@host:~$ pip install kearsley\n```\n\n## Usage\n\nGiven two sets of 3D points ```u``` and ```v```:\n```\n>>> u, v = read_data()\n>>> u\narray([[0, 0, 0],\n       [0, 0, 1],\n       [0, 0, 2],\n       ...,\n       [9, 9, 7],\n       [9, 9, 8],\n       [9, 9, 9]])\n>>> v\narray([[ 30.50347534, -20.16089091,  -7.42752623],\n       [ 30.77704903, -21.02339348,  -7.27823201],\n       [ 31.3215374 , -21.99452332,  -7.15703548],\n       ...,\n       [ 42.05988643, -23.50924264, -15.59516355],\n       [ 42.27217891, -24.36478643, -15.59064995],\n       [ 42.66080502, -25.27318759, -15.386241  ]])\n```\nIt is possible to calculate the rotation and translation that minimize the root mean squared deviation:\n```\n>>> from kearsley import Kearsley\n>>> k = Kearsley()\n>>> rmsd = k.fit(u, v)\n>>> rmsd\n0.10003430497284149\n```\nThe rotation and translation are the attributes of the class:\n```\n>>> k.rot.as_matrix()\narray([[ 0.05552838, -0.04405506, -0.99748471],\n       [ 0.91956342,  0.39147652,  0.03390061],\n       [ 0.38899835, -0.9191329 ,  0.06224948]])\n>>> k.trans\narray([ 30.46560753, -20.15086287,  -7.34422276])\n```\nOnce fitted you can apply the transformation to ```v``` or to other set of points:\n```\n>>> v_transform = k.transform(v)\n>>> v_transform\narray([[ 0.08563846,  0.02807207,  0.01876202],\n       [-0.01009153, -0.0529479 ,  0.92722971],\n       [-0.05796549,  0.07167779,  2.03917659],\n       ...,\n       [ 9.0219524 ,  9.067236  ,  7.08333594],\n       [ 9.06692944,  8.9276801 ,  7.95255679],\n       [ 8.92463409,  8.93635832,  8.95139744]])\n```\nIt is also possible to fit and transform with one command, in this case the transformation is applied to the second set of points:\n```\n>>> v_transform, rmsd = k.fit_transform(u, v)\n>>> rmsd\n0.10003430497284149\n>>> v_transform\narray([[ 0.08563846,  0.02807207,  0.01876202],\n       [-0.01009153, -0.0529479 ,  0.92722971],\n       [-0.05796549,  0.07167779,  2.03917659],\n       ...,\n       [ 9.0219524 ,  9.067236  ,  7.08333594],\n       [ 9.06692944,  8.9276801 ,  7.95255679],\n       [ 8.92463409,  8.93635832,  8.95139744]])\n```\nThe rmsd is the expected:\n```\n>>> np.sqrt(np.sum((u - v_transform)**2)/len(u))\n0.10003430497298871\n```\nThere are two attributes:\n\n- Kearsley.rot: a scipy Rotation instance.\n- Kearsley.trans: a ndarray with shape (3,) with the translation.\n\n\n## Applications\n\n- Compare a set of measured points with their theoretical positions.\n- In robotics compare two sets of points measured in different coordinate systems and get the transformation between both coordinate systems. \n- It is possible to use it in a 2D space fixing the third coordinate to zero.\n\n## Notes\n\nCheck [Scipy Rotation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html) to have all the info about Rotation instance.',
    'author': 'Marcelo Moreno',
    'author_email': 'marcelo.moreno.suarez@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

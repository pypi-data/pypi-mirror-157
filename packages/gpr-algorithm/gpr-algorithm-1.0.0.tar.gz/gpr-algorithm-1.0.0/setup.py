# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gpr_algorithm']

package_data = \
{'': ['*']}

install_requires = \
['deap==1.3.1',
 'geppy==0.1.3',
 'numpy==1.21.6',
 'scikit-learn==1.0.2',
 'sympy==1.9']

setup_kwargs = {
    'name': 'gpr-algorithm',
    'version': '1.0.0',
    'description': 'Gene Programming Rules (GPR) implementation',
    'long_description': "GPR Algorithm\n=============\n\nAn implementation of an extremely simple classifier (GPR_) that consists of highly interpretable fuzzy metarules\nand is suitable for many applications. GPR is effective in accuracy and area under the receiver operating characteristic\n(ROC) curve. We provide a Python implementation of the GPR algorithm to enable the use of the algorithm without using\ncommercial software tools and open access to the research community. We also added enhancements to facilitate the\nreading and interpretation of the rules.\n\n.. _GPR: https://doi.org/10.1016/j.ins.2021.05.041\n\nExample usage\n--------------\n\n.. code:: python3\n\n    import numpy as np\n    from gpr_algorithm import GPR\n\n    feature_names = ['weight', 'height']\n    target_names = ['sick', 'healthy']\n\n    cls = GPR(\n        feature_names=feature_names,\n        target_names=target_names,\n        max_n_of_rules=2, max_n_of_ands=2, n_generations=10, n_populations=10,\n        verbose=False\n    )\n\n    attributes = np.array([\n        [.9, .1],  # sick\n        [1., .9],  # sick\n        [0., .9],\n        [.1, .1]\n    ])\n    labels = np.array([\n        0,  # sick\n        0,  # sick\n        1,\n        1\n    ])\n    cls.fit(attributes, labels)\n\n    pred_labels = cls.predict(attributes)\n\n    assert np.all(labels == pred_labels)\n    rules = cls.rules\n    assert rules == ['IF weight is Low THEN healthy | Support: 0.9500', 'ELSE sick']",
    'author': 'Anna Czmil',
    'author_email': 'czmilanna@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)

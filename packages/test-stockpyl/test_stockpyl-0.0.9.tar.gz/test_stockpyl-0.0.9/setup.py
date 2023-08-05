# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['stockpyl']

package_data = \
{'': ['*'], 'stockpyl': ['aux_files/*']}

install_requires = \
['jsonpickle==2.2.0',
 'matplotlib==3.5.2',
 'networkx==2.8.2',
 'numpy==1.22.4',
 'scipy>=1.8.1,<2.0.0',
 'sphinx_rtd_theme==1.0.0',
 'tabulate==0.8.9',
 'tqdm==4.64.0']

setup_kwargs = {
    'name': 'test-stockpyl',
    'version': '0.0.9',
    'description': 'Python inventory optimization tools.',
    'long_description': 'Stockpyl\n========\n\n![PyPI](https://img.shields.io/pypi/v/stockpyl)\n[![Documentation Status](https://readthedocs.org/projects/stockpyl/badge/?version=latest)](https://stockpyl.readthedocs.io/en/latest/?badge=latest)\n![Coverage](https://raw.githubusercontent.com/LarrySnyder/stockpyl/master/coverage_badge.svg)\n![GitHub](https://img.shields.io/github/license/LarrySnyder/stockpyl)\n![GitHub issues](https://img.shields.io/github/issues/LarrySnyder/stockpyl)\n![Twitter Follow](https://img.shields.io/twitter/follow/LarrySnyder610?style=flat)\n\nStockpyl is a Python package for inventory optimization and simulation. It implements\nclassical single-node inventory models like the economic order quantity (EOQ), newsvendor,\nand Wagner-Whitin problems. It also contains algorithms for multi-echelon inventory optimization\n(MEIO) under both stochastic-service model (SSM) and guaranteed-service model (GSM) assumptions. \nAnd, it has extensive features for simulating multi-echelon inventory systems.\n\nMost of the models and algorithms implemented in Stockpyl are discussed in the textbook\n*Fundamentals of Supply Chain Theory* (*FoSCT*) by Snyder and Shen, Wiley, 2019, 2nd ed. Most of them\nare much older; see *FoSCT* for references to original sources. \n\nFor lots of details, [read the docs](http://stockpyl.readthedocs.io/).\n\nSome Examples\n-------------\n\nSolve the EOQ problem with a fixed cost of 8, a holding cost of 0.225, and a demand rate of 1300 (Example 3.1 in *FoSCT*):\n\n    >>> from stockpyl.eoq import economic_order_quantity\n    >>> Q, cost = economic_order_quantity(fixed_cost=8, holding_cost=0.225, demand_rate=1300)\n    >>> Q\n    304.0467800264368\n    >>> cost\n    68.41052550594829\n\nOr the newsvendor problem with a holding cost of 0.18, a stockout cost of 0.70, and demand that is normally\ndistributed with mean 50 and standard deviation 8 (Example 4.3 in *FoSCT*):\n\n```python    \n    >>> from stockpyl.newsvendor import newsvendor_normal\n    >>> S, cost = newsvendor_normal(holding_cost=0.18, stockout_cost=0.70, demand_mean=50, demand_sd=8)\n    >>> S\n    56.60395592743389\n    >>> cost\n    1.9976051931766445\n```\n\nNote that most functions in Stockpyl use longer, more descriptive parameter names (``holding_cost``, ``fixed_cost``, etc.)\nrather than the shorter notation assigned to them in textbooks and articles (``h``, ``K``). \n\nStockpyl can solve the Wagner-Whitin model using dynamic programming: \n\n```python\n    >>> from stockpyl.wagner_whitin import wagner_whitin\n    >>> T = 4\n    >>> h = 2\n    >>> K = 500\n    >>> d = [90, 120, 80, 70]\n    >>> Q, cost, theta, s = wagner_whitin(T, h, K, d)\n    >>> Q # Optimal order quantities\n    [0, 210, 0, 150, 0]\n    >>> cost # Optimal cost\n    1380.0\n    >>> theta # Cost-to-go function\n    array([   0., 1380.,  940.,  640.,  500.,    0.])\n    >>> s # Optimal next period to order in\n    [0, 3, 5, 5, 5]\n```\n\nAnd finite-horizon stochastic inventory problems:\n\n```python\n    >>> from stockpyl.finite_horizon import finite_horizon_dp\n    >>> T = 5\n    >>> h = 1\n    >>> p = 20\n    >>> h_terminal = 1\n    >>> p_terminal = 20\n    >>> c = 2\n    >>> K = 50\n    >>> mu = 100\n    >>> sigma = 20\n    >>> s, S, cost, _, _, _ = finite_horizon_dp(T, h, p, h_terminal, p_terminal, c, K, mu, sigma)\n    >>> s # Reorder points\n    [0, 110, 110, 110, 110, 111]\n    >>> S # Order-up-to levels\n    [0, 133.0, 133.0, 133.0, 133.0, 126.0]\n```\n\nStockpyl includes an implementation of the Clark and Scarf (1960) algorithm for stochastic serial systems (more precisely,\nChen-Zheng\'s (1994) reworking of it):\n\n```python\n    >>> from stockpyl.supply_chain_network import serial_system\n    >>> from stockpyl.ssm_serial import optimize_base_stock_levels\n    >>> # Build network.\n    >>> network = serial_system(\n    ...     num_nodes=3,\n    ...     node_order_in_system=[3, 2, 1],\n    ...     echelon_holding_cost=[4, 3, 1],\n    ...     local_holding_cost=[4, 7, 8],\n    ...     shipment_lead_time=[1, 1, 2],\n    ...     stockout_cost=40,\n    ...     demand_type=\'N\',\n    ...     mean=10,\n    ...     standard_deviation=2\n    ... )\n    >>> # Optimize echelon base-stock levels.\n    >>> S_star, C_star = optimize_base_stock_levels(network=network)\n    >>> print(f"Optimal echelon base-stock levels = {S_star}")\n    Optimal echelon base-stock levels = {3: 44.1689463285519, 2: 34.93248526934437, 1: 25.69602421013684}\n    >>> print(f"Optimal expected cost per period = {C_star}")\n    Optimal expected cost per period = 227.15328525645054\n```\n\nStockpyl has extensive features for simulating multi-echelon inventory systems. Below, we simulate\nthe same serial system, obtaining an average cost per period that is similar to what the theoretical\nmodel predicted above.\n\n```python\n    >>> from stockpyl.supply_chain_network import echelon_to_local_base_stock_levels\n    >>> from stockpyl.sim import simulation\n    >>> from stockpyl.policy import Policy\n    >>> # Convert to local base-stock levels and set nodes\' inventory policies.\n    >>> S_star_local = echelon_to_local_base_stock_levels(network, S_star)\n    >>> for n in network.nodes:\n    ...     n.inventory_policy = Policy(type=\'BS\', base_stock_level=S_star_local[n.index], node=n)\n    >>> # Simulate the system.\n    >>> T = 1000\n    >>> total_cost = simulation(network=network, num_periods=T, rand_seed=42)\n    >>> print(f"Average total cost per period = {total_cost/T}")\n    Average total cost per period = 226.16794575837224\n```\n\n\nStockpyl also implements Graves and Willems\' (2000) dynamic programming algorithm for optimizing \ncommitted service times (CSTs) in acyclical guaranteed-service model (GSM) systems:\n\n```python\n    >>> from stockpyl.gsm_tree import optimize_committed_service_times\n    >>> from stockpyl.instances import load_instance\n    >>> # Load a named instance, Example 6.5 from FoSCT.\n    >>> tree = load_instance("example_6_5")\n    >>> # Optimize committed service times.\n    >>> opt_cst, opt_cost = optimize_committed_service_times(tree)\n    >>> print(f"Optimal CSTs = {opt_cst}")\n    Optimal CSTs = {1: 0, 3: 0, 2: 0, 4: 1}\n    >>> print(f"Optimal expected cost per period = {opt_cost}")\n    Optimal expected cost per period = 8.277916867529369\n```\n\n\nResources\n---------\n\n* [PyPI](https://pypi.org/project/stockpyl/)\n* [Documentation](http://stockpyl.readthedocs.io/)\n* [Issue tracking](https://github.com/LarrySnyder/stockpyl/issues)\n\nFeedback\n--------\n\nIf you have feedback or encounter problems, please report them on the Stockpyl GitHub\n[Issues Page](https://github.com/LarrySnyder/stockpyl/issues). (If you are not comfortable\nusing GitHub for this purpose, feel free to e-mail me. My contact info is on [my webpage](https://coral.ise.lehigh.edu/larry/).)\n\nLicense\n-------\n\nStockpyl is open-source and released under the [GPLv3 License](https://choosealicense.com/licenses/gpl-3.0/).\n\nCitation\n--------\n\nIf you\'d like to cite the Stockpyl package, you can use the following BibTeX entry:\n\n```bibtex\n@misc{stockpyl,\n    title={Stockpyl},\n    author={Snyder, Lawrence V.},\n    year={2022},\n    url={https://github.com/LarrySnyder/stockpyl}\n}\n```\n\n',
    'author': 'Alex Kressner',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LarrySnyder/stockpyl',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)

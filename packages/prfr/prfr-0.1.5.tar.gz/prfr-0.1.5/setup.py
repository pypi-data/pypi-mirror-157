# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prfr']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.1.0,<2.0.0',
 'numba>=0.55.1,<0.56.0',
 'numpy<1.22',
 'scipy>=1.8.0,<2.0.0',
 'sklearn>=0.0,<0.1',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'prfr',
    'version': '0.1.5',
    'description': '',
    'long_description': '# prfr\n\nProbabilistic random forest regressor: random forest model that accounts for errors in predictors and yields calibrated probabilistic predictions.\n\n## Installation\n\n```bash\npip install prfr\n```\n\nOR\n\n```bash\npip install git+https://github.com/al-jshen/prfr\n```\n\n## Example usage\n\n```python\nimport numpy as np\nfrom prfr import ProbabilisticRandomForestRegressor, split_arrays\n\nx_obs = np.random.uniform(0., 10., size=10000).reshape(-1, 1)\nx_err = np.random.exponential(1., size=10000).reshape(-1, 1)\ny_obs = np.random.normal(x_obs, x_err).reshape(-1, 1) * 2. + 1.\ny_err = np.ones_like(y_obs)\n\ntrain, test, valid = split_arrays(x_obs, y_obs, x_err, y_err, test_size=0.2, valid_size=0.2)\n\nmodel = ProbabilisticRandomForestRegressor(n_estimators=250, n_jobs=-1)\nmodel.fit(train[0], train[1], eX=train[2], eY=train[3])\nmodel.calibrate(valid[0], valid[1], eX=valid[2], eY=valid[3], apply_bias=False)\nmodel.fit_bias(valid[0], valid[1], eX=valid[3])\n\npred = model.predict(x_test, eX=x_err_test)\npred_qtls = np.quantile(pred, [0.16, 0.5, 0.84], axis=1)\n\nprint(pred.shape)\n```\n',
    'author': 'Jeff Shen',
    'author_email': 'jshen2014@hotmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)

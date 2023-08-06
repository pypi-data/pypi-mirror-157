# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymlpipe', 'pymlpipe.utils']

package_data = \
{'': ['*'],
 'pymlpipe': ['.git/*',
              '.git/hooks/*',
              '.git/info/*',
              '.git/logs/*',
              '.git/logs/refs/heads/*',
              '.git/logs/refs/remotes/origin/*',
              '.git/objects/01/*',
              '.git/objects/1c/*',
              '.git/objects/1f/*',
              '.git/objects/22/*',
              '.git/objects/2d/*',
              '.git/objects/43/*',
              '.git/objects/4f/*',
              '.git/objects/53/*',
              '.git/objects/54/*',
              '.git/objects/5a/*',
              '.git/objects/65/*',
              '.git/objects/7f/*',
              '.git/objects/81/*',
              '.git/objects/8b/*',
              '.git/objects/9c/*',
              '.git/objects/b9/*',
              '.git/objects/cb/*',
              '.git/objects/f8/*',
              '.git/objects/pack/*',
              '.git/refs/heads/*',
              '.git/refs/remotes/origin/*',
              'static/*',
              'templates/*']}

install_requires = \
['Flask-API>=3.0.post1,<4.0',
 'Flask>=2.1.2,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'pandas>=1.4.3,<2.0.0',
 'sklearn>=0.0,<0.1']

entry_points = \
{'console_scripts': ['pymlpipeui = pymlpipe.pymlpipeUI:start_ui']}

setup_kwargs = {
    'name': 'pymlpipe',
    'version': '0.1.5',
    'description': 'PyMLpipe is a Python library for ease Machine Learning Model monitering and Deployment.',
    'long_description': '# PyMLpipe\n\nPyMLpipe is a Python library for ease Machine Learning Model monitering and Deployment.\n\n* Simple\n* Intuative\n* Easy to use\n\n\n## Installation\n\nUse the package manager [pip](https://pypi.org/project/pymlpipe/) to install PyMLpipe.\n\n```bash\npip install pymlpipe\n```\nor\n```bash\npip3 install pymlpipe\n```\n\n## Usage\n\n```python\nfrom sklearn.datasets import  load_iris\nimport pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score\n#import PyMLPipe from tabular \nfrom pymlpipe.tabular import PyMLPipe\n\n\n# Initiate the class\nmlp=PyMLPipe()\n# Set experiment name\nmlp.set_experiment("IrisDataV2")\n# Set Version name\nmlp.set_version(0.2)\n\niris_data=load_iris()\ndata=iris_data["data"]\ntarget=iris_data["target"]\ndf=pd.DataFrame(data,columns=iris_data["feature_names"])\ntrainx,testx,trainy,testy=train_test_split(df,target)\n\n\n# to start monitering use mlp.run()\nwith mlp.run():\n    # set tags\n    mlp.set_tags(["Classification","test run","logisticRegression"])\n    model=LogisticRegression()\n    model.fit(trainx, trainy)\n    predictions=model.predict(testx)\n    # log performace metrics\n    mlp.log_matric("Accuracy", accuracy_score(testy,predictions))\n    mlp.log_matric("Precision", precision_score(testy,predictions,average=\'macro\'))\n    mlp.log_matric("Recall", recall_score(testy,predictions,average=\'macro\'))\n    mlp.log_matric("F1", f1_score(testy,predictions,average=\'macro\'))\n\n    # Save train data and test data\n    mlp.register_artifact("train", trainx)\n    mlp.register_artifact("test", testx,artifact_type="testing")\n    # Save the model\n    mlp.scikit_learn.register_model("logistic regression", model)\n\n```\n\n## Usage UI\n\nTo start the UI \n\n```bash\npymlpipeui \n```\nor \n```python\nfrom pymlpipe.pymlpipeUI import start_ui\n\n\nstart_ui(host=\'0.0.0.0\', port=8085)\n```\n\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)',
    'author': 'Indresh Bhattacharya',
    'author_email': 'indresh2neel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/neelindresh/pymlpipe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

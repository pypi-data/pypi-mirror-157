# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nade', 'nade.data']

package_data = \
{'': ['*'], 'nade.data': ['socialmedia_en/*']}

install_requires = \
['fasttext>=0.9.0,<0.10.0',
 'lightgbm>=3.2,<4.0',
 'numpy>=1.19,<2.0',
 'pyarrow>=6.0.1,<7.0.0']

setup_kwargs = {
    'name': 'nade',
    'version': '0.1.1',
    'description': 'Natural affect detection allows to infer basic emotions from social media messages',
    'long_description': "# Readme\n\n**try it: [https://nade.rds.wu.ac.at](https://nade.rds.wu.ac.at)**\n\nNatural affect detection allows to infer basic emotions from social media messages. While human raters are often too resource-intensive, lexical approaches face challenges regarding incomplete vocabulary and the handling of informal language. Even advanced machine learning-based approaches require substantial resources (expert knowledge, programming skills, annotated data sets, extensive computational capabilities) and tend to gauge the mere presence, not the intensity, of emotion. This package (NADE) solves this issue by predicting a vast array of emojis based on the surrounding text, then reduces these predicted emojis to an established set of eight basic emotions.\n\n\n![Architecture](https://raw.githubusercontent.com/inkrement/nade/main/docs/overview.png)\n\n\n## Usage\nAfter installation, the module can be loaded and the predict method can be used for inference.\n\n```python\nfrom nade import Nade\n\nn = Nade()\nn.predict('I love this')\n```\n\nThe method returns a dictionary containing the scores for all eight basic emotions.\n\n```python\n{\n 'anger': [0.004],\n 'anticipation': [0.15],\n 'disgust': [0.017],\n 'fear': [0.027],\n 'joy': [0.451],\n 'sadness': [0.02],\n 'surprise': [0.142],\n 'trust': [0.242]\n}\n```\n\n## Installation\n\nThe package can be installed as follows:\n\n```bash\npip install git+git://github.com/inkrement/nade.git\n```\n\n## Performance\n\nThe prediction method features a _lleaves_ option that provides much faster inference. However, you will have to install [lleaves](https://github.com/siboehm/lleaves) first.\n\n## Links\n\n - [Nade Explorer](https://nade.rds.wu.ac.at)\n - Paper: coming soon\n",
    'author': 'Christian Hotz-Behofsits',
    'author_email': 'chris.hotz.behofsits@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://nade.rds.wu.ac.at',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

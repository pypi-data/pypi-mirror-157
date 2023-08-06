# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skipgrammar',
 'skipgrammar.datasets',
 'skipgrammar.models',
 'skipgrammar.models.lightning']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17.2,<2.0.0',
 'pandas>=1.1,<2.0',
 'pytorch-lightning>=1,<2',
 'torch>=1.4,<2.0']

setup_kwargs = {
    'name': 'skipgrammar',
    'version': '0.1.3',
    'description': 'A framework for representing sequences as embeddings.',
    'long_description': "# Skip-Grammar\nA framework for representing sequences as embeddings.\n\n## Models\n\n### Skip-gram Negative Sampling (SGNS)\n\nPopular natural language processing models such as `word2vec` and `bert` can be repurposed to learn relationships from arbitrary sequences of items. **Skip-gram Negative Sampling** is such an algorithm part of the `models` module. This is implemented in PyTorch components or can be composed as a PyTorch Lightning module. Both are availble under the relevent namespaces `skipgrammar.models.sgns` and `skipgrammar.models.lighting.sgns`.\n\n## Datasets\n\n### Last.FM\n\nThe [Last.FM Dataset-1K](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html) dataset is comprised of the listening history of approximately 1,000 users from the music service [Last.FM](https://www.last.fm/). The dataset is availble at the project's main site [here](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html) and also preprocessed [here](https://github.com/eifuentes/lastfm-dataset-1K) for ease of use. The variants in the `dataset` module use the latter.\n\n### MovieLens\n\nThe popular recommendation system dataset [MovieLens](https://grouplens.org/datasets/movielens/) is availble in three variants via the `dataset` module.\n",
    'author': 'Emmanuel Fuentes',
    'author_email': 'emmanuel.i.fuentes+pypi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eifuentes/skipgrammar',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<3.10',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coco_toolkit',
 'coco_toolkit.convertors',
 'coco_toolkit.helper',
 'coco_toolkit.modules']

package_data = \
{'': ['*']}

install_requires = \
['addict>=2.4.0,<3.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pre-commit>=2.19.0,<3.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'coco-toolkit',
    'version': '0.1.0',
    'description': 'A Reporer Everyting for traninig CocoDataset',
    'long_description': '## Introduction\nCoco-toolkit is a tool for preparing and analyzing object detection data which is coco json format in Python. Tool countains merge, preprocessing, report and converter modules.\n\n1 - Preprocessing\nThis class obtain preprocess functions for preparing coco json dataset.\n\n2 - Converter\nThis module has converters functions which are Pascal voc to coco json and coco json to tfrecords.\n\n3 - Merge\nMerge module has multiple coco merge function.\nIt merges all given coco json file and return all in one output folder.\n\n4- Report\nReport module has analyze dataset functions. These functions are; return information of data set, plots data set information as pie chart, and integrates data set with coco viewer.\n\n### System requirements\n### Installation\n## Basic usage\n\n###  1 - Import\n##### 1.1 -Import preprocess\nfrom coco_toolkit.helper.preprocess import PreProcess\n##### 1.2 -Import merge\nfrom coco_toolkit.helper.merge import merge_multiple_cocos\n##### 1.2 -Import report\nfrom coco_toolkit.helper.report import AnalyzeCategories\n###  2 - Sample usage\n##### 2.1 - Usage filter class\nThis function filter given class names. It returns filtered coco json as dictionary and saves filtered coco json file and filtered images in new folder.\n`\nPreProcess(path).export_according2_class(coco, categories, image_path)`\n\n\nparameter path : This parameter is directory of output.Function saves\nfiltered dataset in this path.\n\nparameter coco : Coco json file as read dictionary\n\nparameter categories : List of to be filtered class names\n\nparameter image_path: Dataset images folder path\n\n`\ncoco = PreProcess(path to coco json file).reader()\n`\n`\nPreProcess(path).export_according2_class(coco, ["human", "car"], "/home/user/data/images")\n`\n\n## Check before PR \n\n```bash\nblack . --config pyproject.toml\nisort .\npre-commit run --all-files\n\n\n```',
    'author': 'mcvarer',
    'author_email': 'murat@visiosoft.com.tr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

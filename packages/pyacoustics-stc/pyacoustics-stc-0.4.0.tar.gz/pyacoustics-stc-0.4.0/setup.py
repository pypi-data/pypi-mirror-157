# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyacoustics_stc']

package_data = \
{'': ['*']}

install_requires = \
['kaleido==0.2.1', 'pandas>=1.4.3,<2.0.0', 'plotly>=5.9.0,<6.0.0']

setup_kwargs = {
    'name': 'pyacoustics-stc',
    'version': '0.4.0',
    'description': 'The Python library for Sound Transmission Class (STC) calculation',
    'long_description': '# pyacoustics-stc\nThe Python library for Sound Transmission Class (STC) calculation\n\n## Installation\n```\npip install pyacoustics-stc\n```\n## Quickstart\n-----\n### Calculate STC\n```py\nfrom pyacoustics_stc import SoundTransmissionClass\n\n# sound transmission loss as dict object {Frequency : Value}\nstl = {\n    125: 11.66, 160: 13.303, 200: 14.825, 250: 20.861,\n    315: 22.868,400: 24.943, 500: 26.881, 630: 28.889,\n    800: 30.964, 1000: 32.902,1250: 34.84,1600: 36.984,\n    2000: 38.923, 2500: 40.861, 3150: 27.557, 4000: 30.67,\n}\n\nstc = SoundTransmissionClass(stl=stl)\n\nstc.index\n# 29\nstc.deficiency\n# 25.579\nstc.contour\n# {125: 13, 160: 16, 200: 19, 250: 22, 315: 25, 400: 28, 500: 29, 630: 30, 800: 31, 1000: 32, 1250: 33, 1600: 33, 2000: 33, 2500: 33, 3150: 33, 4000: 33}\nstc.delta\n# {125: 1.34, 160: 2.697, 200: 4.175, 250: 1.139, 315: 2.132, 400: 3.057, 500: 2.119, 630: 1.111, 800: 0.036, 1000: 0, 1250: 0, 1600: 0, 2000: 0, 2500: 0, 3150: 5.443, 4000: 2.33}\n\n```\n### Visualization\n```py\nstc.plot() # display result as graph\n```\nInteractive Graph by [Plotly](https://plotly.com/)\n\n![Interactive Graph on Browser](https://raw.githubusercontent.com/bozzlab/pyacoustics-stc/main/graph_on_browser.png)\n\n### Static File Export\n\n```py\nstc.export_graph_to_file("stc.png") # save graph result as PNG image file\nstc.export_graph_to_file("stc.jpeg") # save graph result as JPEG image file\nstc.export_graph_to_file("stc.pdf") # save graph result as PDF file\n\n# <your_local_path>/stc.png\n```\n![Sound Transimission Class Graph](https://raw.githubusercontent.com/bozzlab/pyacoustics-stc/main/stc.png)\n\n\n### Utils \n```py\nfrom pyacoustics_stc.utils import build_frequency_stl_map\n\nstl_without_key = [\n    22.49669, 27.85324, 32.77704, 46.30192, \n    52.32415, 58.54912, 64.36372, 70.38595, \n    76.61092, 82.80217, 87.39175, 92.54538, \n    97.27899, 70.36132, 77.44058, 84.8613\n]\nstl = build_frequency_stl_map(stl_without_key)\n\nstl\n# {125: 22.49669, 160: 27.85324, 200: 32.77704, 250: 46.30192, 315: 52.32415, 400: 58.54912, 500: 64.36372, 630: 70.38595, 800: 76.61092, 1000: 82.80217, 1250: 87.39175, 1600: 92.54538, 2000: 97.27899, 2500: 70.36132, 3150: 77.44058, 4000: 84.8613}\n\n```\n\n## Testing\n```\npython -m pytest\n```\n\n## Formatter\n```\nblack pyacoustics_stc \n```',
    'author': 'Peem Srinikorn (Bozzlab)',
    'author_email': 'peemsrinikorn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bozzlab/pyacoustics-stc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gp32_transfer', 'gp32_transfer.utils']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.5,<2.0.0', 'pyserial==3.5', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['gp32_transfer = gp32_transfer.main:app']}

setup_kwargs = {
    'name': 'gp32-transfer',
    'version': '0.2.1',
    'description': '',
    'long_description': '<div id="top"></div>\n<!--\n*** Thanks for checking out the Best-README-Template. If you have a suggestion\n*** that would make this better, please fork the repo and create a pull request\n*** or simply open an issue with the tag "enhancement".\n*** Don\'t forget to give the project a star!\n*** Thanks again! Now go create something AMAZING! :D\n-->\n\n<!-- PROJECT SHIELDS -->\n<!--\n*** I\'m using markdown "reference style" links for readability.\n*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).\n*** See the bottom of this document for the declaration of the reference variables\n*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.\n*** https://www.markdownguide.org/basic-syntax/#reference-style-links\n-->\n<!--\n[![Contributors][contributors-shield]][contributors-url]\n[![Forks][forks-shield]][forks-url]\n[![Stargazers][stars-shield]][stars-url]\n[![Issues][issues-shield]][issues-url]\n[![MIT License][license-shield]][license-url]\n[![LinkedIn][linkedin-shield]][linkedin-url] -->\n\n<!-- PROJECT LOGO -->\n<br />\n<div align="center">\n\n<h3 align="center">GP32 GPS Communication 3000</h3>\n<!-- \n  <p align="center">\n    Interface which can save and upload waypoint to Furuno GP32 using RS232\n    <br />\n    <a href="https://github.com/pepin_nucleaire/furuno-gpx-transfer"><strong>Explore the docs »</strong></a>\n    <br />\n    <br />\n    <a href="https://github.com/pepin_nucleaire/furuno-gpx-transfer">View Demo</a>\n    ·\n    <a href="https://github.com/pepin_nucleaire/furuno-gpx-transfer/issues">Report Bug</a>\n    ·\n    <a href="https://github.com/pepin_nucleaire/furuno-gpx-transfer/issues">Request Feature</a>\n  </p>-->\n</div>\n\n<!-- TABLE OF CONTENTS -->\n<!-- <details>\n  <summary>Table of Contents</summary>\n  <ol>\n    <li>\n      <a href="#about-the-project">About The Project</a>\n      <ul>\n        <li><a href="#built-with">Built With</a></li>\n      </ul>\n    </li>\n    <li>\n      <a href="#getting-started">Getting Started</a>\n      <ul>\n        <li><a href="#prerequisites">Prerequisites</a></li>\n        <li><a href="#installation">Installation</a></li>\n      </ul>\n    </li>\n    <li><a href="#usage">Usage</a></li>\n    <li><a href="#roadmap">Roadmap</a></li>\n    <li><a href="#contributing">Contributing</a></li>\n    <li><a href="#license">License</a></li>\n    <li><a href="#contact">Contact</a></li>\n    <li><a href="#acknowledgments">Acknowledgments</a></li>\n  </ol>\n</details> -->\n\n<!-- GETTING STARTED -->\n\n## Getting Started\n\nThis is an example of how you may give instructions on setting up your project locally.\nTo get a local copy up and running follow these simple example steps.\n\n### Installation\n\n<!-- USAGE EXAMPLES -->\n\n## Usage\n\n<!-- ROADMAP -->\n\n## Roadmap\n\n- [x] ~~Save waypoints~~\n  - [x] ~~Read from GP32~~\n  - [x] ~~Save to GPX file compatible with OpenCPN~~\n- [] Upload Waypoints\n  - [x] ~~Convert GPX to NMEA~~\n  - [x] ~~Upload NMEA to GP32~~\n- [x] Make a nice app\n  - [x] CLI\n  - [] Web-based ?\n  - [] Click-n-go ?\n\nSee the [open issues](https://github.com/pepin_nucleaire/furuno-gpx-transfer/issues) for a full list of proposed features (and known issues).\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n<!-- CONTRIBUTING -->\n\n## Contributing\n\nContributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.\n\nIf you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".\nDon\'t forget to give the project a star! Thanks again!\n\n1. Fork the Project\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Pull Request\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n<!-- LICENSE -->\n\n## License\n\nDistributed under the MIT License. See `LICENSE.txt` for more information.\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n<!-- CONTACT -->\n\n## Contact\n\nYour Name - [@juju_on_mini](https://twitter.com/juju_on_mini) - muller.julien.02@gmail.com.com\n\nProject Link: [https://github.com/pepin_nucleaire/furuno-gpx-transfer](https://github.com/pepin_nucleaire/furuno-gpx-transfer)\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n<!-- ACKNOWLEDGMENTS -->\n\n## Acknowledgments\n\n- [russkiy78 and it furunotogpx project](https://github.com/russkiy78/furunotogpx) that I used as a really big inspiration\n- My dog\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n<!-- MARKDOWN LINKS & IMAGES -->\n<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->\n',
    'author': 'Julien Muller',
    'author_email': 'muller.julien.02@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hoymiles_mqtt', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['ConfigArgParse>=1.5.3,<2.0.0',
 'hoymiles-modbus==0.4.0',
 'paho-mqtt>=1.6.1,<2.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.15.2,<0.16.0',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['black==22.3.0',
          'isort>=5.8.0,<6.0.0',
          'flake8>=3.9.2,<4.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.900,<0.901',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=2.12.0,<3.0.0']}

setup_kwargs = {
    'name': 'hoymiles-mqtt',
    'version': '0.2.0',
    'description': 'Send data from Hoymiles photovoltaic installation to MQTT server.',
    'long_description': "# Hoymiles MQTT\n\n\n[![pypi](https://img.shields.io/pypi/v/hoymiles-mqtt.svg)](https://pypi.org/project/hoymiles-mqtt/)\n[![python](https://img.shields.io/pypi/pyversions/hoymiles-mqtt.svg)](https://pypi.org/project/hoymiles-mqtt/)\n[![Build Status](https://github.com/wasilukm/hoymiles-mqtt/actions/workflows/dev.yml/badge.svg)](https://github.com/wasilukm/hoymiles-mqtt/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/wasilukm/hoymiles-mqtt/branch/main/graphs/badge.svg)](https://codecov.io/github/wasilukm/hoymiles-mqtt)\n\n\n\nSend data from Hoymiles photovoltaic installation to Home Assistant through MQTT broker.\n\n* GitHub: <https://github.com/wasilukm/hoymiles-mqtt>\n* PyPI: <https://pypi.org/project/hoymiles-mqtt/>\n* Free software: MIT\n\nThe tool periodically communicates with Hoymiles DTU trough ModbusTCP and sends gathered data to MQTT broker.\nData to MQTT broker are sent with topics that can be recognized by Home Assistant.\nIn a result DTU and each micro-inverter can be represented in Home Assistant as a separate device with set of entities. Example:\n\n![MQTT Devices](/docs/mqtt_devices.png)\n\n![MQTT Entities](/docs/mqtt_entities.png)\n\nDTU device represent overall data for the installation:\n- pv_power - current power - sum from all micro-inverters\n- today_production - today energy production - sum from all micro-inverters, for each micro-inverter last known\n  good value is cached to prevent disturbances in statistics when part of the installation is temporarily off\n  or off-line. This entity can be used in Home Assistant energy panel as a production from solar panels.\n  An example chart:\n\n  ![Solar production](/docs/solar%20production.png)\n- total_production - lifetime energy production - sum from all micro-inverters\n\nEach micro-inverter has the following entities:\n- port_number\n- pv_voltage\n- pv_current\n- grid_voltage\n- grid_frequency\n- pv_power\n- today_production\n- total_production\n- temperature\n- operating_status\n- alarm_code\n- alarm_count\n- link_status\n\nDepending on the installation (number of micro-inverter), the tool may create many entities. One may limit the entities\nor with the option _--mi-entities_.\n\n## Usage\n\n### Prerequisites\n- DTUs' _Ethernet_ port connected to a network\n- DTU has assigned IP address by DHCP server. IP address shall be reserved for the device\n- running MQTT broker, for example https://mosquitto.org/\n- MQTT integration enabled in Home Assistant, https://www.home-assistant.io/integrations/mqtt/\n\n### From command line\n    usage: python3 -m hoymiles_mqtt [-h] [-c CONFIG] --mqtt-broker MQTT_BROKER [--mqtt-port MQTT_PORT] [--mqtt-user MQTT_USER] [--mqtt-password MQTT_PASSWORD] --dtu-host DTU_HOST [--dtu-port DTU_PORT]\n                                    [--modbus-unit-id MODBUS_UNIT_ID] [--query-period QUERY_PERIOD] [--microinverter-type {MI,HM}] [--mi-entities MI_ENTITIES [MI_ENTITIES ...]]\n\n    options:\n      -h, --help            show this help message and exit\n      -c CONFIG, --config CONFIG\n                            Config file path (default: None)\n      --mqtt-broker MQTT_BROKER\n                            Address of MQTT broker [env var: MQTT_BROKER] (default: None)\n      --mqtt-port MQTT_PORT\n                            MQTT broker port [env var: MQTT_PORT] (default: 1883)\n      --mqtt-user MQTT_USER\n                            User name for MQTT broker [env var: MQTT_USER] (default: None)\n      --mqtt-password MQTT_PASSWORD\n                            Password to MQTT broker [env var: MQTT_PASSWORD] (default: None)\n      --dtu-host DTU_HOST   Address of Hoymiles DTU [env var: DTU_HOST] (default: None)\n      --dtu-port DTU_PORT   DTU modbus port [env var: DTU_PORT] (default: 502)\n      --modbus-unit-id MODBUS_UNIT_ID\n                            Modbus Unit ID [env var: MODBUS_UNIT_ID] (default: 1)\n      --query-period QUERY_PERIOD\n                            How often (in seconds) DTU shall be queried. [env var: QUERY_PERIOD] (default: 60)\n      --microinverter-type {MI,HM}\n                            Type od microinverters in the installation. Mixed types are not supported. [env var: MICROINVERTER_TYPE] (default: MI)\n      --mi-entities MI_ENTITIES [MI_ENTITIES ...]\n                            Microinverter entities that will be sent to MQTT. By default all entities are presented. [env var: MI_ENTITIES] (default: ['port_number', 'pv_voltage', 'pv_current', 'grid_voltage',\n                            'grid_frequency', 'pv_power', 'today_production', 'total_production', 'temperature', 'operating_status', 'alarm_code', 'alarm_count', 'link_status'])\n\n    Args that start with '--' (eg. --mqtt-broker) can also be set in a config file (specified via -c). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). If an\n    arg is specified in more than one place, then commandline values override environment variables which override config file values which override defaults.\n\n### Docker\n\nBuild an image\n\n    docker build https://github.com/wasilukm/hoymiles-mqtt.git#v0.1.0 -t hoymiles_mqtt\n\nRun (replace IP addresses)\n\n    docker run -d -e MQTT_BROKER=192.168.1.101 -e DTU_HOST=192.168.1.100 hoymiles_mqtt\n\nPlease note, depending on the needs more options can be specified with _-e_. See above for all possible options.\n\n## Known issues\nHoymiles DUTs are not the most stable devices. Therefore, from time to time the tool may not be able to connect to DTU\nand will print the following exception:\n\n    Modbus Error: [Invalid Message] No response received, expected at least 8 bytes (0 received)\n\nThe tool will continue its operation and try communication with DTU with the next period.\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n",
    'author': 'Foo Bar',
    'author_email': 'foo@bar.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wasilukm/hoymiles-mqtt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wizwalker',
 'wizwalker.extensions.wizsprinter',
 'wizwalker.extensions.wizsprinter.combat_backends']

package_data = \
{'': ['*']}

install_requires = \
['lark>=0.11.3,<0.12.0', 'wizwalker>=1.0.0']

setup_kwargs = {
    'name': 'wizsprinter',
    'version': '0.5.5',
    'description': 'A semi-official WizWalker extension',
    'long_description': 'WizSprinter is a semi-official extension to the `WizWalker library <https://github.com/StarrFox/wizwalker>`_.\n\nIt adds:\n\nWizSprinter (WizWalker extension):\n    - upgrade_clients\n    - extended get_new_clients\n    - extended remove_dead_clients\n    - extended get_ordered_clients\n\nSprintyClient (Client extension):\n    - better teleport\n    - get_base_entities_with_vague_name\n    - get_base_entities_with_behaviors\n    - get_health_wisps\n    - get_mana_wisps\n    - get_mobs\n    - find_safe_entities_from\n    - find_closest_of_entities\n    - find_closest_by_predicate\n    - find_closest_by_name\n    - find_closest_by_vague_name\n    - find_closest_health_wisp\n    - find_closest_mana_wisp\n    - find_closest_mob\n    - tp_to_closest_of\n    - tp_to_closest_by_name\n    - tp_to_closest_by_vague_name\n    - tp_to_closest_health_wisp\n    - tp_to_closest_mana_wisp\n    - tp_to_closest_mob\n    - calc_health_ratio\n    - calc_mana_ratio\n    - has_potion\n    - use_potion\n    - needs_potion\n    - use_potion_if_needed\n\nSprintyCombat (Implementation of a CombatHandler):\n    - CombatConfigProvider to parse a config file\n    - Full CombatHandler with some logic',
    'author': 'SirOlaf',
    'author_email': 'sirolaf@protonmail.com',
    'maintainer': 'CowHunter0',
    'maintainer_email': 'cowhunter04@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

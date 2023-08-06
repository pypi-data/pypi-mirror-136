# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dooti']

package_data = \
{'': ['*']}

install_requires = \
['click>=7,<8',
 'pyobjc-core>=7.2,<8.0',
 'pyobjc-framework-UniformTypeIdentifiers>=7.2,<8.0']

entry_points = \
{'console_scripts': ['dooti = dooti.cli:cli']}

setup_kwargs = {
    'name': 'dooti',
    'version': '0.0.1',
    'description': 'Sets default file and URL scheme handlers on macOS  12.0+',
    'long_description': '=====\ndooti\n=====\n\nSet default handlers for files and URL schemes on MacOS 12.0+.\n\nWhy?\n----\nMost existing tools use `LSSetDefaultRoleHandlerForContentType <https://developer.apple.com/documentation/coreservices/1447588-lssethandleroptionsforcontenttyp?language=objc>`_ and `LSSetDefaultHandlerForURLScheme <https://developer.apple.com/documentation/coreservices/1447760-lssetdefaulthandlerforurlscheme?language=objc>`_, which are deprecated and apparently only available up to macOS 12.0. ``dooti`` uses a different API and should work on Monterey (12.0) and above.\n\nLimitations\n-----------\n* This tool was built out of necessity for myself and is not battle-tested.\n* The CLI interface is very spartan currently, including not being very talkative and not catching exceptions.\n* The designated handler has to be installed before running the command for this to work at all.\n* Setting some URL scheme handlers (especially for http) might cause a prompt.\n* Setting some file extension handlers might be restricted (especially html seems to fail silently).\n\nInstallation\n------------\nI recommend installing with `pipx <https://pypa.github.io/pipx/>`_, although pip will work fine as well:\n\n.. code-block:: bash\n\n        pipx install dooti\n\nQuickstart\n----------\n``dooti`` currently supports three commands:\n\next\n    specify handlers for file extensions (will be automapped to associated UTI)\nscheme\n    specify handlers for URL schemes\nuti\n    specify handlers for specific UTI\n\nThe first argument is always the target file extension / URL scheme / UTI. This allows you to inspect the current handlers for the specific target:\n\n.. code-block:: console\n\n    $ dooti ext html\n    /Applications/Firefox.app\n    $ dooti scheme http\n    /Applications/Firefox.app\n    $ dooti uti public.html\n    /Applications/Firefox.app\n\nWhen you want to change a setting, you need to specify the second argument, which is the default handler to set. The following three formats are supported:\n\n* name of application:\n\n    .. code-block:: bash\n\n        dooti ext csv "Sublime Text"\n\n* absolute filesystem path:\n\n    .. code-block:: bash\n\n        dooti scheme http "/Applications/Firefox.app"\n\n* bundle ID\n\n    .. code-block:: bash\n\n        dooti uti py com.sublimetext.4\n\n\nSimilar tools\n-------------\n* `duti <https://github.com/moretension/duti>`_\n* `openwith <https://github.com/jdek/openwith>`_\n* `defaultbrowser <https://gist.github.com/miketaylr/5969656>`_\n* `SwiftDefaultApps <https://github.com/Lord-Kamina/SwiftDefaultApps>`_\n',
    'author': 'jeanluc',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lkubb/dooti',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

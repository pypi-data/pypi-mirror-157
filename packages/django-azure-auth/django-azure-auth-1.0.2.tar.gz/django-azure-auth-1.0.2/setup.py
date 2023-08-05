# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['azure_auth', 'azure_auth.tests']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2', 'msal>=1.18.0,<2.0.0']

setup_kwargs = {
    'name': 'django-azure-auth',
    'version': '1.0.2',
    'description': 'A simple Django app for user authentication with Azure Active Directory.',
    'long_description': '![Build](https://github.com/AgileTek/django-azure-auth/actions/workflows/push-actions.yml/badge.svg)\n\n# Django Azure Auth\nA simple Django app for user authentication with Azure Active Directory.\n\n## Description\n`django-azure-auth` is a Django app which wraps the great [MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-python)\npackage to enable authentication against Microsoft\'s Azure Active Directory in Django projects.\n\nThe app includes `login`, `logout` and `callback` authentication views, a decorator\nto protect individual views, and middleware which allows the entire site to require user \nauthentication by default, with the ability to exempt specified views.\n\nThis project is in no way affiliated with Microsoft.\n\n## Installation\nFrom PyPi:\n```bash\npip install django-azure-auth\n```\n\n## Configuration\n### Azure setup\n- Register an app at https://portal.azure.com/.\n- Add a client secret and note it down.\n- Add a redirect URI of the format `https://<domain>/azure_auth/callback`.\n\n### Settings\nAdd the following to your `settings.py`, replacing the variables in braces with the values\nfrom your Azure app: \n```python\nAZURE_AUTH = {\n    "CLIENT_ID": "<client id>",\n    "CLIENT_SECRET": "<client secret>",\n    "REDIRECT_URI": "https://<domain>/azure_auth/callback",\n    "SCOPES": ["User.Read"],\n    "AUTHORITY": "https://login.microsoftonline.com/<tenant id>",   # Or https://login.microsoftonline.com/common if multi-tenant\n    "LOGOUT_URI": "https://<domain>/logout",    # Optional\n    "PUBLIC_URLS": ["<public:view_name>",]  # Optional, public views accessible by non-authenticated users\n}\nLOGIN_URL = "/azure_auth/login"\nLOGIN_REDIRECT_URL = "/"    # Or any other endpoint\n```\n#### Note: You should obfuscate the credentials by using environment variables.\n\n### Installed apps\nAdd the following to your `INSTALLED_APPS`:\n```python\nINSTALLED_APPS = (\n    "...",\n    "azure_auth",\n    "..."\n)\n```\n\n### Authentication backend\nConfigure the authentication backend:\n```python\nAUTHENTICATION_BACKENDS = ("azure_auth.backends.AzureBackend",)\n```\n\n### URLs\nInclude the app\'s URLs in your `urlpatterns`:\n```python\nfrom django.urls import path, include\n\nurlpatterns = [\n    path("azure_auth/", include("azure_auth.urls"),),\n]\n```\n\n## Usage\n### Decorator\nTo make user authentication a requirement for accessing an individual view, decorate the\nview like so:\n```python\nfrom azure_auth.decorators import azure_auth_required\nfrom django.shortcuts import HttpResponse\n\n@azure_auth_required\ndef protected_view(request):\n    return HttpResponse("A view protected by the decorator")\n```\n\n### Middleware\nIf you want to protect your entire site by default, you can use the middleware by adding the \nfollowing to your `settings.py`:\n```python\nMIDDLEWARE = [\n    "...",\n    "azure_auth.middleware.AzureMiddleware",\n    "...",\n]\n```\nMake sure you add the middleware after Django\'s `session` and `authentication` middlewares so \nthat the request includes the session and user objects. Public URLs which need to be accessed by \nnon-authenticated users should be specified in the `settings.AZURE_AUTH["PUBLIC_URLS"]`, as \nshown above.\n\n## Planned development\n- Groups management\n\n## Credits\nThis app is heavily inspired by and builds on functionality in \nhttps://github.com/shubhamdipt/django-microsoft-authentication, with both feature \nimprovements and code assurance through testing.\n\nCredit also to:\n- https://github.com/Azure-Samples/ms-identity-python-webapp\n- https://github.com/AzMoo/django-okta-auth',
    'author': 'AgileTek Engineering',
    'author_email': 'london@agiletek.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AgileTek/django-azure-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

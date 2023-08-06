# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cortex_xdr_client', 'cortex_xdr_client.api', 'cortex_xdr_client.api.models']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'cortex-xdr-client',
    'version': '1.5.1',
    'description': 'API client for Cortex XDR Prevent',
    'long_description': 'About the cortex-xdr-client\n###########################\n\nA python-based API client for `Cortex XDR\nAPI <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api>`__.\n\nCurrently, it supports the following Cortex XDR **Prevent & Pro** APIs:\n\n*Incidents API:*\n\n-  `Get\n   Incidents <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/incident-management/get-incidents.html>`__\n-  `Get Extra Incident\n   Data <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/incident-management/get-extra-incident-data.html>`__\n\n\n*Alerts API:*\n\n-  `Get\n   Alerts <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/incident-management/get-alerts.html>`__\n\n\n*Endpoints API:*\n\n-  `Get All\n   Endpoints <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/endpoint-management/get-all-endpoints.html>`__\n-  `Get\n   Endpoint <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/endpoint-management/get-endpoints.html>`__\n-  `Isolate\n   Endpoints <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/response-actions/isolate-endpoints.html>`__\n-  `Scan\n   Endpoints <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/response-actions/scan-endpoints.html>`__\n-  `Retrieve\n   File <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/response-actions/retrieve-file.html>`__\n\n\n*XQL API:*\n\n-  `Start\n   XQL <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/xql-apis/start-xql-query.html>`__\n-  `Get XQL\n   Results <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/xql-apis/get-xql-query-results.html>`__\n-  `Get XQL Result\n   Stream <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/xql-apis/get-xql-query-exported-data.html>`__\n\n\n*Scripts API:*\n\n-  `Get\n   Scripts <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/script-execution/get-scripts.html>`__\n-  `Get Script\n   Metadata <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/script-execution/get-script-metadata.html>`__\n-  `Get Script Execution\n   Status <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/script-execution/get-script-execution-status.html>`__\n-  `Get Script Execution\n   Results <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/script-execution/get-script-execution-results.html>`__\n-  `Get Script Execution Result\n   Files <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/script-execution/get-script-execution-result-files.html>`__\n-  `Run\n   Script <https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/script-execution/run-script.html>`__\n\n\n*Contributing:*\n\nSee `CONTRIBUTING.md <./CONTRIBUTING.md>`__ for details.\n',
    'author': 'ebarti',
    'author_email': 'me@eloibarti.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ebarti/cortex-xdr-client',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

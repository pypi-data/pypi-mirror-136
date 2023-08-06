# Signadot Python SDK

## Installation
Install the package using the below command:
```sh
pip3 install signadot-sdk
```

Or add as a dependency to `requirements.txt` as:
```python
signadot-sdk==0.1.0
```

Then run:
```sh
pip3 install -r requirements.txt
```

## Sample Usage

```python
from __future__ import print_function
import time
import signadot_sdk
from signadot_sdk.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = signadot_sdk.Configuration()
configuration.api_key['signadot-api-key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['signadot-api-key'] = 'Bearer'

# create an instance of the API class
api_instance = signadot_sdk.ClusterApi(signadot_sdk.ApiClient(configuration))
org_name = 'my-company' # str | Signadot Org Name
data = signadot_sdk.ConnectClusterRequest() # ConnectClusterRequest | Request to create cluster

try:
    # Connect Cluster
    api_response = api_instance.connect_cluster(org_name, data)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ClusterApi->connect_cluster: %s\n" % e)

```

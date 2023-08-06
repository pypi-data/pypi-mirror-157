class CertificateError(Exception):
    pass


def get_etfs(verify='path/to/consolidate.pem'):
    '''Devuelve un DataFrame con todos los ETFs que cotizan en ARG.
    El parámetro verify define si se utiliza un certificado SSL para la conexión. Definirlo como False implica exponer vulnerabilidades en la conexión (https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror).
    Para evitar esto, es necesario generar el archivo .pem utilizando OpenSSL (https://levelup.gitconnected.com/solve-the-dreadful-certificate-issues-in-python-requests-module-2020d922c72f)
    '''
    import warnings
    
    if verify == 'path/to/consolidate.pem':
        raise CertificateError('''El certificado SSL de open.bymadata.com.ar no fue validado.
Se puede especificar 'verify=False', pero implica exponer vulnerabilidades en la conexión: 
https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror.
Para evitar esto, es necesario generar el archivo .pem utilizando OpenSSL y poner la ruta al archivo en 'verify': 
https://levelup.gitconnected.com/solve-the-dreadful-certificate-issues-in-python-requests-module-2020d922c72f
''')    
    elif verify == False:
        warnings.warn("InsecureRequestWarning: Unverified HTTPS request is being made to host 'open.bymadata.com.ar'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings\n-------------------------------------------------------------------------------------------------", stacklevel=3)
    
    import requests
    import json
    import pandas as pd
    
    
    url = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/etf"

    payload = json.dumps({
    "excludeZeroPxAndQty": True,
    "T2": True,
    "T1": False,
    "T0": False,
    "Content-Type": "application/json"
    })
    
    headers = {
    'Content-Type': 'application/json'
    }
    if verify:
        response = requests.request("POST", url, headers=headers, data=payload, verify=verify)
    else:
        response = requests.request("POST", url, headers=headers, data=payload)
    
    return pd.DataFrame(response.json())


def get_cedears(verify='path/to/consolidate.pem'):
    '''Devuelve un DataFrame con todos los ETFs que cotizan en ARG.
    El parámetro verify define si se utiliza un certificado SSL para la conexión. Definirlo como False implica exponer vulnerabilidades en la conexión (https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror).
    Para evitar esto, es necesario generar el archivo .pem utilizando OpenSSL (https://levelup.gitconnected.com/solve-the-dreadful-certificate-issues-in-python-requests-module-2020d922c72f)
    '''
    import warnings
    
    if verify == 'path/to/consolidate.pem':
        raise CertificateError('''El certificado SSL de open.bymadata.com.ar no fue validado.
Se puede especificar 'verify=False', pero implica exponer vulnerabilidades en la conexión: 
https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror.
Para evitar esto, es necesario generar el archivo .pem utilizando OpenSSL y poner la ruta al archivo en 'verify': 
https://levelup.gitconnected.com/solve-the-dreadful-certificate-issues-in-python-requests-module-2020d922c72f
''')    
    elif verify == False:
        warnings.warn("InsecureRequestWarning: Unverified HTTPS request is being made to host 'open.bymadata.com.ar'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings\n-------------------------------------------------------------------------------------------------", stacklevel=3)
    
    import requests
    import json
    import pandas as pd
    
    
    url = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/cedears"

    payload = json.dumps({
    "excludeZeroPxAndQty": True,
    "T2": True,
    "T1": False,
    "T0": False,
    "Content-Type": "application/json"
    })
    
    headers = {
    'Content-Type': 'application/json'
    }

    if verify:
        response = requests.request("POST", url, headers=headers, data=payload, verify=verify)
    else:
        response = requests.request("POST", url, headers=headers, data=payload)
    
    return pd.DataFrame(response.json())


def get_bonos(verify='path/to/consolidate.pem'):
    '''Devuelve un DataFrame con todos los ETFs que cotizan en ARG.
    El parámetro verify define si se utiliza un certificado SSL para la conexión. Definirlo como False implica exponer vulnerabilidades en la conexión (https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror).
    Para evitar esto, es necesario generar el archivo .pem utilizando OpenSSL (https://levelup.gitconnected.com/solve-the-dreadful-certificate-issues-in-python-requests-module-2020d922c72f)
    '''
    import warnings
    
    if verify == 'path/to/consolidate.pem':
        raise CertificateError('''El certificado SSL de open.bymadata.com.ar no fue validado.
Se puede especificar 'verify=False', pero implica exponer vulnerabilidades en la conexión: 
https://stackoverflow.com/questions/10667960/python-requests-throwing-sslerror.
Para evitar esto, es necesario generar el archivo .pem utilizando OpenSSL y poner la ruta al archivo en 'verify': 
https://levelup.gitconnected.com/solve-the-dreadful-certificate-issues-in-python-requests-module-2020d922c72f
''')    
    elif verify == False:
        warnings.warn("InsecureRequestWarning: Unverified HTTPS request is being made to host 'open.bymadata.com.ar'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings\n-------------------------------------------------------------------------------------------------", stacklevel=3)
    
    import requests
    import json
    import pandas as pd
    
    
    url = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/public-bonds"

    payload = json.dumps({
    "excludeZeroPxAndQty": True,
    "T2": True,
    "T1": False,
    "T0": False,
    "Content-Type": "application/json"
    })
    
    headers = {
    'Content-Type': 'application/json'
    }

    if verify:
        response = requests.request("POST", url, headers=headers, data=payload, verify=verify)
    else:
        response = requests.request("POST", url, headers=headers, data=payload)
    
    return pd.DataFrame(response.json())


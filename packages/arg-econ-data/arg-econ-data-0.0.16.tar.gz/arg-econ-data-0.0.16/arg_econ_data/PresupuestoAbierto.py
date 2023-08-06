class AuthenticationError(Exception):
    pass

def get_columnas(endpoint='credito'):
    '''
    Devuelve la lista de columnas válidas para el punto de acceso (endpoint) solicitado de Presupuesto Abierto (https://www.presupuestoabierto.gob.ar/api/).
    
    Args:
        @endpoint (str): 'credito' o 'recurso'. Endpoint de la API de Presupuesto Abierto. Defaults to 'credito'
    '''
    import pandas as pd
    if endpoint not in ['recurso', 'credito']:
        raise ValueError('El endpoint solicitado no es válido. Debe ser "recurso" o "credito"')

    df = pd.read_table('https://www.presupuestoabierto.gob.ar/api/json/itemRecurso.txt', sep=';', encoding='utf-16').replace('\t', '', regex=True)
    df.columns = df.columns.str.strip()
    return df


def get_microdata(token: str, columns: list, endpoint: str='credito', **kwargs):
    '''
    Accede a los datos de Presupuesto Abierto mediante la API y devuelve un DataFrame. Requiere un token de autenticación libre y gratuito, que se solicita en https://www.presupuestoabierto.gob.ar/sici/api-pac.
    
    Args:
        token (str): Token de autenticación de la API (https://www.presupuestoabierto.gob.ar/sici/api-pac)
        columns (list): Lista de columnas a solicitar. Pueden consultarse con get_columnas() o en https://www.presupuestoabierto.gob.ar/api/
        endpoint (str): 'credito' o 'recurso'. Endpoint de la API de Presupuesto Abierto. Defaults to 'credito' 
        
    Kwargs:
        ejercicios (list de ints): Año de los ejercicios a consultar (i.e. [2018, 2019])
        order: ver formato en https://www.presupuestoabierto.gob.ar/api/ 
        filters: ver formato en https://www.presupuestoabierto.gob.ar/api/
        
        '''
    import pandas as pd
    import requests
    import re
    
    
    if not token:
        raise AuthenticationError('Para utilizar la API de Presupuesto Abierto es necesario obtener un token de autenticación. Solicitarlo en https://www.presupuestoabierto.gob.ar/sici/api-pac')
    
    headers = {
        'Authorization': token,
        'Accept': 'text/csv',
        }
    
    json_data = {
        'columns': columns
    }
    
    response = requests.post(f'https://www.presupuestoabierto.gob.ar/api/v1/{endpoint}', headers=headers, json=json_data)
    COMMA_MATCHER = re.compile(r",(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)")
    df = pd.DataFrame(COMMA_MATCHER.split(x) for x in response.text.split('\n'))
    df = df.apply(lambda s:s.str.replace('"', ''))
    df.columns = df.iloc[0]
    df.drop(index=df.index[0], axis=0, inplace=True)
    df = df.reset_index(drop=True)
    df.drop(df.tail(1).index,inplace=True)
    
    return df
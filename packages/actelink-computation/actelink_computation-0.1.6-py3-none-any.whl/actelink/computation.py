import json
import requests
import urllib.parse
from os import getenv
from actelink.config import settings
from actelink.logger import log
from actelink.server import app
import actelink.models as models
from actelink.models import Context

def init(url: str = None, key: str = None) -> None:
    """Initialise le module actelink.computation

    :param str url: L'url de connexion à la plateforme Actelink.
    :param str key: La clé d'API avec laquelle s'authentifier auprès de la plateforme.
    """
    # use computation proxy url & api-key from environment variables by default
    proxy_url = getenv("COMPUTATION_PROXY_URL", url)
    proxy_key = getenv("COMPUTATION_PROXY_API_KEY", key)
    log.info(f"using url {proxy_url} & key {proxy_key}")
    global __PROXY_API_KEY, __PROXY_ENDPOINT
    __PROXY_API_KEY     = proxy_key
    __PROXY_ENDPOINT    = urllib.parse.urljoin(proxy_url, '/api/declarations')

def declare(fname: str, fcallback: object, context: Context) -> None:
    """Déclare une fonction de tarification pour un contexte donné

    :param str fname: Le nom de la fonction.
    :param str fcallback: La fonction de tarification à appeler pour calculer le tarif correspondant au contexte donné.
    :param Context context: Le contexte de calcul pour lequel cette fonction doit être appelée.

    Exemple d'utilisation :

    >>> import actelink.computation as ac

    >>> def cout_moyen_frequence(context: Context, params: dict) -> float:
    >>>     ...
    >>>     return result
    
    >>> ac.init(...)
    >>> ac.declare("avg_cost", cout_moyen_frequence, Context(...))
    """
    log.info(f"{fname}, {fcallback}, {context})")
    models.add(fname, fcallback, context)

def start() -> None:
    """Démarre le serveur de calcul

    L'appel à cette fonction va provoquer la déclaration effective des formules de calcul de tarification auprès de la plateforme Actelink et écouter les demandes de tarification provenant de cette dernière. 

    :raises ConnectionError: si la connexion à la plateforme échoue.
    """
    # server declaration to computation proxy
    body = {
        'apiKey':            __PROXY_API_KEY, 
        'serverAddress':     settings.COMPUTATION_SERVER_URL,
        'formulesSupported': models.get()
    }
    j = json.dumps(body, default=vars)
    log.info(f"declaring to proxy as {settings.COMPUTATION_SERVER_URL}")
    log.debug(f"{j}")
    try:
        # no need for session since we only send this request once
        response = requests.post(__PROXY_ENDPOINT, 
                                headers={'Content-Type': 'application/json; charset=utf-8'},
                                data=j)
    except requests.exceptions.ConnectionError as error:
        log.error(f"CONNECTION FAILED!\n{error})")
        raise
    # check response is valid
    if response.status_code != 200:
        log.error(f"REQUEST FAILED!\n{response.reason})")
        raise requests.exceptions.ConnectionError(f'Request failed, reason: {response.reason}')
    log.info(f"declaration succeeded")
    app.start()
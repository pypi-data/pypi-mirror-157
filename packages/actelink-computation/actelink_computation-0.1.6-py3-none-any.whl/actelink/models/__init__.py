from dataclasses import dataclass
from enum import Enum
from actelink.logger import log
from .utils import get_context_params, get_level_params

# makes our enums also inherits from str so that it is JSON serializable
class Calcul(str, Enum):
    """
    Enumération des différents types de calcul
    """
    PrimePureDirecte    = 'PRIME_PURE_DIRECTE'
    """ Calcul de la prime pure directe """
    CoutMoyenFrequence  = 'avg_cost'
    """ Calcul du coût moyen * fréquence """

class Regime(str, Enum):
    """
    Enumération des régimes de sécurité sociale
    """
    General         = 'GENERAL'
    """ Régime général """
    AlsaceMoselle   = 'ALSACE_MOSELLE'
    """ Régime Alsace Moselle """

class NiveauProduit(str, Enum):
    """
    Enumération des différents niveaux de produit
    """
    Bas     = 'BAS'
    """ Niveau de produit bas de gamme """
    Milieu  = 'MILIEU'
    """ Niveau de produit milieu de gamme """
    Haut    = 'HAUT'
    """ Niveau de produit haut de gamme """

@dataclass
class Context(object):
    """
    Object représentant un contexte de calcul
    """
    millesime:  str
    """ Millésime """
    offre:      str
    """ Offre """
    guarantyId: str
    """ Identifiant unique de garantie """
    calcul:     Calcul
    """ Type de calcul """

    @classmethod
    def from_dict(cls, context: dict):
        return cls(**context)

    @classmethod
    def from_string(cls, context: str):
        new_ctx = {}
        ctx_values = context.split(".")
        for idx, field in enumerate(Context.__dataclass_fields__.keys()):
            if idx >= len(ctx_values):
                return None
            new_ctx[field] = ctx_values[idx]
        return cls(**new_ctx)

    # implements __hash__ so that Context is hashable hence can be used as a key
    def __hash__(self):
        return hash((self.millesime, self.offre, self.guarantyId, self.calcul))

__functions = {}

def add(fname: str, fcallback: object, context: Context) -> None:
    log.info(f"{fname}, {fcallback}, {context})")
    __functions[context] = {"functionName": fname, "callback": fcallback}

def get() -> list:
    return [{"context": key, "functionName": value["functionName"]} for key,value in __functions.items()]

def compute(contexts: dict) -> list:
    params = get_level_params(contexts["computationContexts"])
    results_list = {"results": []}
    # TODO: threading
    for item in contexts["computationContexts"]["contexts"]:
        context = Context.from_dict(item["context"])
        function = __functions.get(context)
        if function is not None:
            get_context_params(item, params)
            log.info(f"found function {function['functionName']} for {context}")
            result = {"context": item["context"]}
            result["functionName"] = function["functionName"]
            result["rate"] = {
                "value": function["callback"](context, params),
                "unit": "euros"
            }
            results_list["results"].append(result)
        else:
            log.error(f"no function defined for {context}")
    return results_list
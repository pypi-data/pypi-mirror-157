def get_level_params(contexts: dict) -> dict:
    params = {}
    params["demography"]      = contexts["demography"]
    params["regime"]          = contexts["regime"]
    params["levelOfProduct"]  = contexts["levelOfProduct"]
    return params

def get_context_params(context: dict, params: dict):
    # dunno why parameters is an array..
    params["parameters"] = context["parameters"][0]
from . import Context, Calcul, Regime, NiveauProduit
from typing import List, Optional
from pydantic import BaseModel

class ContextSchema(BaseModel):
    context: Context

class ContextsSchema(BaseModel):
    contexts = List[ContextSchema]

class ComputationContexts(BaseModel):
    contexts: ContextSchema
    offre = fields.String()
    guarantyId = fields.String()
    calcul = fields.String()
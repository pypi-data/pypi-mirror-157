from flask import request, abort
from flask_restx import Api, Resource
import actelink.models as models

api = Api()

#TODO: request validation vs. schema
@api.route('/_computations/', methods=['POST'])
class Computations(Resource):
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def post(self):
        data = request.get_json()
        res = models.compute(data)
        if len(res["results"]) == 0:
            abort(400, "no function registered for these contexts")
        return res, 200

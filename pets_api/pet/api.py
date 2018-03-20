from flask.views import MethodView
from flask import jsonify, request, abort

import uuid
import json
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match

from pets_api.app.decorators import app_required
from pets_api.pet.models import Pet
from pets_api.pet.schema import schema

from pets_api.store.models import Store
from datetime import datetime


class PetAPI(MethodView):

    decorators = [app_required, ]

    def __init__(self):
        self.PETS_PER_PAGE = 10
        if request.method not in ["GET", "DELETE", ] and not request.json:
            abort(400)

    def get(self, pet_id=None):
        if pet_id:
            pet = Pet.objects.filter(external_id=pet_id, live=True).first()
            if pet:
                return jsonify(dict(result="ok", pet=pet.to_obj())), 200
            return jsonify({"result": "not found", "id": pet_id}), 404

        pet_href = "/pets/?page=%s"
        pets = Pet.objects.filter(live=True)
        # add filters:
        for f in ["species", "breed", "name", ]:
            v = request.args.get(f)
            if v:
                pets = pets.filter(**{f: v})
                pet_href += '&' + f + '=' + v
        page = int(request.args.get("page", 1))
        pets = pets.paginate(page=page, per_page=self.PETS_PER_PAGE)
        links = [
            dict(rel="self", href=pet_href % page),
        ]
        if pets.has_prev:
            links.append(
                dict(rel="previous", href=pet_href % pets.prev_num))
        if pets.has_next:
            links.append(
                dict(rel="next", href=pet_href % pets.next_num))
        return jsonify(
            dict(
                result="ok",
                links=links,
                pet=[s.to_obj() for s in pets.items])), 200

    def post(self):
        data = request.json
        error = best_match(Draft4Validator(schema).iter_errors(data))

        if error:
            return jsonify(dict(error=error.message)), 400

        store = Store.objects.filter(external_id=data.get('store')).first()
        if not store:
            error = {
                "code": "STORE_NOT_FOUND"
            }
            return jsonify({'error': error}), 400
        data["store"] = store

        try:
            data["received_date"] = datetime.strptime(
                data.get('received_date'), "%Y-%m-%dT%H:%M:%SZ")
        except:
            return jsonify({"error": "INVALID_DATE"}), 400

        pet = Pet(external_id=str(uuid.uuid4()), **data)
        pet.save()
        pet.reload()

        if pet:
            return jsonify(dict(result="ok", pet=pet.to_obj())), 201
        return jsonify(dict(result="error",
                            error="Failed to create a pet.")), 400

    def put(self, pet_id):  # for "update" you can use PATCH for individual attribute updates
        pet = Pet.objects.filter(external_id=pet_id, live=True).first()
        if not pet:
            return jsonify({"result": "not found", "external_id": pet_id}), 404
        data = request.json
        if not data:
            abort(400)
        error = best_match(Draft4Validator(schema).iter_errors(data))
        if error:
            return jsonify(dict(error=error.message)), 400

        if "store" in data:
            store = Store.objects.filter(external_id=data["store"]).first()
            if not store:
                error = {
                    "code": "STORE_NOT_FOUND"
                }
                return jsonify({'error': error}), 400
            data["store"] = store

        if "received_date" in data:
            try:
                data["received_date"] = datetime.strptime(
                    data.get('received_date'), "%Y-%m-%dT%H:%M:%SZ")
            except:
                return jsonify({"error": "INVALID_DATE"}), 400

        pet.update(**data)
        pet.reload()
        return jsonify(dict(result="ok", pet=pet.to_obj())), 200

    def patch(
            self, pet_id=None
    ):  # for "update" you can use PATCH for individual attribute updates
        if not request.json or "name" not in request.json:
            abort(400)
        if pet_id and pet_id < len(self.pets):
            pet = self.pets[pet_id - 1]
            pet["name"] = request.json["name"]
            return jsonify({"pet": pet}), 200
        return None, 200

    def delete(self, pet_id):
        pet = Pet.objects.filter(external_id=pet_id, live=True).first()
        if not pet:
            return jsonify({"result": "not found", "external_id": pet_id}), 404
        pet.live = False
        pet.save()
        return jsonify({"result": "deleted", "external_id": pet_id}), 204

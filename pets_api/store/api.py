from flask.views import MethodView
from flask import jsonify, request, abort, render_template

import uuid
import json
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match

from pets_api.app.decorators import app_required
from pets_api.store.models import Store
from pets_api.store.schema import schema
from pets_api.pet.models import Pet


class StoreAPI(MethodView):

    decorators = [app_required, ]

    stores = [dict(
                id=store_id,
                name=name,
                links=[dict(rel="self", href="/stores/%d" % store_id), ])
              for store_id, name in enumerate(("Mac", "Leo", "Brownie", ), 1)]

    def __init__(self):
        self.STORES_PER_PAGE = 5
        self.PETS_PER_PAGE = 5
        if request.method not in ["GET", "DELETE", ] and not request.json:
            abort(400)

    def get(self, store_id=None):
        page = int(request.args.get("page", 1))
        if store_id:
            store = Store.objects.filter(external_id=store_id, live=True).first()
            if store:
                if "pets" in request.url:
                    pets = Pet.objects.filter(store=store, live=True)
                    pets = pets.paginate(
                        page=page, per_page=self.PETS_PER_PAGE)
                    links = [
                        dict(
                            rel="self",
                            href="/stores/%s/pets/?page=%s" % (store_id,
                                                               page)),
                    ]
                    if pets.has_prev:
                        links.append(
                            dict(
                                rel="previous",
                                href="/stores/%s/pets/?page=%s" %
                                (store_id, pets.prev_num)))
                    if pets.has_next:
                        links.append(
                            dict(
                                rel="next",
                                href="/stores/%s/pets/?page=%s" %
                                (store_id, pets.next_num)))
                    return jsonify(
                        dict(
                            result="ok",
                            links=links,
                            store=store.to_obj(),
                            pets=[p.to_obj(nostore=True) for p in pets.items])), 200

                return jsonify(dict(result="ok", store=store.to_obj())), 200
            return jsonify({"result": "not found", "id": store_id}), 404

        stores = Store.objects.filter(live=True)
        stores = stores.paginate(page=page, per_page=self.STORES_PER_PAGE)
        links = [
            dict(rel="self", href="/stores/?page=%s" % page),
        ]
        if stores.has_prev:
            links.append(dict(rel="previous", href="/stores/?page=%s" % stores.prev_num))
        if stores.has_next:
            links.append(dict(rel="next", href="/stores/?page=%s" % stores.next_num))
        return jsonify(dict(
            result="ok",
            links=links,
            store=[s.to_obj() for s in stores.items]
        )), 200

    def post(self):
        data = request.json
        error = best_match(Draft4Validator(schema).iter_errors(data))

        if error:
            return jsonify(dict(error=error.message)), 400

        store = Store(external_id=str(uuid.uuid4()), **data)
        store.save()

        if store:
            return jsonify(dict(result="ok", store=store.to_obj())), 201
        return jsonify(dict(result="error", error="Failed to create a store.")), 400

    def put(self, store_id):  # for "update" you can use PATCH for individual attribute updates
        store = Store.objects.filter(external_id=store_id, live=True).first()
        if not store:
            return jsonify({"result": "not found", "external_id": store_id}), 404
        data = request.json
        if not data:
            abort(400)
        error = best_match(Draft4Validator(schema).iter_errors(data))
        if error:
            return jsonify(dict(error=error.message)), 400
        store.update(**data)
        store.reload()
        return jsonify(dict(result="ok", store=store.to_obj())), 200

    def patch(self, store_id=None):  # for "update" you can use PATCH for individual attribute updates
        if not request.json or "name" not in request.json:
            abort(400)
        if store_id and store_id < len(self.stores):
            store = self.stores[store_id-1]
            store["name"] = request.json["name"]
            return jsonify({"store": store}), 200
        return None, 200

    def delete(self, store_id):
        store = Store.objects.filter(external_id=store_id, live=True).first()
        if not store:
            return jsonify({"result": "not found", "external_id": store_id}), 404
        store.live = False
        store.save()
        return jsonify({"result": "deleted", "external_id": store_id}), 204
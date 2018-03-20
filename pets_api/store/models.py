from mongoengine import signals
from application import db
from mongoengine.fields import StringField, BooleanField

class Store(db.Document):
    external_id = StringField(db_field="ei")
    neighborhood = StringField(db_field="n")
    street_address = StringField(db_field="sa")
    city = StringField(db_field="c")
    state = StringField(db_field="st")
    zip = StringField(db_field="z")
    phone = StringField(db_field="p")
    live = BooleanField(db_field="l", default=True)

    meta = dict(indexes=[("external_id", "live", )])

    @property
    def links(self):
        return [
            dict(rel="self", href="/stores/" + self.external_id),
            dict(rel="pets", href="/stores/" + self.external_id + "/pets/"),
        ]

    def to_obj(self):
        obj = {"id" if f == "external_id" else f: self[f] for f in self.fields if f not in ("_id", "id", )}
        obj["links"] = self.links
        return obj
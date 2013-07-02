
#  IATI Updates, IATI Registry API augmented
#  by Mark Brough
#
#  Copyright (C) 2013 Publish What You Fund
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the GNU Affero General Public License v3.0

from flask import Flask, render_template, flash, request, Markup, \
    session, redirect, url_for, escape, Response, abort, send_file, \
    current_app

from iatiupdates import app
from iatiupdates import db
import registry
import os
import json
import datetime
import ast

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def jsonify(*args, **kwargs):
    return current_app.response_class(json.dumps(dict(*args, **kwargs),
            indent=None if request.is_xhr else 2, cls=JSONEncoder),
        mimetype='application/json')

@app.route("/api/")
def api():
    return jsonify({"paths": {'publisher': url_for('api_publisher')}})

@app.route("/api/publisher/")
def api_publisher():
    data = []
    publishers = registry.publishers()
    for publisher in publishers:
        d = publisher.as_dict()
        d["extras"] = ast.literal_eval(d["extras"])
        d["packages"] = ast.literal_eval(d["packages"])
        data.append(d)
    return jsonify({"data": data})

@app.route("/api/package/")
def api_package():
    data = []
    packages = registry.packages()
    for package in packages:
        d = package.as_dict()
        if d["extras"] is not None:
            d["extras"] = ast.literal_eval(d["extras"])
        if d["resources"] is not None:
            d["resources"] = ast.literal_eval(d["resources"])
        data.append(d)
    return jsonify({"data": data})


@app.route("/api/package/hash/")
def api_package_hash():
    data = []
    packages = registry.packages()
    for package in packages:
        data.append({"id": package.id, "name": package.name, "hash": package.hash})
    return jsonify({"data": data})

@app.route("/api/revision/")
def api_revision():

    try:
        limit = request.args['limit']
        assert int(limit) >= 0
    except Exception:
        limit = 100

    try:
        offset = request.args['offset']
        assert int(offset) >= 0
    except Exception:
        offset = 0

    try:
        conditions = json.loads(request.args['conditions'])
    except Exception:
        conditions = None

    data = []
    revisions = registry.revisions_data(offset, limit, conditions)
    for revision in revisions:
        try:
            pg = revision.PackageGroup.as_dict()
        except AttributeError:
            pg = None
        try:
            p = revision.Package.as_dict()
        except AttributeError:
            p = None
        try:
            r = revision.Revision.as_dict()
        except AttributeError:
            r = None
        data.append({
            "publisher": pg,
            "package": p,
            "revision": r
             })
    return jsonify({"data": data})

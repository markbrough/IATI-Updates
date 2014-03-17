
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
    return jsonify({"paths": {
                    'publisher': url_for('api_publisher'),
                    'package': url_for('api_package'),
                    'package_hash': url_for('api_package_hash'),
                    'revision': url_for('api_revision')}
                   })

def frequentify(frequency):
    FREQUENCIES = {
            0: 'Over a year ago',
            1: 'Monthly',
            2: 'Quarterly',
            3: 'Less than quarterly',
            None: ''
         }
    return FREQUENCIES[frequency]

@app.route("/api/publisher/frequency/")
@app.route("/api/publisher/<packagegroup_name>/frequency/")
def api_publisher_frequency(packagegroup_name=None):
    data = []
    if packagegroup_name is not None:
        publisher = registry.publishers_frequency(packagegroup_name)
        data.append({
                'publisher': publisher.name,
                'frequency_code': publisher.frequency,
                'frequency': frequentify(publisher.frequency),
                'frequency_comment': publisher.frequency_comment
            })
    else:
        for publisher in registry.publishers_frequency():
            data.append({
                'publisher': publisher.name,
                'frequency_code': publisher.frequency,
                'frequency': frequentify(publisher.frequency),
                'frequency_comment': publisher.frequency_comment
            })
    return jsonify({"data":data})

@app.route("/api/publisher/<packagegroup_name>/updates/")
@app.route("/api/publisher/<packagegroup_name>/updates/<message_method>/")
def api_publisher_updates(packagegroup_name, message_method=None):
    return jsonify({"dates": registry.getUpdatedDates(packagegroup_name, message_method)})

@app.route("/api/publisher/")
@app.route("/api/publisher/<packagegroup_name>/")
def api_publisher(packagegroup_name=None):
    data = []
    if packagegroup_name is not None:
        publishers = registry.publishers(packagegroup_name)
        d = publishers.as_dict()
        d["extras"] = ast.literal_eval(d["extras"])
        d["packages"] = ast.literal_eval(d["packages"])
        data.append(d)
    else:
        publishers = registry.publishers()
        for publisher in publishers:
            d = publisher.as_dict()
            d["extras"] = ast.literal_eval(d["extras"])
            d["packages"] = ast.literal_eval(d["packages"])
            data.append(d)
    return jsonify({"data": data})

@app.route("/api/package/")
@app.route("/api/package/<id>/")
def api_package(id=None):
    data = []
    if id is not None:
        packages = registry.packages(id)
        d = packages.as_dict()
        if d["extras"] is not None:
            d["extras"] = ast.literal_eval(d["extras"])
        if d["resources"] is not None:
            d["resources"] = ast.literal_eval(d["resources"])
        data.append(d)
    else:
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
        data.append({"id": package.id, 
                     "name": package.name, 
                     "hash": package.hash, 
                     "url": package.url})
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

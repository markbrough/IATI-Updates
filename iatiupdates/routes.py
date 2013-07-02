
#  IATI Updates, IATI Registry API augmented
#  by Mark Brough
#
#  Copyright (C) 2013 Publish What You Fund
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the GNU Affero General Public License v3.0

from flask import Flask, render_template, flash, request, Markup, \
    session, redirect, url_for, escape, Response, abort, send_file

from iatiupdates import app
from iatiupdates import db
import registry
import os

@app.route("/")
def home():
    num_publishers = registry.getNumRealPublishers()
    return render_template("dashboard.html",
            num_publishers=num_publishers)

@app.route("/publisher/")
def publisher():
    publishers = registry.publishers()
    return render_template("publisher.html", 
                    publishers=publishers)

@app.route("/package/")
def package():
    packages = registry.packages()
    return render_template("package.html", 
                    packages=packages)

@app.route("/revision/")
def revision():
    revisions = registry.revisions()
    return render_template("revision.html", 
                    revisions=revisions)

@app.route("/update/")
def update():
    print "getting packagegroups..."
    registry.get_packagegroups()
    print "getting packages..."
    registry.get_packages()
    print "getting revisions..."
    registry.get_revisions()

@app.route("/update/revisions/")
def update_revisions():
    print "getting revisions..."
    registry.get_revisions()

@app.route("/update/packagegroups/")
def update_packagegroups():
    print "getting packagegroups..."
    registry.get_packagegroups()

@app.route("/update/packages/")
def update_packages():
    print "getting packages..."
    registry.get_packages()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#!/usr/bin/env python

#  IATI Data Quality, tools for Data QA on IATI-formatted  publications
#  by Mark Brough, Martin Keegan, Ben Webb and Jennifer Smith
#
#  Copyright (C) 2013  Publish What You Fund
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the GNU Affero General Public License v3.0

from flask.ext.script import Manager
import iatiupdates

def run():
    iatiupdates.db.create_all()
    manager = Manager(iatiupdates.app)
    manager.run()

if __name__ == "__main__":
    run()


#  IATI Updates, IATI Registry API augmented
#  by Mark Brough
#
#  Copyright (C) 2013 Publish What You Fund
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the GNU Affero General Public License v3.0

from sqlalchemy import *
from iatiupdates import db
from datetime import datetime

class Package(db.Model):
    __tablename__ = 'package'
    id = Column(UnicodeText, primary_key=True)
    packagegroup_id = Column(UnicodeText, ForeignKey('packagegroup.id'))
    metadata_created = Column(DateTime)
    metadata_modified = Column(DateTime)
    relationships = Column(UnicodeText)
    author_email = Column(UnicodeText)
    state = Column(UnicodeText)
    license_id = Column(UnicodeText)
    resources = Column(UnicodeText)
    tags = Column(UnicodeText)
    groups = Column(UnicodeText)
    name = Column(UnicodeText)
    isopen = Column(UnicodeText)
    license = Column(UnicodeText)
    notes_rendered = Column(UnicodeText)
    ckan_url = Column(UnicodeText)
    title = Column(UnicodeText)
    extras = Column(UnicodeText)
    ratings_count = Column(UnicodeText)
    revision_id = Column(UnicodeText)
    notes = Column(UnicodeText)
    ratings_average = Column(UnicodeText)
    author = Column(UnicodeText)
    packagegroup_name = Column(UnicodeText)
    issue_type = Column(UnicodeText, ForeignKey('issuetype.id'))
    issue_message = Column(UnicodeText)
    issue_date = Column(UnicodeText)
    hash = Column(UnicodeText)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PackageGroup(db.Model):
    __tablename__ = 'packagegroup'
    id = Column(UnicodeText, primary_key=True)
    display_name = Column(UnicodeText)
    description = Column(UnicodeText)
    created = Column(DateTime)
    title = Column(UnicodeText)
    state = Column(UnicodeText)
    extras = Column(UnicodeText)
    revision_id = Column(UnicodeText)
    packages = Column(UnicodeText)
    name = Column(UnicodeText)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Revision(db.Model):
    __tablename__ = 'revision'
    id = Column(UnicodeText, primary_key=True)
    timestamp = Column(DateTime)
    package_id = Column(UnicodeText, ForeignKey('package.id'))
    message = Column(UnicodeText)
    author = Column(UnicodeText)
    group_id = Column(UnicodeText, ForeignKey('packagegroup.id'))
    message_type = Column(UnicodeText)
    message_text = Column(UnicodeText)
    date = Column(DateTime)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class IssueType(db.Model):
    __tablename__ = 'issuetype'
    id = Column(UnicodeText, primary_key=True)
    name = Column(UnicodeText)

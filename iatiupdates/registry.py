
#  IATI Updates, IATI Registry API augmented
#  by Mark Brough
#
#  Copyright (C) 2013 Publish What You Fund
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the GNU Affero General Public License v3.0

import urllib2
import json
import datetime
import models
from iatiupdates import db
from sqlalchemy import func

PACKAGESEARCH_URL = "http://iatiregistry.org/api/2/search/dataset?fl=id,name,groups,title,ckan_url&limit=1000&offset=%s"
PACKAGEGROUPS_URL="http://iatiregistry.org/api/2/rest/group/"
PACKAGEGROUP_URL="http://iatiregistry.org/api/2/rest/group/%s"
PACKAGES_URL="http://iatiregistry.org/api/2/rest/package/"
PACKAGE_URL="http://iatiregistry.org/api/2/rest/package/%s"
REVISIONS_URL="http://iatiregistry.org/api/2/search/revision?since_time=%s"
REVISION_URL="http://iatiregistry.org/api/2/rest/revision/%s"

FREQUENCY_OVERAYEAR=0
FREQUENCY_MONTHLY=1
FREQUENCY_QUARTERLY=2
FREQUENCY_LTQUARTERLY=3

ORGANIZATION_TYPES = [
    ('80', 'Academic, Training and Research'),
    ('60', 'Foundation'),
    ('10', 'Government'),
    ('21', 'International NGO'),
    ('40', 'Multilateral'),
    ('22', 'National NGO'),
    ('15', 'Other Public Sector'),
    ('70', 'Private Sector'),
    ('30', 'Public Private Partnership'),
    ('23', 'Regional NGO'),
]

FREQUENCIES = {
            0: 'Over a year ago',
            1: 'Monthly',
            2: 'Quarterly',
            3: 'Less than quarterly'
             }

def getUpdatedDates(publisher_name, message_method=None):
    # Get distinct dates for each packagegroup

    q = db.session.query(models.Revision.date,
                        func.count(models.Revision.package_id)
            ).outerjoin(models.Package
            ).outerjoin(models.PackageGroup
            ).distinct(
            ).filter(models.PackageGroup.name==publisher_name)

    if message_method is not None:
        q = q.filter(models.Revision.message_method==message_method)

    data = q.group_by(models.Revision.date
            ).all()

    dates = {}
    for row in data:
        thedate = str(datetime.date(row.date.date().year, row.date.date().month, row.date.date().day))
        if thedate not in dates:
            dates[thedate] = row[1]
        else:
            dates[thedate] += row[1]
    dates_new = []
    for d in sorted(dates):
        dates_new.append({"date": d, "updates": dates[d]})
    return dates_new

def getNumRealPublishers():
    query = db.session.query(models.PackageGroup
                ).join(models.Package
                ).filter(models.PackageGroup.name!=None
                ).filter(models.PackageGroup.deleted!=True
                ).all()
    return len(query)

def getFrequencyTotals():
    query = db.session.query(models.PackageGroup.frequency,
                             func.count(models.PackageGroup.id)
                    ).filter(models.PackageGroup.name!=None
                    ).group_by(models.PackageGroup.frequency
                    ).all()
    return query

def publishers(name=None):
    if name is not None:
        return models.PackageGroup.query.filter_by(name=name).first()
    return models.PackageGroup.query.filter(models.PackageGroup.name!=None
                ).order_by('display_name ASC'
                ).all()

def publishers_frequency(name=None):
    if name is not None:
        return db.session.query(models.PackageGroup.name,
                                models.PackageGroup.frequency,
                                models.PackageGroup.frequency_comment
                    ).filter(models.PackageGroup.name==name
                    ).first()
    else:
        return db.session.query(models.PackageGroup.name,
                                models.PackageGroup.frequency,
                                models.PackageGroup.frequency_comment
                    ).all()

def packages(id=None):
    if id is not None:
        return db.session.query(models.Package,
                                models.PackageGroup.name
                    ).outerjoin(models.PackageGroup
                    ).filter(models.Package.id==id).first()
    return db.session.query(models.Package,
                            models.PackageGroup.name
                ).outerjoin(models.PackageGroup
                ).order_by('Package.title ASC').all()

def revisions():
    data = db.session.query(models.Revision, 
                            models.Package, 
                            models.PackageGroup
            ).outerjoin(models.Package
            ).outerjoin(models.PackageGroup
            ).order_by(models.Revision.timestamp.desc()
            ).limit(100
            ).all()
    return data

def revisions_data(offset, limit, conditions):
    query = db.session.query(models.Revision, 
                            models.Package, 
                            models.PackageGroup
            ).outerjoin(models.Package
            ).outerjoin(models.PackageGroup)

    if conditions:
        conditions_query = query
        if 'packagegroup_name' in conditions:
            conditions_query = conditions_query.filter(models.PackageGroup.name==conditions['packagegroup_name'])
        if 'exclude_iatiarchiver' in conditions:
            conditions_query = conditions_query.filter(models.Revision.author!='iati-archiver')
        if 'message_method' in conditions:
            conditions_query = conditions_query.filter(models.Revision.message_method==conditions['message_method'])
    else:
        conditions_query = query

    data = conditions_query.order_by(models.Revision.timestamp.desc()
            ).limit(limit
            ).offset(offset
            ).all()

    return data

def get_current_revisions(): 
    r = db.session.query(models.Revision.id).all()
    return list(map(lambda i: i.id, r))

def get_current_packages():
    p = db.session.query(models.Package.id).all()
    return list(map(lambda i: i.id, p))

def get_current_packagegroups():
    pg = db.session.query(models.PackageGroup.id).all()
    return list(map(lambda i: i.id, pg))

def getCreatePackage(id):
    if not id:
        return None
    check = models.Package.query.filter_by(id=id).first()
    if not check:
        p = models.Package()
        p.id = id
        db.session.add(p)
        db.session.commit()
        return p
    return check

def getCreatePackage_id(id):
    if not id:
        return None
    check = models.Package.query.filter_by(id=id).first()
    if not check:
        p = models.Package()
        p.id = id
        db.session.add(p)
        db.session.commit()
        return p.id
    return check.id

def getCreatePackageGroup(id):
    check = models.PackageGroup.query.filter_by(id=id).first()
    if not check:
        pg = models.PackageGroup()
        pg.id = id
        db.session.add(pg)
        db.session.commit()
        return pg
    return check

def getCreatePackageGroup_id(id):
    if id is None:
        return None
    check = models.PackageGroup.query.filter_by(id=id).first()
    if not check:
        pg = models.PackageGroup()
        pg.id = id
        db.session.add(pg)
        db.session.commit()
        return pg.id
    return check.id

def getPackageGroupByName(name):
    check = models.PackageGroup.query.filter_by(name=name).first()
    if not check:
        return None
    return check.id

def getOrCreateIssueType(id):
    print "getting issue type", id
    issuetype = models.IssueType.query.filter_by(id=id).first()
    if not issuetype:
        print "issuetype was not there"
        it = models.IssueType()
        it.id=id
        db.session.add(it)
        db.session.commit()
        print "committing"
        return it
    print "issuetype was there, retunring"
    return issuetype

def get_packagegroups(cleanup=False):
    current_packagegroups = get_current_packagegroups()
    print current_packagegroups

    packagegroups_list_req = urllib2.Request(PACKAGEGROUPS_URL)
    packagegroups_list_webfile = urllib2.urlopen(packagegroups_list_req)
    packagegroups_list = json.loads(packagegroups_list_webfile.read())

    # Also mark packagegroups for deletion if they're not there anymore
    # This should really be done in the model.
    disappeared = 0
    for current in current_packagegroups:
        if current not in packagegroups_list:
            disappeared +=1
            pg = models.PackageGroup.query.filter_by(id=current
                ).first()
            print pg.name, "is no longer on the Registry"
            pg.deleted = True
            db.session.commit()

    print disappeared, "packagegroups no longer on the Registry"
    
    for packagegroup in packagegroups_list:
        print packagegroup

        packagegroup_req = urllib2.Request(PACKAGEGROUP_URL % (packagegroup))
        packagegroup_webfile = urllib2.urlopen(packagegroup_req)
        packagegroup_data = json.loads(packagegroup_webfile.read())
    
        pg = getCreatePackageGroup(packagegroup_data["id"])
        pg.display_name = packagegroup_data["display_name"]
        pg.description = packagegroup_data["description"]
        pg.created = packagegroup_data["created"]
        pg.title = packagegroup_data["title"]
        pg.state = packagegroup_data["state"]
        pg.extras = str(packagegroup_data["extras"])
        pg.revision_id = packagegroup_data["revision_id"]
        pg.packages = str(packagegroup_data["packages"])
        pg.name = packagegroup_data["name"]
        if packagegroup_data.get('extras') is not None:
            pg.orgtype = packagegroup_data['extras'].get('publisher_organization_type')
        db.session.add(pg)
        db.session.commit()

def get_packages(update_existing_ones=False):
    current_packages = get_current_packages()
    print "There are", len(current_packages), "current packages"

    packages_list_req = urllib2.Request(PACKAGES_URL)
    packages_list_webfile = urllib2.urlopen(packages_list_req)
    packages_list = json.loads(packages_list_webfile.read())
    print "There are", len(packages_list), "packages on the Registry"

    # Also mark packages for deletion if they're not there anymore
    disappeared = 0
    for current in current_packages:
        if current not in packages_list:
            disappeared +=1
            p = models.Package.query.filter_by(id=current
                ).first()
            print p.name, "is no longer on the Registry"
            p.deleted = True
            db.session.commit()

    print disappeared, "packages no longer on the Registry"
        
    for package_id in packages_list:

        # Generally ignore existing packages
        if not update_existing_ones:
            if package_id in current_packages:
                continue

        print "Requesting metadata for package", package_id

        package_req = urllib2.Request(PACKAGE_URL % (package_id))
        package_webfile = urllib2.urlopen(package_req)
        package = json.loads(package_webfile.read())

        p = getCreatePackage(package['id'])

        fields = ['metadata_modified', 'metadata_created',
        'relationships', 'author_email', 'state', 'license_id', 
        'resources', 'tags', 'groups', 'name', 'isopen', 'license', 
        'notes_rendered', 'ckan_url', 'title', 'ratings_count', 
        'revision_id', 'notes', 'ratings_average', 'author']
        
        for field in fields:
            try:
                setattr(p, field, str(package[field].decode('utf-8')))
            except Exception:
                pass

        p.extras = str(package['extras'])
        p.resources = str(package['resources'])

        if len(package['resources']) >0:
            p.hash = package['resources'][0]['hash']
            p.url = package['resources'][0]['url']
        else:
            # Don't add packages without a URL... weird things could happen 
            # (not sure what exactly)
            continue

        if (package.get('organization') and len(package["organization"])>0):
            # CKAN v2 API changed!!
            packagegroup = publishers(package["organization"]["name"])
            p.packagegroup_id = packagegroup.id
            p.packagegroup_name = packagegroup.name

        if package['extras'].get('issue_type'):
            p.issue_type = getOrCreateIssueType(package['extras']['issue_type']).id
            p.issue_date = package['extras']['issue_date']
            p.issue_message = package['extras']['issue_message']
        else:
            p.issue_type = None
            p.issue_date = None
            p.issue_message = None
        
        db.session.add(p)
        db.session.commit()
    
def get_package_id(revision_data):
    try:
        return revision_data['packages'][0]
    except KeyError:
        pass
    except IndexError:
        pass
    except TypeError:
        pass

def get_packagegroup_id(revision_data):
    try:
        return revision_data['groups'][0]
    except KeyError:
        pass
    except IndexError:
        pass
    except TypeError:
        pass

def get_revision_type(revision_message):
    try:
        data = revision_message.split(": ")
        if data[0] in ["REST API", 
                       "Daily archiver", 
                       "CSV import"]:
            method = data[1].split(" ")[0].lower()
        else:
            method = ""
        return {"type": data[0],
                "text": data[1],
                "method": method }
    except Exception:
        return {"type": "",
                "text": "",
                "method": ""}

def get_revisions():
    current_revisions = get_current_revisions()
    revisions_list_req = urllib2.Request(REVISIONS_URL % ("2013-01-01"))
    revisions_list_webfile = urllib2.urlopen(revisions_list_req)
    revisions_list = json.loads(revisions_list_webfile.read())

    print "got revisions list"
        
    revcount = 0
    continuecount = 0
    for revision in revisions_list:
        if revision in current_revisions:
            continuecount +=1
            if continuecount >= 5000:
                print "Writing to DB"
                db.session.commit()
                continuecount = 0
            continue
        revision_req = urllib2.Request(REVISION_URL % (revision))
        revision_webfile = urllib2.urlopen(revision_req)
        revision_data = json.loads(revision_webfile.read())
        revision_message = get_revision_type(revision_data["message"])
        revision_datetime = datetime.datetime.strptime(revision_data["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
        revision_date = revision_datetime.date()

        rev = models.Revision()
        rev.id = revision_data["id"]
        rev.timestamp = revision_datetime
        rev.date = revision_date
        rev.package_id = getCreatePackage_id(get_package_id(revision_data))
        rev.group_id = getCreatePackageGroup_id(get_packagegroup_id(revision_data))
        rev.author = revision_data["author"]
        rev.message = revision_data["message"]
        rev.message_type = revision_message["type"]
        rev.messsage_text = revision_message["text"]
        rev.message_method = revision_message["method"]
        print "Saving revision", revision_data["id"]
        db.session.add(rev)
        if revcount >= 100:
            print "Writing to DB"
            db.session.commit()
            revcount = 0
    # Save at end of loop, as well.
    db.session.commit()

def parse_existing_revision_methods():
    def get_revs(offset):
        revs = db.session.query(models.Revision
                ).limit(10000
                ).offset(offset
                ).all()
        return revs
    offset = 0
    while True:
        revs = get_revs(offset)
        if not revs:
            break
        for rev in revs:
            revmsg = rev.message
            revision_message = get_revision_type(revmsg)
            rev.message_type = revision_message["type"]
            rev.messsage_text = revision_message["text"]
            rev.message_method = revision_message["method"]
            db.session.add(rev)
        offset += 10000
        print "Getting", offset
        db.session.commit()
    return "Done"

def calculate_frequency():
    def check_data_last_four_months(packagegroup_name, packagegroups):
        fourmonths_ago = (datetime.datetime.utcnow()-datetime.timedelta(days=4*30)).date()
        lastfourmonth_dates = filter(lambda d: d>fourmonths_ago, packagegroups[packagegroup_name])
        return len(lastfourmonth_dates)

    def check_data_avg_months_to_publication(packagegroup_name, packagegroups):

        pg_dates = set(packagegroups[packagegroup_name])

        # Check how many days ago earliest date was
        #  If it's greater than 185, use 185 because we should
        #  look only at the last six months.

        ## 2014: Set earliest date to 185 days ago for all orgs

        earliest_date = min(pg_dates)
        earliest_date_days_ago_check=(datetime.datetime.utcnow().date()-earliest_date).days
        if earliest_date_days_ago_check < 185:
            return 190
        earliest_date_days_ago = 185

        # Filter out dates that are more than six months old

        oneyear_ago = (datetime.datetime.utcnow()-datetime.timedelta(days=185)).date()
        the_dates = filter(lambda d: d>oneyear_ago, pg_dates)

        number_months_changes = len(the_dates)

        if number_months_changes == 0:
            return 0

        avg_days_per_change = earliest_date_days_ago/number_months_changes
        return avg_days_per_change

    def generate_data():
        # Get distinct dates for each packagegroup

        data = db.session.query(models.PackageGroup.name, models.Revision.date
                ).outerjoin(models.Package
                ).outerjoin(models.Revision
                ).distinct(
                ).all()

        packagegroups = {}
        for row in data:
            if (row.date and (row.date.date() > datetime.date(year=2014, month=7, day=1))):
                continue

            try:
                packagegroups[row.name].append(datetime.date(row.date.date().year, row.date.date().month, 1))
            except KeyError:
                try:
                    packagegroups[row.name] = []
                    packagegroups[row.name].append(datetime.date(row.date.date().year, row.date.date().month, 1))
                except AttributeError:
                    packagegroups[row.name] = []
                    default_date = datetime.date(year=2000,month=1,day=1)
                    packagegroups[row.name].append(default_date)
            except AttributeError:
                packagegroups[row.name] = []
                default_date = datetime.date(year=2000,month=1,day=1)
                packagegroups[row.name].append(default_date)
                
        return packagegroups

    def get_frequency():
        packagegroups = generate_data()
        for packagegroup in sorted(packagegroups.keys()):
            #lastfour = check_data_last_four_months(packagegroup, packagegroups)
            avgmonths = check_data_avg_months_to_publication(packagegroup, packagegroups)
            #if lastfour >=3:
            #    frequency = "monthly"
            #    comment = "Updated " + str(lastfour) + " times in the last 4 months"
            if avgmonths ==0:
                frequency = FREQUENCY_OVERAYEAR
                comment = "Last updated more than one year ago"
            elif avgmonths<=38:
                frequency = FREQUENCY_MONTHLY
                comment = "Updated on average every " + str(avgmonths) + " days"
            elif avgmonths<=93:
                frequency = FREQUENCY_QUARTERLY
                comment = "Updated on average every " + str(avgmonths) + " days"
            else:
                frequency = FREQUENCY_LTQUARTERLY
                comment = "Updated on average every " + str(avgmonths) + " days"
            yield packagegroup, frequency, comment

    out = ""
    for packagegroup, frequency, comment in get_frequency():
        ps = publishers(packagegroup)
        if not ps:
            continue
        if packagegroup is not None:
            ps.frequency = frequency
            ps.frequency_comment = comment
            db.session.add(ps)
            db.session.commit()
        out += str((packagegroup, frequency, comment)) + "<br />"
    return out

#!/usr/bin/env python

#  IATI Updates, IATI Registry API augmented
#  by Mark Brough
#
#  Copyright (C) 2013 Publish What You Fund
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the GNU Affero General Public License v3.0

import iatiupdates

from iatiupdates import registry

print "getting packagegroups..."
registry.get_packagegroups()
print "getting packages..."
registry.get_packages()
print "getting revisions..."
registry.get_revisions()
print "updating frequencies..."
registry.calculate_frequency()

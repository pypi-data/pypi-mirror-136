# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
rattail-harvest model importers
"""

from rattail.importing.model import ToRattail
from rattail_harvest.db import model


##############################
# harvest cache models
##############################

class HarvestUserImporter(ToRattail):
    model_class = model.HarvestUser

class HarvestClientImporter(ToRattail):
    model_class = model.HarvestClient

class HarvestProjectImporter(ToRattail):
    model_class = model.HarvestProject

class HarvestTaskImporter(ToRattail):
    model_class = model.HarvestTask

class HarvestTimeEntryImporter(ToRattail):
    model_class = model.HarvestTimeEntry

    def cache_query(self):
        query = super(HarvestTimeEntryImporter, self).cache_query()
        return query.filter(self.model_class.spent_date >= self.start_date)\
                    .filter(self.model_class.spent_date <= self.end_date)

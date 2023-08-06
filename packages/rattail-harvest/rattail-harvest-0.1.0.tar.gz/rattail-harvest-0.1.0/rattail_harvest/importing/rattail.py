# -*- coding: utf-8 -*-
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
Rattail -> Rattail data import for Harvest integration
"""

from rattail.importing import rattail as base
from rattail_harvest import importing as rattail_harvest_importing


class FromRattailToRattailHarvestMixin(object):
    """
    Add default registration of custom importers
    """

    def add_harvest_importers(self, importers):
        importers['HarvestUser'] = HarvestUserImporter
        importers['HarvestClient'] = HarvestClientImporter
        importers['HarvestProject'] = HarvestProjectImporter
        importers['HarvestTask'] = HarvestTaskImporter
        importers['HarvestTimeEntry'] = HarvestTimeEntryImporter
        return importers


##############################
# harvest cache models
##############################

class HarvestUserImporter(base.FromRattail, rattail_harvest_importing.model.HarvestUserImporter):
    pass

class HarvestClientImporter(base.FromRattail, rattail_harvest_importing.model.HarvestClientImporter):
    pass

class HarvestProjectImporter(base.FromRattail, rattail_harvest_importing.model.HarvestProjectImporter):
    pass

class HarvestTaskImporter(base.FromRattail, rattail_harvest_importing.model.HarvestTaskImporter):
    pass

class HarvestTimeEntryImporter(base.FromRattail, rattail_harvest_importing.model.HarvestTimeEntryImporter):
    pass

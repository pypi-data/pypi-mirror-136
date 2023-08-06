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
Harvest -> Rattail "cache" data import
"""

import datetime
import decimal
import logging

from rattail import importing
from rattail.util import OrderedDict
from rattail_harvest import importing as rattail_harvest_importing
from rattail_harvest.harvest.webapi import HarvestWebAPI


log = logging.getLogger(__name__)


class FromHarvestToRattail(importing.ToRattailHandler):
    """
    Import handler for data coming from the Harvest API
    """
    host_key = 'harvest'
    host_title = "Harvest (API)"
    generic_host_title = "Harvest (API)"

    def get_importers(self):
        importers = OrderedDict()
        importers['HarvestUser'] = HarvestUserImporter
        importers['HarvestClient'] = HarvestClientImporter
        importers['HarvestProject'] = HarvestProjectImporter
        importers['HarvestTask'] = HarvestTaskImporter
        importers['HarvestTimeEntry'] = HarvestTimeEntryImporter
        return importers


class FromHarvest(importing.Importer):
    """
    Base class for all Harvest importers
    """
    key = 'id'

    @property
    def supported_fields(self):
        fields = list(super(FromHarvest, self).supported_fields)
        fields.remove('uuid')
        return fields

    def setup(self):
        super(FromHarvest, self).setup()

        access_token = self.config.require('harvest', 'api.access_token')
        account_id = self.config.require('harvest', 'api.account_id')
        user_agent = self.config.require('harvest', 'api.user_agent')
        self.webapi = HarvestWebAPI(access_token=access_token,
                                    account_id=account_id,
                                    user_agent=user_agent)

    def time_from_harvest(self, value):
        # all harvest times appear to come as UTC, so no conversion needed
        value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
        return value

    def normalize_host_object(self, obj):
        data = dict(obj)

        if 'created_at' in self.fields:
            data['created_at'] = self.time_from_harvest(data['created_at'])

        if 'updated_at' in self.fields:
            data['updated_at'] = self.time_from_harvest(data['updated_at'])

        return data


class HarvestUserImporter(FromHarvest, rattail_harvest_importing.model.HarvestUserImporter):
    """
    Import user data from Harvest
    """

    @property
    def supported_fields(self):
        fields = list(super(HarvestUserImporter, self).supported_fields)

        # this used to be in harvest i thought, but is no longer?
        fields.remove('name')

        return fields

    def get_host_objects(self):
        return self.webapi.get_users()['users']


class HarvestClientImporter(FromHarvest, rattail_harvest_importing.model.HarvestClientImporter):
    """
    Import client data from Harvest
    """

    def get_host_objects(self):
        return self.webapi.get_clients()['clients']


class HarvestProjectImporter(FromHarvest, rattail_harvest_importing.model.HarvestProjectImporter):
    """
    Import project data from Harvest
    """

    def get_host_objects(self):
        return self.webapi.get_projects()['projects']

    def normalize_host_object(self, project):
        data = super(HarvestProjectImporter, self).normalize_host_object(project)
        if not data:
            return

        data['client_id'] = project['client']['id']

        # cost_budget
        cost_budget = data['cost_budget']
        if cost_budget is not None:
            cost_budget = decimal.Decimal('{:0.2f}'.format(cost_budget))
            data['cost_budget'] = cost_budget

        # fee
        fee = data['fee']
        if fee is not None:
            fee = decimal.Decimal('{:0.2f}'.format(fee))
            data['fee'] = fee

        # starts_on
        starts_on = data['starts_on']
        if starts_on:
            starts_on = datetime.datetime.strptime(starts_on, '%Y-%m-%d')
            data['starts_on'] = starts_on.date()

        # ends_on
        ends_on = data['ends_on']
        if ends_on:
            ends_on = datetime.datetime.strptime(ends_on, '%Y-%m-%d')
            data['ends_on'] = ends_on.date()

        # over_budget_notification_date
        date = data['over_budget_notification_date']
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            data['over_budget_notification_date'] = date.date()

        return data


class HarvestTaskImporter(FromHarvest, rattail_harvest_importing.model.HarvestTaskImporter):
    """
    Import task data from Harvest
    """

    def get_host_objects(self):
        return self.webapi.get_tasks()['tasks']


class HarvestTimeEntryImporter(FromHarvest, rattail_harvest_importing.model.HarvestTimeEntryImporter):
    """
    Import time entry data from Harvest
    """

    def setup(self):
        super(HarvestTimeEntryImporter, self).setup()
        model = self.model

        self.harvest_projects_by_id = self.app.cache_model(self.session,
                                                           model.HarvestProject,
                                                           key='id')

    def get_host_objects(self):
        return self.webapi.get_time_entries(**{'from': self.start_date,
                                               'to': self.end_date})

    def normalize_host_object(self, entry):
        data = super(HarvestTimeEntryImporter, self).normalize_host_object(entry)
        if not data:
            return

        data['user_id'] = entry['user']['id']
        data['client_id'] = entry['client']['id']

        data['project_id'] = entry['project']['id']
        if data['project_id'] not in self.harvest_projects_by_id:
            log.warning("time entry references non-existent project id %s: %s",
                        data['project_id'], entry)
            data['project_id'] = None

        data['task_id'] = entry['task']['id']
        data['invoice_id'] = entry['invoice']['id'] if entry['invoice'] else None

        # spent_date
        spent_date = data['spent_date']
        if spent_date:
            spent_date = datetime.datetime.strptime(spent_date, '%Y-%m-%d')
            data['spent_date'] = spent_date.date()

        # hours
        hours = data['hours']
        if hours is not None:
            hours = decimal.Decimal('{:0.2f}'.format(hours))
            data['hours'] = hours

        return data

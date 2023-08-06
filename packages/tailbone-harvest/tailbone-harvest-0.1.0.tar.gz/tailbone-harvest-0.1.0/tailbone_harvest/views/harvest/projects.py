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
Harvest Project views
"""

from rattail_harvest.db.model import HarvestProject

from .master import HarvestMasterView


class HarvestProjectView(HarvestMasterView):
    """
    Master view for Harvest Projects
    """
    model_class = HarvestProject
    url_prefix = '/harvest/projects'
    route_prefix = 'harvest.projects'

    grid_columns = [
        'id',
        'client',
        'name',
        'code',
        'is_active',
        'is_billable',
        'bill_by',
        'hourly_rate',
        'fee',
    ]

    def configure_grid(self, g):
        super(HarvestProjectView, self).configure_grid(g)
        model = self.model

        g.set_joiner('client', lambda q: q.outerjoin(model.HarvestClient))
        g.set_sorter('client', model.HarvestClient.name)
        g.set_filter('client', model.HarvestClient.name, label="Client Name")
        g.filters['client'].default_active = True
        g.filters['client'].default_verb = 'contains'

        g.set_type('hourly_rate', 'currency')
        g.set_type('fee', 'currency')

        g.set_sort_defaults('client')

        g.set_link('id')
        g.set_link('client')
        g.set_link('name')
        g.set_link('code')


def includeme(config):
    HarvestProjectView.defaults(config)

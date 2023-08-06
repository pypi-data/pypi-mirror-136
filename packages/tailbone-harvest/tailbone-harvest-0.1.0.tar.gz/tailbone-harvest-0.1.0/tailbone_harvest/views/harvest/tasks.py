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
Harvest Task views
"""

from rattail_harvest.db.model import HarvestTask

from .master import HarvestMasterView


class HarvestTaskView(HarvestMasterView):
    """
    Master view for Harvest Tasks
    """
    model_class = HarvestTask
    url_prefix = '/harvest/tasks'
    route_prefix = 'harvest.tasks'

    grid_columns = [
        'id',
        'name',
        'billable_by_default',
        'default_hourly_rate',
        'is_default',
        'is_active',
    ]

    def configure_grid(self, g):
        super(HarvestTaskView, self).configure_grid(g)

        g.set_sort_defaults('name')

        g.set_link('id')
        g.set_link('name')

    def configure_form(self, f):
        super(HarvestTaskView, self).configure_form(f)

        # time_entries
        f.remove_field('time_entries')


def includeme(config):
    HarvestTaskView.defaults(config)

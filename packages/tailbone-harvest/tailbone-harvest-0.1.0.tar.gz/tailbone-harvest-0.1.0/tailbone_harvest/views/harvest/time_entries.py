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
Harvest Time Entry views
"""

from rattail_harvest.db.model import HarvestTimeEntry

from .master import HarvestMasterView


class HarvestTimeEntryView(HarvestMasterView):
    """
    Master view for Harvest Time Entries
    """
    model_class = HarvestTimeEntry
    url_prefix = '/harvest/time-entries'
    route_prefix = 'harvest.time_entries'

    labels = {
        'user_id': "User ID",
        'client_id': "Client ID",
        'project_id': "Project ID",
        'task_id': "Task ID",
        'invoice_id': "Invoice ID",
    }

    grid_columns = [
        'id',
        'spent_date',
        'user',
        'client',
        'project',
        'task',
        'hours',
        'notes',
    ]

    def configure_grid(self, g):
        super(HarvestTimeEntryView, self).configure_grid(g)

        g.set_type('hours', 'duration_hours')

        g.set_sort_defaults('spent_date', 'desc')

        g.set_link('id')
        g.set_link('user')
        g.set_link('client')
        g.set_link('notes')


def includeme(config):
    HarvestTimeEntryView.defaults(config)

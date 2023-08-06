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
Harvest User views
"""

from rattail_harvest.db.model import HarvestUser

from .master import HarvestMasterView


class HarvestUserView(HarvestMasterView):
    """
    Master view for Harvest Users
    """
    model_class = HarvestUser
    url_prefix = '/harvest/users'
    route_prefix = 'harvest.users'

    grid_columns = [
        'id',
        'first_name',
        'last_name',
        'email',
        'telephone',
        'timezone',
        'is_admin',
    ]

    def configure_grid(self, g):
        super(HarvestUserView, self).configure_grid(g)

        g.set_sort_defaults('first_name')

        g.set_link('id')
        g.set_link('first_name')
        g.set_link('last_name')
        g.set_link('email')

    def configure_form(self, f):
        super(HarvestUserView, self).configure_form(f)

        # TODO: should add this as child rows/grid instead
        f.remove('time_entries')


def includeme(config):
    HarvestUserView.defaults(config)

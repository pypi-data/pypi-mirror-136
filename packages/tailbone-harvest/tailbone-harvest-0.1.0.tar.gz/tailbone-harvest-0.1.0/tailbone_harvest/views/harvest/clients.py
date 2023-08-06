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
Harvest Client views
"""

from rattail_harvest.db.model import HarvestClient

from webhelpers2.html import HTML, tags

from .master import HarvestMasterView


class HarvestClientView(HarvestMasterView):
    """
    Master view for Harvest Clients
    """
    model_class = HarvestClient
    url_prefix = '/harvest/clients'
    route_prefix = 'harvest.clients'

    grid_columns = [
        'id',
        'name',
        'currency',
    ]

    def configure_grid(self, g):
        super(HarvestClientView, self).configure_grid(g)

        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'

        g.set_sort_defaults('name')

        g.set_link('id')
        g.set_link('name')

    def configure_form(self, f):
        super(HarvestClientView, self).configure_form(f)

        # projects
        f.set_renderer('projects', self.render_projects)

        # time_entries
        f.remove_field('time_entries')

    def render_projects(self, client, field):
        projects = client.projects
        if not projects:
            return

        items = []
        for project in projects:
            text = "({}) {}".format(project.code, project.name)
            url = self.request.route_url('harvest.projects.view', uuid=project.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)


def includeme(config):
    HarvestClientView.defaults(config)

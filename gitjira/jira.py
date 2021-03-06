#################################################################################
#
#    Copyright 2013 Jairam Chandar & Michael Pitidis
#  
#    This file is part of GitJira.
#
#    GitJira is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GitJira is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GitJira.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
"""
Handle requests to Jira.
"""

import os
import json
import urllib2

from error import HTTPError


class Workflow(object):
    BACKLOG     = 11
    IN_PROGRESS = 4
    REVIEW      = 711
    DONE        = 41


class Jira(object):
    """Perform requests to Jira's REST API."""

    def __init__(self, conf):
        self.conf = conf

    def ticket(self, ticket):
        return self.get(self._api(ticket))

    def mark_in_progress(self, ticket):
        path = self._api(ticket,'transitions?expand=transitions.fields')
        data = json.dumps(dict(transition=dict(id=Workflow.IN_PROGRESS)))
        return self.post(path, data)

    def join(self, *parts):
        assert all(not part.startswith('/') for part in parts), "Expecting relative path"
        return os.path.join(*parts)

    def get(self, path):
        return self._request(path)

    def post(self, path, data):
        return self._request(path, data)

    def _api(self, *parts):
        return self.join('rest/api/latest/issue', *parts)

    def _request(self, path, data=None):
        """Build and perform a request to the JIRA API."""
        url = self.join(self.conf.base_url, path)
        headers = {'Authorization': 'Basic %s' % self.conf.userhash,
                   'Content-Type' : 'application/json'}

        request = urllib2.Request(url, data, headers)
        reply = urllib2.urlopen(request)

        if reply.getcode() >= 400:
            raise HTTPError("Request failed with status %d, url: %s" % (reply.getcode(), url))
        text = reply.read()         #storing the data
        if text:
            text = json.loads(text);
        return text


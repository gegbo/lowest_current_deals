#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
# Starting out by making search bar that will take in a search paramenter and return its result

import webapp2
import os
import jinja2

jinja_environment=jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__)))

# handles input for searches
class SearchHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('/templates/search.html')
        self.response.write(template.render())

#displays search results on a new page /results
# with GCSE, it's also possible to display the search bar and results on the same page,
# instead of two pages as it is here.
class ResultHandler(webapp2.RequestHandler):
    def get(self):
        template=jinja_environment.get_template('/templates/results.html')
        template_variables={"user_search":self.request.get('search')}
        self.response.write(template.render(template_variables))

class WishListHandler(webapp2.RequestHandler):
    def get(self):
        template=jinja_environment.get_template('/templates/wishlist.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', SearchHandler),
    ('/results',ResultHandler),
    ('/wishlist',WishListHandler)
], debug=True)

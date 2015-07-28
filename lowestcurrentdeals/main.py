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
import json
import urllib2
from google.appengine.api import urlfetch

jinja_environment=jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__)))

# handles input for searches
class SearchHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('/templates/search.html')
        self.response.write(template.render())

#displays search results on a new page /results
# In the finished product, searches will display products matching the
# user's search from Best Buy, Walmart
# via their respective APIs

class ResultHandler(webapp2.RequestHandler):
    def post(self):
        # Gets data source for Bestbuy
        bestbuy_data_source = urlfetch.fetch("http://api.remix.bestbuy.com/v1/products(name=%s*)?format=json&show=name,salePrice,image&sort=salePrice.desc&apiKey=24ta6vtsr78a22fmv8ngfjet" %self.request.get('query').replace(' ','+'))
        bestbuy_json_content = bestbuy_data_source.content
        parsed_bestbuy_dictionary = json.loads(bestbuy_json_content)

        # Adds the atributes name, image pic, and price to a bestbuy list
        bestbuy_product=['<img src =%s>' %parsed_bestbuy_dictionary['products'][0]['image'],parsed_bestbuy_dictionary['products'][0]['name'],parsed_bestbuy_dictionary['products'][0]['salePrice']]

        # Gets data source for Walmart

        walmart_data_source = urlfetch.fetch("http://api.walmartlabs.com/v1/search?query=%s&format=json&apiKey=cz9kfm3vuhssnk6hn33zg86k" %self.request.get('query').replace(' ','+'))
        walmart_json_content = walmart_data_source.content
        parsed_walmart_dictionary = json.loads(walmart_json_content)

        # Adds the atributes name, image pic, and price to a walmart list
        walmart_product=['<img src =%s>' %parsed_walmart_dictionary['items'][0]['thumbnailImage'],parsed_walmart_dictionary['items'][0]['name'],parsed_walmart_dictionary['items'][0]['salePrice']]

        template=jinja_environment.get_template('/templates/results.html')
        template_variables={"user_search":self.request.get('search'),'bestbuy':bestbuy_product,'walmart':walmart_product}
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

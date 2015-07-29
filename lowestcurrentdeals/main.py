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
from test_settings import *
from amazon.api import AmazonAPI
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment=jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.dirname(__file__)))

class WishList(ndb.Model):
    user_id = ndb.StringProperty()
    store = ndb.StringProperty()
    item_id = ndb.StringProperty()
    name = ndb.StringProperty()
    price = ndb.StringProperty()
    image = ndb.StringProperty()
    url = ndb.StringProperty()

# handles input for searches
class SearchHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/search.html')
        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        self.response.out.write(template.render({'user' : user, 'greeting' : greeting}))

#displays search results on a new page /results
class ResultHandler(webapp2.RequestHandler):
# In the finished product, searches will display products matching the
# user's search from Best Buy, Walmart, Amazon
# via their respective APIs
    def get(self):
        search = self.request.get('search')
        amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
        amazon_results = amazon.search_n(15, Keywords=search, SearchIndex='All')

        # returns in JSON name, salePrice, and URL of user's search from BestBuy
        best_buy_url = 'http://api.remix.bestbuy.com/v1/products(search='+ search.replace(' ', '&search=')+')?format=json&show=sku,name,salePrice,url,image&pageSize=15&page=5&apiKey=24ta6vtsr78a22fmv8ngfjet'
        best_buy_results = json.load(urllib2.urlopen(best_buy_url)).get('products')

        walmart_url = "http://api.walmartlabs.com/v1/search?query=%s&format=json&apiKey=cz9kfm3vuhssnk6hn33zg86k&responseGroup=base" % search.replace(' ','+')
        walmart_results = json.load(urllib2.urlopen(walmart_url)).get('items')

        results = []
        for product in amazon_results:
            results += [(product.title, product.price_and_currency[0], product.offer_url, product.large_image_url, 'Amazon','placeholder')]
            #How to retrive asin for amazon products and decrease image size
        for product in best_buy_results:
            results += [(product.get('name'), product.get('salePrice'), product.get('url'), product.get('image'), 'Best Buy','/wishlist?type=bestbuy&id=%s'%product.get('sku'))]
        for product in walmart_results:
            results += [(product.get('name'), product.get('salePrice'), product.get('productUrl'), product.get('thumbnailImage'), 'Walmart','/wishlist?type=walmart&id=%s'%product.get('itemId'))]
        results = sorted(results,key=lambda x: x[1])
        template_variables={"user_search":search, 'results':results}

        template=jinja_environment.get_template('/templates/results.html')
        self.response.write(template.render(template_variables))



class WishListHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        person_id = user.user_id()

        store_type = self.request.get('type')
        product_id = self.request.get('id')

        if store_type.lower() == "walmart":
            walmart_url=("http://api.walmartlabs.com/v1/items/%s?format=json&apiKey=cz9kfm3vuhssnk6hn33zg86k" %product_id)
            walmart_JSON_string=json.load(urllib2.urlopen(walmart_url))

            walmart_image_source="<img src=%s>" %walmart_JSON_string["thumbnailImage"]

            walmart_name=walmart_JSON_string["name"]

            sales_Price = str(walmart_JSON_string["salePrice"])

            walmart_link_to_buy = walmart_JSON_string["productUrl"]

            walmart = WishList(user_id = person_id, store = store_type, item_id = product_id,name = walmart_name, price = sales_Price, image = walmart_image_source, url = walmart_link_to_buy)

            walmart.put()

        if store_type.lower() == "bestbuy":
            bestbuy_url=("http://api.remix.bestbuy.com/v1/products/%s.json?show=sku,name,salePrice,url,image&apiKey=24ta6vtsr78a22fmv8ngfjet" %product_id)
            bestbuy_JSON_string=json.load(urllib2.urlopen(bestbuy_url))

            bestbuy_image_source="<img src=%s>" %bestbuy_JSON_string["image"]

            bestbuy_name=bestbuy_JSON_string["name"]

            bestbuy_Price = str(bestbuy_JSON_string["salePrice"])

            bestbuy_link_to_buy = bestbuy_JSON_string["url"]

            bestbuy = WishList(user_id = person_id, store = store_type, item_id = product_id,name = bestbuy_name, price = bestbuy_Price, image = bestbuy_image_source, url = bestbuy_link_to_buy)

            bestbuy.put()

        template=jinja_environment.get_template('/templates/wishlist.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', SearchHandler),
    ('/results',ResultHandler),
    ('/wishlist',WishListHandler)
], debug=True)

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
# user's search from Best Buy, Walmart, Amazon
# via their respective APIs

class ResultHandler(webapp2.RequestHandler):
    def get(self):
        template=jinja_environment.get_template('/templates/results.html')
        template_variables={"user_search":self.request.get('search').replace(" ","%20")}
        self.response.write(template.render(template_variables))
        # returns in JSON name, salePrice, and URL of user's search from BestBuy
        bestbuy_url='http://api.remix.bestbuy.com/v1/products(search='+template_variables["user_search"]+')?format=json&show=sku,name,salePrice,url,image&apiKey=24ta6vtsr78a22fmv8ngfjet'
        bestbuy_JSON_string=json.load(urllib2.urlopen(bestbuy_url))
        # returns in JSON name, salePrice, and URL of user's search from Walmart
        walmart_url="http://api.walmartlabs.com/v1/search?query="+template_variables["user_search"]+"&format=json&numitems=10&apiKey=cz9kfm3vuhssnk6hn33zg86k"
        walmart_JSON_string=json.load(urllib2.urlopen(walmart_url))


        # loop that controls walmart entries

        j=0
        while j<(len(walmart_JSON_string)-1):
            j+=1
            walmart_name=walmart_JSON_string["items"][j]["name"]
            self.response.out.write(walmart_name)

            walmart_image_source=walmart_JSON_string["items"][j]["thumbnailImage"]
            self.response.out.write(("<img src=%s>")%(walmart_image_source))

            self.response.write('Sale Price: '+str(walmart_JSON_string["items"][j]["salePrice"])+"&nbsp;")
            walmart_link_to_buy=str(walmart_JSON_string["items"][j]["productUrl"])
            self.response.write(("<a href=%s>Buy</a>")%walmart_link_to_buy)
            self.response.write("<br>")

        # loop that controls BestBuy entries 
        i=0
        while i<(len(bestbuy_JSON_string)-1):

            i+=1
            bestbuy_name=bestbuy_JSON_string["products"][i]['name']
            self.response.out.write(bestbuy_name+"&nbsp;")

            bestbuy_image_source=bestbuy_JSON_string["products"][i]["image"]
            self.response.write(("<img src=%s>")%(bestbuy_image_source))
            self.response.write('Sale Price: '+str(bestbuy_JSON_string["products"][i]["salePrice"])+"&nbsp;")
            link_to_buy=str(bestbuy_JSON_string["products"][i]["url"])
            self.response.write(("<a href=%s>Buy</a>")%link_to_buy)
            self.response.write("<br>")


class WishListHandler(webapp2.RequestHandler):
    def get(self):
        template=jinja_environment.get_template('/templates/wishlist.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', SearchHandler),
    ('/results',ResultHandler),
    ('/wishlist',WishListHandler)
], debug=True)

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
import logging
from test_settings import *
from amazon.api import AmazonAPI
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail



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
    removeUrl = ndb.StringProperty()
    upc_id = ndb.StringProperty()
    compare_url = ndb.StringProperty()


# handles input for searches
class SearchHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/search.html')
        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s!' %
                        (user.nickname()))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        self.response.out.write(template.render({'user' : user, 'greeting' : greeting, 'logout' : users.create_logout_url('/'), 'login' : users.create_login_url('/')}))

#displays search results on a new page /results
class ResultHandler(webapp2.RequestHandler):
# In the finished product, searches will display products matching the
# user's search from Best Buy, Walmart, Amazon
# via their respective APIs
    def get(self):
        search = self.request.get('search')
        amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG) #initiates a new Amazon API
        amazon_results = amazon.search_n(15, Keywords=search, SearchIndex='All')

        # returns in JSON name, salePrice, and URL of user's search from BestBuy
        best_buy_url = 'http://api.remix.bestbuy.com/v1/products(search='+ search.replace(' ', '&search=')+')?format=json&show=sku,name,salePrice,url,image,upc&pageSize=15&page=5&apiKey=24ta6vtsr78a22fmv8ngfjet'
        best_buy_results = json.load(urllib2.urlopen(best_buy_url)).get('products')

        walmart_url = "http://api.walmartlabs.com/v1/search?query=%s&format=json&apiKey=cz9kfm3vuhssnk6hn33zg86k&responseGroup=base" % search.replace(' ','+')
        walmart_results = json.load(urllib2.urlopen(walmart_url)).get('items')

        results = []
        for product in amazon_results:
            results += [(product.title, product.price_and_currency[0], product.offer_url, product.medium_image_url, 'Amazon','/wishlist?type=amazon&id=%s'%product.asin,"/compare?upc=%s" %str(product.upc), '/email?producturl=%s'%product.offer_url)]
            #How to retrive asin for amazon products and decrease image size
        for product in best_buy_results:
            results += [(product.get('name'), product.get('salePrice'), product.get('url'), product.get('image'), 'Best Buy','/wishlist?type=bestbuy&id=%s'%product.get('sku'),"/compare?upc=%s" %str(product.get('upc')), '/email?producturl=%s'%product.get('url'))]
        for product in walmart_results:
            results += [(product.get('name'), product.get('salePrice'), product.get('productUrl'), product.get('thumbnailImage'), 'Walmart','/wishlist?type=walmart&id=%s'%product.get('itemId'),"/compare?upc=%s" %str(product.get('upc')),'/email?producturl=%s'%product.get('productUrl'))]

        results = sorted(results,key=lambda x: x[1])

        for item in results:
            i = results.index(item)
            if str(item[1])[len(str(item[1]))-2] == '.':
                item = list(item)
                item[1] = str(item[1]) + '0'
                item = tuple(item)
                results[i] = item
        template_variables={"user_search":search, 'results':results, 'user': users.get_current_user(),  'logout' : users.create_logout_url('/'), 'login' : users.create_login_url('/')}
        template=jinja_environment.get_template('/templates/results.html')
        self.response.write(template.render(template_variables))



class WishListHandler(webapp2.RequestHandler):
    def post(self):
        wishlist_item = self.request.get('item')
        self.response.write(wishlist_item)

    def get(self):

        user = users.get_current_user()
        person_id = user.user_id()

        store_type = self.request.get('type')
        product_id = self.request.get('id')

        item_to_add = None

        if store_type.lower() == "walmart":

            logging.info('True for walmart')
            walmart_url=("http://api.walmartlabs.com/v1/items/%s?format=json&apiKey=cz9kfm3vuhssnk6hn33zg86k" %product_id)
            walmart_JSON_string=json.load(urllib2.urlopen(walmart_url))

            walmart_image_source="<img src=%s>" %walmart_JSON_string["thumbnailImage"]

            walmart_name=walmart_JSON_string["name"]

            sales_Price = str(walmart_JSON_string["salePrice"])

            walmart_link_to_buy = walmart_JSON_string["productUrl"]

            walmart_link_to_remove = "/remove?id=%s" %product_id

            walmart_upc = str(walmart_JSON_string["upc"])

            walmart_compare_upc = "/compare?upc=%s" %str(walmart_JSON_string["upc"])


            check_product=WishList.query(WishList.user_id==person_id,WishList.item_id==product_id).get()

            if check_product == None:

                walmart = WishList(user_id = person_id, store = store_type, item_id = product_id,name = walmart_name, price = sales_Price, image = walmart_image_source, url = walmart_link_to_buy,removeUrl=walmart_link_to_remove,upc_id=walmart_upc)
                walmart = WishList(user_id = person_id, store = store_type, item_id = product_id,name = walmart_name, price = sales_Price, image = walmart_image_source, url = walmart_link_to_buy,removeUrl=walmart_link_to_remove,compare_url=walmart_compare_upc)

                walmart.put()
                item_to_add = walmart


        if store_type.lower() == "bestbuy":

            logging.info('True for bestbuy')
            bestbuy_url=("http://api.remix.bestbuy.com/v1/products/%s.json?show=sku,name,salePrice,url,image,upc&apiKey=24ta6vtsr78a22fmv8ngfjet" %product_id)
            bestbuy_JSON_string=json.load(urllib2.urlopen(bestbuy_url))

            bestbuy_image_source="<img src=%s>" %bestbuy_JSON_string["image"]

            bestbuy_name=bestbuy_JSON_string["name"]

            bestbuy_Price = str(bestbuy_JSON_string["salePrice"])

            bestbuy_link_to_buy = bestbuy_JSON_string["url"]

            bestbuy_link_to_remove = "/remove?id=%s" %product_id

            bestbuy_upc = str(bestbuy_JSON_string["upc"])

            check_product=WishList.query(WishList.user_id==person_id,WishList.item_id==product_id).get()
            if check_product == None:
                bestbuy = WishList(user_id = person_id, store = store_type, item_id = product_id,name = bestbuy_name, price = bestbuy_Price, image = bestbuy_image_source, url = bestbuy_link_to_buy,removeUrl=bestbuy_link_to_remove,upc_id = bestbuy_upc,bestbuy_compare_upc = "/compare?upc=%s" %str(bestbuy_JSON_string["upc"]))

            check_product=WishList.query(WishList.user_id==person_id,WishList.item_id==product_id).get()
            if check_product == None:
                bestbuy = WishList(user_id = person_id, store = store_type, item_id = product_id,name = bestbuy_name, price = bestbuy_Price, image = bestbuy_image_source, url = bestbuy_link_to_buy,removeUrl=bestbuy_link_to_remove,compare_url = bestbuy_compare_upc)

                bestbuy.put()
                item_to_add = bestbuy

        if store_type.lower() == "amazon":
            amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG) #initiates a new Amazon API
            product = amazon.lookup(ItemId='%s' %product_id)

            amazon_image_source="<img src=%s>" %product.medium_image_url

            amazon_name=product.title

            amazon_Price = str(product.price_and_currency[0])

            amazon_link_to_buy = product.offer_url

            amazon_link_to_remove = "/remove?id=%s" %product_id

            amazon_upc = str(product.upc)

            check_product=WishList.query(WishList.user_id==person_id,WishList.item_id==product_id).get()
            if check_product == None:
                amazon = WishList(user_id = person_id, store = store_type, item_id = product_id,name = amazon_name, price = amazon_Price, image = amazon_image_source, url = amazon_link_to_buy,removeUrl=amazon_link_to_remove,upc_id = amazon_upc)

            amazon_Price = str(product.price_and_currency[0])

            amazon_link_to_buy = product.offer_url

            amazon_link_to_remove = "/remove?id=%s" %product_id

            amazon_compare_upc = "/compare?upc=%s" %str(product.upc)

            check_product=WishList.query(WishList.user_id==person_id,WishList.item_id==product_id).get()
            if check_product == None:
                amazon = WishList(user_id = person_id, store = store_type, item_id = product_id,name = amazon_name, price = amazon_Price, image = amazon_image_source, url = amazon_link_to_buy,removeUrl=amazon_link_to_remove,compare_url = amazon_compare_upc)

                amazon.put()
                item_to_add = amazon

        template=jinja_environment.get_template('/templates/wishlist.html')
        wishlist_items = WishList.query(WishList.user_id==person_id).fetch()
        if item_to_add:
            wishlist_items.append(item_to_add)

        for item in wishlist_items:
            i = wishlist_items.index(item)
            if str(item.price)[len(str(item.price))-2] == '.':
                item.price = str(item.price) + '0'
                wishlist_items[i] = item

        self.response.write(template.render({'wishlist' : wishlist_items,  'user': users.get_current_user(),  'logout' : users.create_logout_url('/'), 'login' : users.create_login_url('/')}))

class RemoveHandler(webapp2.RequestHandler):
    def removeItem(self,person_id,thing_id):
        product = WishList.query(WishList.user_id==person_id,WishList.item_id==thing_id).get()

        product.key.delete()

    def get(self):

        user = users.get_current_user()
        person_id = user.user_id()

        self.removeItem(person_id,self.request.get('id'))

        template=jinja_environment.get_template('/templates/remove.html')
        self.response.write(template.render({'user': users.get_current_user(), 'logout' : users.create_logout_url('/'), 'login' : users.create_login_url('/')}))

class EmailHandler(webapp2.RequestHandler):
    def getMessageBodyForProductURL(self):
        return """

        Buy Here: %s""" % (
        self.request.get('producturl'))

    # Step two: make the email body look "nice"
    def getMessageBodyForWishlist(self):
        user = users.get_current_user()
        person_id = user.user_id()
        wishlist_items = WishList.query(WishList.user_id==person_id).fetch()

        body_text = "<html><body>"
        for wishlist_item in wishlist_items:
            body_text += 'I found %s for only $%s! Please buy it for me! :) <a href = "%s">Buy item</a><br>' % (
              wishlist_item.name,
              wishlist_item.price,
              wishlist_item.url,
            )
        body_text+="</body></html>"
        return body_text

    def get (self):
        template = jinja_environment.get_template("/templates/emailsent.html")
        self.response.write(template.render())

        user=users.get_current_user()
        # Step 3: Use your new form field to set the to_address.
        to_address = self.request.get('to_address')
        sender_address = user.email()
        subject = "Wishlist from Lowest Current Deals"
        body = self.getMessageBodyForWishlist()
        mail.send_mail(sender_address, to_address, subject, body, html = body)


class CompareHandler(webapp2.RequestHandler):
    def get(self):
        upc_num = self.request.get('upc')

        items = []

        # Add equivalent bestbuy item to a list x
        bestbuy_item=("http://api.remix.bestbuy.com/v1/products(upc=%s)?show=sku,name,salePrice,upc,url,image&apiKey=24ta6vtsr78a22fmv8ngfjet&format=json" %upc_num)
        bestbuy_JSON_string=json.load(urllib2.urlopen(bestbuy_item))

        #checks if list is empty, if it is it wont add to items list
        if len(bestbuy_JSON_string['products']) >0:

            logging.info('Item added to list')
            items += [(bestbuy_JSON_string['products'][0]['name'], bestbuy_JSON_string['products'][0]['salePrice'], bestbuy_JSON_string['products'][0]['url'], bestbuy_JSON_string['products'][0]['image'], 'Best Buy','/wishlist?type=bestbuy&id=%s'%bestbuy_JSON_string['products'][0]['sku'])]

        #Adds equivalent walmart item to a list
        walmart_item=("http://api.walmartlabs.com/v1/items?apiKey=cz9kfm3vuhssnk6hn33zg86k&upc=%s&format=json" %upc_num)

        try:
            walmart_JSON_string=json.load(urllib2.urlopen(walmart_item))

            items += [(walmart_JSON_string['items'][0]['name'], walmart_JSON_string['items'][0]['salePrice'], walmart_JSON_string['items'][0]['productUrl'], walmart_JSON_string['items'][0]['thumbnailImage'], 'Walmart','/wishlist?type=walmart&id=%s'%walmart_JSON_string['items'][0]['itemId'])]
        except urllib2.HTTPError:
            pass

        #Adds equivalent amazon item to a list
        amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG) #initiates a new Amazon API
        amazon_results = amazon.search_n(1,Keywords=upc_num, SearchIndex='All')


        if len(amazon_results) > 0:
            items += [(amazon_results[0].title,
            amazon_results[0].price_and_currency[0],amazon_results[0].offer_url,amazon_results[0].medium_image_url,'amazon','/wishlist?type=amazon&id=%s'%amazon_results[0].asin)]
        template=jinja_environment.get_template('/templates/compare.html')

        for item in items:
            i = items.index(item)
            if str(item[1])[len(str(item[1]))-2] == '.':
                item = list(item)
                item[1] = str(item[1]) + '0'
                item = tuple(item)
                items[i] = item

        template_variables={'results':items,   'user': users.get_current_user(),  'logout' : users.create_logout_url('/'), 'login' : users.create_login_url('/')}
        self.response.write(template.render(template_variables))


app = webapp2.WSGIApplication([
    ('/', SearchHandler),
    ('/results',ResultHandler),
    ('/wishlist',WishListHandler),
    ('/remove', RemoveHandler),
    ('/email',EmailHandler),
    ('/compare',CompareHandler)
], debug=True)

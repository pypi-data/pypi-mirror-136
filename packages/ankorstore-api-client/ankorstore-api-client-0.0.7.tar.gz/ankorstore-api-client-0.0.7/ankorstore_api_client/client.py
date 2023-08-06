import re
import json
from time import sleep

import requests as rq
import pandas as pd

from ankorstore_api_client import utils, resources

class TokenNotFoundError:
    pass

class APIClient:
    BASE_URL = 'https://fr.ankorstore.com'

    def __init__(self, email, password, cookies=None, authenticate=True):
                        
        self._email = email
        self._password = password
        self._base_url = self.BASE_URL

        self._session = rq.Session()

        self._resources = {
            'orders': resources.OrderPool(
                utils.urljoin(self._base_url, 'api/orders'), self._session),
            'products': resources.ProductPool(
                utils.urljoin(self._base_url, 'api/products'), self._session),
            'account': resources.AccountPool(
                utils.urljoin(self._base_url, 'account'), self._session),
            'brand': resources.BrandPool(
                utils.urljoin(self._base_url, 'api/me/brand'), self._session),
            'conversations': resources.ConversationPool(
                utils.urljoin(self._base_url, 'api/conversations'), self._session),
        }

        if not authenticate:
            return

        if not cookies:
            self._authenticate_browser()
        else:
            self._session.cookies.update(cookies)

    def _authenticate(self):
        self._session.headers.update({
            'user-agent': 'Chrome/90.0.4430.212',
            'content-type': 'application/json;charset=UTF-8',
            'accept': 'application/json, text/plain, */*'
        })        
        login_url = utils.urljoin(self._base_url, 'login')
        # retrieve CSRF token
        res = self._session.get(login_url)
        pattern = '<meta name="csrf-token" content="(.+?)">'
        tokens = re.findall(pattern, res.text)
        
        if len(tokens) == 0:
            raise TokenNotFoundError('CSRF Token not found')
        self._session.headers.update({
            'x-csrf-token': tokens[0]
        })
        res = self._session.post(login_url, data=json.dumps({'email': self._email, 'password': self._password}))
        return res

    def _authenticate_browser(self):
        from selenium.webdriver.common.keys import Keys
        login_url = utils.urljoin(self._base_url, 'login')

        browser = utils.init_firefox_browser()
        browser.get(login_url)
        
        email_el = browser.find_element_by_id('email')
        password_el = browser.find_element_by_id('password')
        button = browser.find_element_by_css_selector('.form input')

        email_el.send_keys(self._email)
        password_el.send_keys(self._password)
        button.send_keys(Keys.RETURN)

        sleep(7)

        utils.transfert_cookies(browser, self._session)  
        browser.close()
        return self._session
        
    @property
    def resources(self):
        """Return all resources as a list of Resources"""
        return self._resources

    @property
    def products(self):
        return self._resources['products']

    @property
    def orders(self):
        return self._resources['orders']

    @property
    def account(self):
        return self._resources['account']

    @property
    def brand(self):
        return self._resources['brand']

    @property
    def conversations(self):
        return self._resources['conversations']                

# utilities.py
'''General utility functions used throughout plugin'''

import re
import os
import time
import socket
from httplib import HTTPException
from calibre.library import current_library_path
from calibre_plugins.xray_creator.lib.exceptions import PageDoesNotExist

HEADERS = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"}

BOOK_ID_PAT = re.compile(r'\/show\/([\d]+)')
AMAZON_ASIN_PAT = re.compile(r'data\-asin=\"([a-zA-z0-9]+)\"')
GOODREADS_ASIN_PAT = re.compile(r'"asin":"(.+?)"')
GOODREADS_URL_PAT = re.compile(r'href="(\/book\/show\/.+?)"')

LIBRARY = current_library_path().replace('/', os.sep)

def open_url(connection, url, return_redirect_url=False):
    '''Tries to open url and return page's html'''
    if 'goodreads.com' in url:
        url = url[url.find('goodreads.com') + len('goodreads.com'):]
    try:
        connection.request('GET', url, headers=HEADERS)
        response = connection.getresponse()
        if response.status == 301 or response.status == 302:
            if return_redirect_url:
                return response.msg['location']
            response = open_url(connection, response.msg['location'])
        else:
            response = response.read()
    except (HTTPException, socket.error):
        time.sleep(1)
        connection.close()
        connection.connect()
        connection.request('GET', url, headers=HEADERS)
        response = connection.getresponse()
        if response.status == 301 or response.status == 302:
            if return_redirect_url:
                return response.msg['location']
            response = open_url(connection, response.msg['location'])
        else:
            response = response.read()


    if 'Page Not Found' in response:
        raise PageDoesNotExist('Page not found.')

    return response

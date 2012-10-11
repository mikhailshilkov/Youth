#coding=utf-8

import Cookie
from google.appengine.api import urlfetch

class URLOpener:
    def __init__(self, host = None, cookie_header = None):
        self.host = host
        self.cookie_header = cookie_header
        self.cookie = Cookie.SimpleCookie()
    
    def open(self, url, data = None):
        if data is None:
            method = urlfetch.GET
        else:
            method = urlfetch.POST
        while url is not None:
            response = urlfetch.fetch(url=url,
                          payload=data,
                          method=method,
                          headers=self._getHeaders(method),
                          allow_truncated=False,
                          follow_redirects=False
                          )
            cookie_value = response.headers.get('set-cookie', '')
            self.cookie.load(cookie_value) # Load the cookies from the response
            self.cookie_header = self._makeCookieHeader(self.cookie)
    
            return response
      
    def _getHeaders(self, method):
        headers = {
                 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2 (.NET CLR 3.5.30729)',
                 'Accept': 'application/json',
                 'Cookie' : self.cookie_header,
                 'Origin': ('http://' + self.host) if self.host is not None else None,
                 'Referer': ('http://' + self.host) if self.host is not None else None
                  }
        return headers

    def _makeCookieHeader(self, cookie):
        cookieHeader = ""
        for value in cookie.values():
            cookieHeader += "%s=%s; " % (value.key, value.value)
        return cookieHeader

import httplib
import urllib
import urllib2 
import re
import csv
import lxml.etree as etree
import lxml.html as html
import traceback
import gzip
import random
import time
import sys

from cookielib import Cookie, CookieJar
from StringIO import StringIO


class pyGoogleTrendsCsvDownloader(object):
    '''
    Google Trends Downloader
    
    Recommended usage:
    
    from pyGoogleTrendsCsvDownloader import pyGoogleTrendsCsvDownloader
    r = pyGoogleTrendsCsvDownloader(username, password)
    r.get_csv(cat='0-958', geo='US-ME-500')
    
    '''
    def __init__(self, username, password):
        '''
        Provide login and password to be used to connect to Google Trends
        All immutable system variables are also defined here
        '''
        
        # The amount of time (in secs) that the script should wait before making a request.
        # This can be used to throttle the downloading speed to avoid hitting servers too hard.
        # It is further randomized.
        self.download_delay = 0.25
        
        self.service = "trendspro"
        self.url_service = "http://www.google.com/trends/"
        self.url_download = self.url_service + "trendsReport?"
        
        self.login_params = {}
        # These headers are necessary, otherwise Google will flag the request at your account level
        self.headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'),
                        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                        ("Accept-Language", "en-gb,en;q=0.5"),
                        ("Accept-Encoding", "gzip, deflate"),
                        ("Connection", "keep-alive")]
        self.url_login = 'https://accounts.google.com/ServiceLogin?service='+self.service+'&passive=1209600&continue='+self.url_service+'&followup='+self.url_service
        self.url_authenticate = 'https://accounts.google.com/accounts/ServiceLoginAuth'
        self.header_dictionary = {}
        
        self._authenticate(username, password)
        
    def _authenticate(self, username, password):
        '''
        Authenticate to Google:
        1 - make a GET request to the Login webpage so we can get the login form
        2 - make a POST request with email, password and login form input values
        '''
        
        # Make sure we get CSV results in English
        ck = Cookie(version=0, name='I4SUserLocale', value='en_US', port=None, port_specified=False, domain='www.google.com', domain_specified=False,domain_initial_dot=False, path='/trends', path_specified=True, secure=False, expires=None, discard=False, comment=None, comment_url=None, rest=None)
        ck_pref = Cookie(version=0, name='PREF', value='', port=None, port_specified=False, domain='www.google.com', domain_specified=False,domain_initial_dot=False, path='/trends', path_specified=True, secure=False, expires=None, discard=False, comment=None, comment_url=None, rest=None) 

        self.cj = CookieJar()                            
        self.cj.set_cookie(ck)
        self.cj.set_cookie(ck_pref)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = self.headers
        
        # Get all of the login form input values
        find_inputs = etree.XPath("//form[@id='gaia_loginform']//input")
        try:
            #
            resp = self.opener.open(self.url_login)
            
            if resp.info().get('Content-Encoding') == 'gzip':
                buf = StringIO( resp.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else:
                data = resp.read()
            
            xmlTree = etree.fromstring(data, parser=html.HTMLParser(recover=True, remove_comments=True))
            
            for input in find_inputs(xmlTree):
                name = input.get('name')
                if name:
                    name = name.encode('utf8')
                    value = input.get('value', '').encode('utf8')
                    self.login_params[name] = value
        except:
            print("Exception while parsing: %s\n" % traceback.format_exc())    
        
        self.login_params["Email"] = username
        self.login_params["Passwd"] = password
        
        params = urllib.urlencode(self.login_params)
        self.opener.open(self.url_authenticate, params)
        
    def get_csv(self, throttle=False, **kwargs):
        '''
        Download CSV reports
        '''
        
        # Randomized download delay
        if throttle:
            r = random.uniform(0.5 * self.download_delay, 1.5 * self.download_delay)
            time.sleep(r)
        
        params = {
            'export': 1
        }
        params.update(kwargs)
        params = urllib.urlencode(params)
        
        r = self.opener.open(self.url_download + params)
        
        # Make sure everything is working ;)
        if not r.info().has_key('Content-Disposition'):
            print "You've exceeded your quota. Continue tomorrow..."
            sys.exit(0)
            
        if r.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( r.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = r.read()
        
        myFile = open('trends_%s.csv' % '_'.join(['%s-%s' % (key, ''.join([char for char in value if char.isalnum()])) for (key, value) in kwargs.items()]), 'w')
        myFile.write(data)
        myFile.close()

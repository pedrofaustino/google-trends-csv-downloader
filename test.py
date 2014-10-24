from pyGoogleTrendsCsvDownloader import pyGoogleTrendsCsvDownloader
import time
from random import randint

google_username = '<your email address>'
google_pass = '<your password>'

# Create the csv downloader object
downloader = pyGoogleTrendsCsvDownloader(google_username, google_pass)

# Wait some time to avoid blocking by google
time.sleep(randint(0, 5))

# Attributes for the url
kwargs = {'hl':'en-US', 'q':'\"Pizza\"', 'cmpt':'q', 'content' :'1'}

downloader.get_csv(**kwargs)

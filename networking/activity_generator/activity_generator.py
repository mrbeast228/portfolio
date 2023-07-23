import os
import sys
import stat
from time import sleep, time_ns
from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from warnings import filterwarnings as filt
from os.path import expanduser as pathFormat
from random import randint, choice, uniform
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from argparse import ArgumentParser

# Get absolute path to resource, works for dev and for PyInstaller (if needed to pack Webdriver)
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Selener:
	driver = None
	profileDest = ""

	def __init__(self, proxy_address, proxy_port, proxy_username, proxy_password):
		options = Options()
		options.headless = True

		seleniumwire_options = {
			'proxy': {
				'http': f'http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}',
				'verify_ssl': False,
			},
		}

		profile = webdriver.FirefoxProfile()
		profile.set_preference("general.useragent.override", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36")

		firefox_capabilities = DesiredCapabilities.FIREFOX
		firefox_capabilities['marionette'] = True
		self.driver = webdriver.Firefox(profile, capabilities=firefox_capabilities, options=options, seleniumwire_options=seleniumwire_options)

	def TGScroll(self, url, timer):
		self.driver.get('https://upos-repo.ru')

		if not url.startswith('http'):
			url = 'http://' + url

		expandedUrl = url # don't use expand for tglink
		realUrl = expandedUrl.split('?')[0]

		if realUrl.count('/') == 2:
			realUrl += '/'

		source = ['telegram', 'tg']
		medium = ['social', 'cpc']

		realUrl += '?utm_source={}&utm_medium={}'.format(choice(source), choice(medium))
		self.driver.execute_script('window.open("{}");'.format(realUrl))
		sleep(10)
		self.driver.switch_to.window(self.driver.window_handles[1])

		steps = int(timer / 3)
		for i in range(steps):
			self.driver.execute_script(f"window.scrollBy(0, document.body.scrollHeight / {steps});")
			sleep(uniform(2.0, 4.0))

	def close(self):
		if self.driver is not None:
			self.driver.quit()

	def __del__(self):
		self.close()

# run scrolling
def scroller(url, timer, repeat, proxyListPath):
	for i in range(repeat):
		proxy = choice(open(proxyListPath, 'r').read().splitlines()).split(' ')
		selener = Selener(proxy[0], proxy[1], proxy[2], proxy[3])
		try:
			selener.TGScroll(url, timer)
		except Exception as e:
			pass
		sleep(uniform(300, 1000))
		selener.close()

if __name__ == "__main__":
	parser = ArgumentParser()

	parser.add_argument('--url', required=True) # URL to make activity
	parser.add_argument('-t', '--timer', default=100, required=False) # time of scrolling of page
	parser.add_argument('-r', '--repeats', default=10, required=False) # how much times reopen page
	parser.add_argument('-p', '--proxy-list', required=True) # file with list of proxies
	args = parser.parse_args()

	scroller(args.url, args.timer, args.repeats, args.proxy_list)

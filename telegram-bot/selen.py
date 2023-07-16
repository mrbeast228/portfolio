from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from warnings import filterwarnings as filt
from os.path import expanduser as pathFormat
from random import randint

filt("ignore", category=DeprecationWarning)

class Selener:
	driver = None

	def __init__(self, profile):
		options = Options()
		options.headless = True
		options.add_argument("-profile")
		options.add_argument(pathFormat('~/.mozilla/firefox/' + profile))
		firefox_capabilities = DesiredCapabilities.FIREFOX
		firefox_capabilities['marionette'] = True
		self.driver = webdriver.Firefox(capabilities=firefox_capabilities, options=options)

	def openBulletin(self, bulletinNumber):
		self.driver.get("https://www.farpost.ru/personal/actual/bulletins")
		bulletins = self.driver.find_elements(By.XPATH, "//*[contains(@id,'bulletinId')]")
		sleep(2)
		bulletins[bulletinNumber].find_element(By.XPATH, "./child::*//*[@data-role = 'bulletin-link']").click()

	def bulletinCasino(self, state = 2):
		# fix 16042023 - "Изменить ставку" is no more showing
		self.driver.find_element(By.CLASS_NAME, 'service-card-head').send_keys(Keys.RETURN)
		WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'priceFieldPanel')))
		sleep(3)

		self.driver.find_element(By.LINK_TEXT, 'Грузоперевозки' if state == 1 else 'Грузчики').send_keys(Keys.RETURN)
		WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'priceFieldPanel')))
		sleep(5)

		# first place bug solving
		if self.driver.find_element(By.ID, 'priceFieldPanel').text.splitlines()[2] == 'за 1 место':
			self.driver.find_element(By.XPATH, "//*[contains(@class,'spin_down')]").click()

		inputField = self.driver.find_element(By.ID, 'stickPrice')
		startPrice = int(inputField.get_attribute('value'))
		result = [startPrice]

		for i in range(1000):
			if self.driver.find_element(By.ID, 'priceFieldPanel').text.splitlines()[2] == 'за 1 место':
				break
			self.driver.find_element(By.XPATH, "//*[contains(@class,'spin_up')]").click()
			result.insert(0, int(inputField.get_attribute('value')))

		inputField.send_keys(Keys.CONTROL + "a")
		inputField.send_keys(Keys.DELETE)
		inputField.send_keys(str(startPrice))
		self.driver.find_element(By.XPATH, "//*[contains(@class,'spin_down')]").click()

		for i in range(1000):
			curPrice = int(self.driver.find_element(By.ID, 'stickPrice').get_attribute('value'))
			if result and result[-1] == curPrice:
				break
			result.append(curPrice)
			self.driver.find_element(By.XPATH, "//*[contains(@class,'spin_down')]").click()

		# WARNING: don't close this page!
		return result

	def strategy(self, prices, limit, diff):
		countPrices = len(prices)
		if countPrices == 0:
			return 0
		for i in range(countPrices):
			if limit >= prices[i]:
				if prices[i] - prices[i + 1] >= diff:
					return prices[i + 1] + 10
				return prices[i] + 10
		return limit

	def setPrice(self, price):
		inputField = self.driver.find_element(By.ID, 'stickPrice')

		# WARNING: very important to clear!
		inputField.send_keys(Keys.CONTROL + "a")
		inputField.send_keys(Keys.DELETE)

		inputField.send_keys(str(price))
		self.driver.find_element(By.ID, 'confirm').click()

	def runMulti(self, modes):
		bullcount = len(modes)
		for bulletinNumber in range(bullcount):
			sleep(2)
			self.openBulletin(bulletinNumber)
			prices = self.bulletinCasino(int(modes[bulletinNumber][0]))
			targetPrice = self.strategy(prices, int(modes[bulletinNumber][1]), int(modes[bulletinNumber][2]))
			self.setPrice(targetPrice)

	def close(self):
		if self.driver is not None:
			self.driver.close()

class Buller:
	selener = None

	def __init__(self, profile):
		self.selener = Selener(profile)

	def bull(self, modes):
		self.selener.runMulti(modes)

	def __del__(self):
		if self.selener is not None:
			self.selener.close()

buller = Buller('n6nymtue.default-esr')

bullerDataFile = open('.buller-data', 'r')
bullerData = []
for bulletinProps in bullerDataFile:
	bullerData.append(bulletinProps.split())
bullerDataFile.close()

buller.bull(bullerData)

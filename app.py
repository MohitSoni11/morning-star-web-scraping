#############
## Imports ##
#############

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

import selenium
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

######################
## Helper Functions ##
######################

def login_morningstar():
  # Starting web-scraper and making browser headless
  options = Options()
  #options.add_argument('--headless')
  
  browser = webdriver.Chrome(options=options)
  browser.get('https://evgcatalog.kcls.org/eg/opac/ezproxy/login?qurl=https://ar.morningstar.com%2fmirc%2fhome.aspx')
  browser.maximize_window()
  
  barcode_input = browser.find_element(By.ID, 'barcode-input')
  password_input = browser.find_element(By.ID, 'password-input')
  barcode_input.send_keys('9340044928')
  password_input.send_keys('0035')
  password_input.submit()
  
  # Waiting for at most 30 seconds to allow morningstar to load
  browser.implicitly_wait(30)
  return browser

def get_ticker_info(browser, ticker):
  data = []
  
  # Searching for ticker
  search_bar = browser.find_element(By.XPATH, "//input[@class='mdc-search-field__input mds-search-field__input__rxp']")
  search_bar.send_keys(ticker)
  search_bar.submit()
  
  # Go to ticker page
  ticker_button = browser.find_element(By.XPATH, "//a[@class='mdc-security-module__name mdc-link__rxp mdc-link--no-underline__rxp']")
  ticker_button.click()
  
  # Getting information under Morningstar Fundamentals (except the Sustainability section)
  data += get_fundamental_info(browser)
    
  return data

def get_fundamental_info(browser):
  data = []
  fundamental_section = browser.find_element(By.ID, 'sal-components-eqsv-overview')
  
  # Looping through first three lists in fundamental_section and getting all data
  for i in range(3):
    lists = fundamental_section.find_elements(By.CSS_SELECTOR, 'ul')[i]
    
    for element in lists.find_elements(By.CSS_SELECTOR, 'p.sal-dp-value'):
      data.append(element.text)
      
    for element in lists.find_elements(By.CSS_SELECTOR, 'span.sal-dp-value'):
      data.append(element.text)
  
  return data

######################
## Initializing App ##
######################

app = Flask(__name__)

######################
## Global Variables ##
######################

tickers = []
browser = login_morningstar()

#############
## Routing ##
#############

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/add-ticker', methods=['POST'])
def addTicker():
  tickers.append(request.form['ticker'])
  return redirect('/', data=get_ticker_info(browser, request.form['ticker']))
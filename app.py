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
## Initializing App ##
######################

app = Flask(__name__)

######################
## Global Variables ##
######################

tickers = []

#############
## Routing ##
#############

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/add-ticker', methods=['POST'])
def addTicker():
  tickers.append(request.form['ticker'])
  get_info(request.form['ticker'])
  return redirect('/')

def get_info(ticker):
  # Starting web-scraper and making browser headless
  options = Options()
  options.add_argument('--headless')
  
  browser = webdriver.Edge(options=options)
  browser.get('https://evgcatalog.kcls.org/eg/opac/ezproxy/login?qurl=https://ar.morningstar.com%2fmirc%2fhome.aspx')
  browser.maximize_window()
  
  # Login to morningstar
  barcode_input = browser.find_element(By.ID, 'barcode-input')
  password_input = browser.find_element(By.ID, 'password-input')
  barcode_input.send_keys('9340044928')
  password_input.send_keys('0035')
  password_input.submit()
  
  # Waiting for at most 30 seconds to allow morningstar to load
  browser.implicitly_wait(30)
  
  # Go to ticker page
  search_bar = browser.find_element(By.XPATH, "//input[@class='mdc-search-field__input mds-search-field__input__rxp']")
  search_bar.send_keys(ticker)
  search_bar.submit()
  
  ticker_button = browser.find_element(By.XPATH, "//a[@class='mdc-security-module__name mdc-link__rxp mdc-link--no-underline__rxp']")
  ticker_button.click()
  
  for element in browser.find_elements(By.XPATH, "//p[@class='sal-dp-value']"):
    print(element.text + ",")
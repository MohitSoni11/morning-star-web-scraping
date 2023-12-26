#############
## Imports ##
#############

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from flask_sqlalchemy import SQLAlchemy

######################
## Helper Functions ##
######################

def login_morningstar():
  # Starting web-scraper and making browser headless
  options = Options()
  options.add_argument('--headless')
  
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
  
  # Getting information under Morningstar Fundamentals
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

def push_to_database(ticker, data):
  return

def retrieve_from_database(ticker):
  return

######################
## Initializing App ##
######################

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

###########################
## Initializing Database ##
###########################

db = SQLAlchemy(app)

#with app.app_context():
#  db.create_all()
  
class Ticker(db.Model):
  ticker = db.Column(db.String(50), nullable=False, unique=True, primary_key=True)
  ticker_fundamental_data = db.Column(db.String(300))

######################
## Global Variables ##
######################

ticker_data = {}
browser = login_morningstar()
labels = ['Last Price', 'Fair Value', 'Uncertainty', '1-Star Price', '5-Star Price', 'Economic Moat', 'Capital Allocation', 'Controversy Level',
          'Top Material ESG Issue', 'Investment Style', 'Sector', 'Industry', 'Day Range', 'Year Range', 'Market Cap', 'Volume/Avg', 'Price/Sales',
          'Price/Book', 'Price/Earnings', 'Forward Div Yield']

#############
## Routing ##
#############

@app.route('/')
def home():
  return render_template('home.html', ticker_data=ticker_data, labels=labels)

@app.route('/add-ticker', methods=['POST'])
def addTicker():
  data = get_ticker_info(browser, request.form['ticker'])
  ticker_data[request.form['ticker']] = data
  return redirect('/')
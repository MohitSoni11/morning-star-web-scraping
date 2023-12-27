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
## Initializing App ##
######################

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

###########################
## Initializing Database ##
###########################

db = SQLAlchemy(app)
  
class Ticker(db.Model):
  _id = db.Column('id', db.Integer, primary_key=True)
  ticker = db.Column(db.String(50), nullable=False, unique=True)
  fundamental_data = db.Column(db.String(300))

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

def push_to_db(ticker, fundamental_data):
  fundamental_data_string = "#".join(fundamental_data)
  
  # Only changing ticker data if ticker is already in db
  ticker_found = Ticker.query.filter_by(ticker=ticker).first()
  if ticker_found:
    ticker_found.fundamental_data = fundamental_data_string
    db.session.commit()
  
  # Adding ticker and data if ticker is not already in db
  else:
    new_db_element = Ticker(ticker=ticker, fundamental_data=fundamental_data_string)
    db.session.add(new_db_element)
    db.session.commit()
    
def remove_from_db(ticker):
  # Only removing ticker if it is already in db
  ticker_found = Ticker.query.filter_by(ticker=ticker).first()
  if (ticker_found):
    ticker = Ticker.query.filter_by(ticker=ticker)
    ticker.delete()
    db.session.commit()
    return True
  
  return False

def retrieve_from_db():
  ticker_data = {}
  
  # Looping through all Tickers in database
  for curr_ticker in Ticker.query.all():
    ticker_data[curr_ticker.ticker] = curr_ticker.fundamental_data.split('#')
  
  return ticker_data

def refresh_db():
  for curr_ticker in Ticker.query.all():
    ticker = curr_ticker.ticker
    data = get_ticker_info(browser, ticker)
    push_to_db(ticker, data)
    
  return True

def clear_db():
  for curr_ticker in Ticker.query.all():
    ticker = Ticker.query.filter_by(ticker=curr_ticker.ticker)
    ticker.delete()
    db.session.commit()  
    
  return True

######################
## Global Variables ##
######################

browser = login_morningstar()
fundamental_labels = ['Last Price', 'Current Value', 'Fair Value', 'Uncertainty', '1-Star Price', '5-Star Price', 'Economic Moat', 'Capital Allocation', 'Controversy Level',
          'Top Material ESG Issue', 'Investment Style', 'Sector', 'Industry', 'Day Range', 'Year Range', 'Market Cap', 'Volume/Avg', 'Price/Sales',
          'Price/Book', 'Price/Earnings', 'Forward Div Yield']

#############
## Routing ##
#############

@app.route('/')
def home():
  return render_template('home.html', ticker_data=retrieve_from_db(), fundamental_labels=fundamental_labels)

@app.route('/add-ticker', methods=['POST'])
def addTicker():
  ticker = request.form['ticker']
  data = get_ticker_info(browser, ticker)
  push_to_db(ticker, data)
  return redirect('/')

@app.route('/remove-ticker', methods=['POST'])
def removeTicker():
  ticker = request.form['ticker']
  remove_from_db(ticker)
  return redirect('/')

@app.route('/refresh', methods=['POST'])
def refresh():
  refresh_db()
  return redirect('/')

@app.route('/clear', methods=['POST'])
def clear():
  clear_db()
  return redirect('/')
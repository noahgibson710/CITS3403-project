import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Update this path to your local chromedriver if needed
CHROMEDRIVER_PATH = 'chromedriver'

@pytest.fixture(scope='module')
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_homepage_loads(driver):
    driver.get('http://localhost:5000/')
    assert 'Health Macro Calculator' in driver.page_source

def test_signup_flow(driver):
    driver.get('http://localhost:5000/signup')
    driver.find_element(By.NAME, 'name').send_keys('seleniumuser')
    driver.find_element(By.NAME, 'email').send_keys('seleniumuser@example.com')
    driver.find_element(By.NAME, 'password').send_keys('SeleniumPass123!')
    driver.find_element(By.NAME, 'gender').send_keys('Male')
    driver.find_element(By.NAME, 'age').send_keys('25')
    driver.find_element(By.CSS_SELECTOR, 'form button[type=submit], form input[type=submit]').click()
    time.sleep(1)
    assert 'Login' in driver.page_source or 'Sign in' in driver.page_source

def test_login_flow(driver):
    driver.get('http://localhost:5000/login')
    driver.find_element(By.NAME, 'email').send_keys('seleniumuser@example.com')
    driver.find_element(By.NAME, 'password').send_keys('SeleniumPass123!')
    driver.find_element(By.CSS_SELECTOR, 'form button[type=submit], form input[type=submit]').click()
    time.sleep(1)
    assert 'Logout' in driver.page_source or 'Profile' in driver.page_source

def test_calculator_page_loads(driver):
    driver.get('http://localhost:5000/calculator')
    assert 'Calculator Form' in driver.page_source

def test_calculator_form_interaction(driver):
    driver.get('http://localhost:5000/calculator')
    driver.find_element(By.ID, 'gender').send_keys('male')
    driver.find_element(By.ID, 'age').send_keys('30')
    driver.find_element(By.ID, 'weight').send_keys('70')
    driver.find_element(By.ID, 'height').send_keys('175')
    driver.find_element(By.ID, 'activity').send_keys('1.2')
    driver.find_element(By.ID, 'calorie').send_keys('surplus')
    # Simulate form submission if possible
    driver.find_element(By.CSS_SELECTOR, 'form').submit()
    time.sleep(1)
    # Check for some result or confirmation (update as per app's response)
    assert 'Calculator Form' in driver.page_source  # Adjust as needed 
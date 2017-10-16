
# coding: utf-8

# In[6]:

import bs4
import re
import selenium
import requests
import json
import csv 
import time
import os
import sys
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import *
#from fake_useragent import UserAgent
from unidecode import unidecode
import pandas as pd
import collections
import datetime


# In[17]:

home_page = 'https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentType'

#driver = webdriver.Chrome('/Users/Lucinda/chromedriver')
#driver.get(home_page)

display = Display(visible=0, size=(1024, 768))
display.start()

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11")


caps = webdriver.DesiredCapabilities().FIREFOX
caps["marionette"] = False
driver = webdriver.Firefox(capabilities=caps,firefox_profile=profile)
driver.wait = WebDriverWait(driver, 5)

# driver = webdriver.Chrome('/home/ubuntu/We3/LU/chromedriver')
driver.get(home_page)
# delay = 5 
# driver.implicitly_wait(5)
driver.save_screenshot('screen.png')


DocClass = 'DEEDS AND OTHER CONVEYANCES'
DocType = 'DEED'
DateRange = 'Specific Date Range'

try:
    select = Select(driver.find_element_by_xpath("/html/body/div/form/table/tbody/tr/td/table[1]/tbody/tr/td[1]/select"))
    select.select_by_visible_text(DocClass)
    time.sleep(2)
except NoSuchElementException:
    print 'Doc Class Selection not loaded'


    
#-----
try:
    select = Select(driver.find_element_by_xpath('//*[@id="DocType"]/select'))
    select.select_by_visible_text(DocType)
    time.sleep(2)
    
except NoSuchElementException:
    print 'Doc Type Selection not loaded'


#-----
try:
    select = Select(driver.find_element_by_xpath("/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[1]/td[1]/font/font/select"))
    select.select_by_visible_text(DateRange)
    time.sleep(2)
except NoSuchElementException:
    print 'Date Range Selection not loaded'

#-----


def send_keys(value, xpath):
    key_input = driver.find_element_by_xpath(xpath)
    key_input.send_keys(value)
    
now = datetime.datetime.now()

#From
# MM/DD/YYYY
try:
    #send month
    send_keys(str(now.month),"/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[1]/td[2]/div/font/font[3]/input")
    time.sleep(3)
    #send date
    send_keys(str(now.day),"/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[1]/td[2]/div/font/font[3]/font[2]/input")
    time.sleep(3)
    #send year
    send_keys(str(now.year),"/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[1]/td[2]/div/font/font[3]/font[2]/font[2]/input")
    time.sleep(3)
except NoSuchElementException:
    print 'From Date Input elements not found'

    
#Through
# MM/DD/YYYY
try:
    #send month
    send_keys(str(now.month),"/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[1]/td[2]/div/font/font[3]/font[2]/font[2]/font[2]/input")
    time.sleep(3)
    #send date
    send_keys(str(now.day),"/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[1]/td[2]/div/font/font[3]/font[2]/font[2]/font[2]/font[2]/input")
    time.sleep(3)
    #send year
    send_keys(str(now.year),"/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr[1]/td[2]/div/font/font[3]/font[2]/font[2]/font[2]/font[2]/font[2]/input")
    
except NoSuchElementException:
    print 'Through Input elements not found'
    
    
try:
    SearchButton = driver.find_element_by_xpath("/html/body/div/form/table/tbody/tr/td/table[2]/tbody/tr/td/font/b/table/tbody/tr/td[1]/input[1]")
    SearchButton.click()
    print 'Search Button found'
except NoSuchElementException:
    print 'Search Button elements not found'

try:
    MaxNum = '99'
    MaxRowsSelect = Select(driver.find_element_by_xpath("/html/body/form[1]/table/tbody/tr[1]/td/font/select"))
    MaxRowsSelect.select_by_visible_text(MaxNum)
    print "Max Row Number is", MaxNum
except NoSuchElementException:
    print 'Max Rows Selection not loaded'
    
    
id_list = []

# grab the data
while True:

    try:       
        for each in driver.find_elements_by_name("DET"):
            ID_string = each.get_attribute("onclick").encode('ascii', 'ignore') 
            doc_id = str(filter(str.isdigit, ID_string))
            id_list.append(doc_id)
            print doc_id
            #writer.writerow(doc_id)
        time.sleep(3)
        
        next_button_path = "/html/body/form[1]/table/tbody/tr[1]/td/font//a[@href='JavaScript:go_next()']"
        go_next_button = driver.find_element_by_xpath(next_button_path)
        go_next_button.click()
        print "Go to Next Page"
        time.sleep(3)

    except NoSuchElementException:
        
        print 'Go Next Button not loaded --> Last Page'
        break


with open("deed_ids.csv", "wb") as f:
    writer = csv.writer(f)
    for item in id_list:
        writer.writerow([item,])


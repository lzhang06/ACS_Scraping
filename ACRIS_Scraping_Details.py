
# coding: utf-8

# In[40]:

import bs4
import re
import selenium
import requests
import json
import csv 
import time
import os
import sys
#from pyvirtualdisplay import Display
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
from pyvirtualdisplay import Display



# In[38]:

with open('deed_ids.csv','rb') as file:
    rows = csv.reader(file, 
                      delimiter = ',', 
                      quotechar = '"')
    deed_doc_ids = [data for data in rows]
    

iteration = 0

# driver = webdriver.Chrome('/Users/Lucinda/chromedriver')
# driver.wait = WebDriverWait(driver, 1)

display = Display(visible=0, size=(1024, 768))
display.start()


profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11")


caps = webdriver.DesiredCapabilities().FIREFOX
caps["marionette"] = False
driver = webdriver.Firefox(capabilities=caps,firefox_profile=profile)
driver.wait = WebDriverWait(driver, 5)

with open('ACRIS_DeedDoc_details.csv','a') as f:
    filewriter = csv.writer(f)
    
    CSV_Header = ["document_id","CRFN","doc_type","acris_street_number","acris_street_name","acris_addr_unit",
"document_amt","recorded_datetime","document_date","borough","block","lot","easement","partial_lot",
"subterranean_rights","air_rights","property_type","reel_year","reel_pg","reel_nbr","party_json",
"party1_type","party2_type","party3_type","party1","party2","party3"]

    filewriter.writerow(CSV_Header)
    

    for each in deed_doc_ids:

        deed_doc_id = each[0]
        print deed_doc_id
        iteration += 1
        print 'In Iteration %d ' % iteration

        doc_url = 'https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentDetail?doc_id='+deed_doc_id
        driver.get(doc_url)  

        #------
        delay = 5 
        driver.implicitly_wait(delay)

        acris_dict = collections.OrderedDict()
        document_id = driver.current_url.split("=")[1].encode('ascii', 'ignore')

        #------Doc_Detail------
        Path_Doc_Detail = '/html/body/table[4]/tbody/tr/td/table[2]/tbody'
        Doc_Detail_Table = driver.find_element_by_xpath(Path_Doc_Detail)
        acris_dict['Doc_Detail'] = collections.OrderedDict()

        Doc_Text = unidecode(Doc_Detail_Table.text)


        Doc_Header = ['DOCUMENT ID', 'CRFN','COLLATERAL','# of PAGES', 'REEL-PAGE', 'EXPIRATION DATE', 'DOC. TYPE', 'FILE NUMBER',
        'ASSESSMENT DATE', 'DOC. DATE', 'ECORDED / FILED','SLID #', 'DOC. AMOUNT','BOROUGH', '% TRANSFERRED','RPTT #', 
        'MAP SEQUENCE #', 'MESSAGE']

        for each in Doc_Header:
            re_search = each+":\s(.*?)\s"
            match = re.search(re_search, Doc_Text)
            if match:
                result = match.group(1)
                acris_dict['Doc_Detail'][each] = result.encode('ascii', 'ignore')
            else:
                acris_dict['Doc_Detail'][each] = ""



        #---------Party1--------------

        #encode by table and by row
        Path_Party1 = '(//*[@id="ABPOSITION"]/table/tbody)[position()=1]'
        Party1_Table = driver.find_element_by_xpath(Path_Party1)
        acris_dict['Party1'] = collections.OrderedDict()

        PARTY1_header = [unidecode(header.text) for header in driver.find_element_by_xpath('/html/body/table[4]/tbody/tr/td/table[3]/tbody/tr[1]/td/table/tbody/tr[2]/td/table').find_elements_by_tag_name('th')]

        j = 1

        for each_row_element in Party1_Table.find_elements_by_tag_name('tr'):

            all_cells_element = each_row_element.find_elements_by_tag_name('td')
            each_row_value = [unidecode(each_cell_ele.text).strip() for each_cell_ele in all_cells_element]

            if [each.strip() for each in each_row_value ] == ['']*len(PARTY1_header):
                continue
            else:   
                if len(PARTY1_header) == len(each_row_value):
                    num_member = "Member"+str(j)
                    acris_dict['Party1'][num_member] = collections.OrderedDict()
                    for i in range(len(PARTY1_header)):             
                        acris_dict['Party1'][num_member][PARTY1_header[i]] = each_row_value[i]
                j+=1

        #---------Party2--------------   
        #encode by table and by row

        Path_Party2 = '(//*[@id="ABPOSITION"]/table/tbody)[position()=2]'
        Party2_Table = driver.find_element_by_xpath(Path_Party2)
        acris_dict['Party2'] = collections.OrderedDict()


        PARTY2_header = [unidecode(header.text).strip() for header in driver.find_element_by_xpath('/html/body/table[4]/tbody/tr/td/table[3]/tbody/tr[2]/td/table/tbody/tr[2]/td/table').find_elements_by_tag_name('th')]

        j = 1
        #print PARTY2_header

        for each_row_element in Party2_Table.find_elements_by_tag_name('tr'):

            all_cells_element = each_row_element.find_elements_by_tag_name('td')
            each_row_value = [unidecode(each_cell_ele.text) for each_cell_ele in all_cells_element]

            #if the row has all null values, then contine, else add to dict
            if [each.strip() for each in each_row_value ] == ['']*len(PARTY2_header):
                continue
            else:   
                if len(PARTY2_header) == len(each_row_value):
                    num_member = "Member"+str(j)
                    acris_dict['Party2'][num_member] = collections.OrderedDict()

                    #print PARTY2_header
                    for i in range(len(PARTY2_header)): 

                        acris_dict['Party2'][num_member][PARTY2_header[i]] = each_row_value[i]
                        #print ( acris_dict['Party2'][num_member][PARTY2_header[i]], each_row_value[i])

                j+=1

        #---------PARCELS--------------              
        #encode by table and by row
        Path_PARCELS = '(//*[@id="ABPOSITION"]/table/tbody)[position()=4]'
        PARCELS_Table = driver.find_element_by_xpath(Path_PARCELS)

        PARCELS_header = [unidecode(header.text).strip() for header in driver.find_element_by_xpath('/html/body/table[4]/tbody/tr/td/table[4]/tbody/tr/td/table[1]/tbody/tr[2]/td/table').find_elements_by_tag_name('th')]
        acris_dict['PARCELS'] = collections.OrderedDict()

        for each_row_element in PARCELS_Table.find_elements_by_tag_name('tr'):
            all_cells_element = each_row_element.find_elements_by_tag_name('td')
            each_row_value = [unidecode(each_cell_ele.text) for each_cell_ele in all_cells_element]
            if [each.strip() for each in each_row_value ] == ['']*len(PARCELS_header):
                continue
            else:
                if len(PARCELS_header) == len(each_row_value):
                    for i in range(len(PARCELS_header)):
                        acris_dict['PARCELS'][PARCELS_header[i]] = each_row_value[i]

        #------------Write to CSV-----------                
        document_id = acris_dict['Doc_Detail']['DOCUMENT ID']
        CRFN = acris_dict['Doc_Detail']['CRFN']
        doc_type = acris_dict['Doc_Detail']['DOC. TYPE']
        acris_street_number = acris_dict['PARCELS']['PROPERTY ADDRESS'].split(" ")[0]
        acris_street_name = " ".join(acris_dict['PARCELS']['PROPERTY ADDRESS'].split(" ")[1:])

        acris_addr_unit = acris_dict['PARCELS']['UNIT']
        document_amt = acris_dict['Doc_Detail']['DOC. AMOUNT'][1:] if acris_dict['Doc_Detail']['DOC. AMOUNT'].startswith("$") else acris_dict['Doc_Detail']['DOC. AMOUNT']

        recorded_datetime = acris_dict['Doc_Detail']['ECORDED / FILED']
        document_date = acris_dict['Doc_Detail']['DOC. DATE']
        borough = acris_dict['PARCELS']['BOROUGH']

        block = acris_dict['PARCELS']['BLOCK']
        lot = acris_dict['PARCELS']['LOT']
        easement = acris_dict['PARCELS']['EASEMENT']
        partial_lot = acris_dict['PARCELS']['PARTIAL']
        subterranean_rights = acris_dict['PARCELS']['SUBTERRANEAN RIGHTS']
        air_rights = acris_dict['PARCELS']['AIR RIGHTS']
        property_type = acris_dict['PARCELS']['PROPERTY TYPE']
        reel_year = str(0)
        reel_pg = acris_dict['Doc_Detail']['REEL-PAGE']
        reel_nbr = str(0)

        party_json = json.dumps(acris_dict)

        party1_type = "GRANTOR/SELLER"
        party2_type = 'GRANTEE/BUYER'
        party3_type = ''

        party1 = ";".join(acris_dict['Party1'][each]['NAME'] for each in acris_dict['Party1'])
        party2 = ";".join(acris_dict['Party2'][each]['NAME'] for each in acris_dict['Party2'])
        party3 = ''

        #print (party1,party2,party3)            



        print (document_id,deed_doc_id , document_id == deed_doc_id)          
        final_data = [str(document_id), str(CRFN),doc_type,str(acris_street_number),str(acris_street_name),acris_addr_unit,str(document_amt),
                      recorded_datetime,document_date,borough,block,lot,easement,partial_lot,subterranean_rights,air_rights,
                      property_type,reel_year,reel_pg,reel_nbr,party_json,party1_type,party2_type,party3_type,
                      party1,party2,party3]



        filewriter.writerow(final_data)  
        print "--"
    
    print "The Loop is Completed"





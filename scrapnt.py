'''
title: scrapping nitt detail
author: Christian Julca
date modified: 23/06/2022
version: 1.0
virtualenv path: /home/cjulcas/project/hd_scrapdowloadpdf/scrappingweb/bin/python3.exe
'''

import pandas as pd
import numpy as np
import time
from datetime import datetime as dt
import os
import warnings
from io import StringIO

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.common.by import By

pd.set_option('display.max_columns', None)
warnings.filterwarnings("ignore")



####
# 01 funciones de limpieza y scrapping casacion por casacion
####
def scrapnit(n):
    ''''
    n: int nit code for provider


    scrap provider features from nit code
    '''
    variables_to_scrap        = pd.read_csv('/home/cjulcas/project/hd_desafiogt/scrapdesafiogt/resources/vars2scrap - bd.csv')
    variables_to_scrap_input  = variables_to_scrap[variables_to_scrap['type']=="input"] 
    variables_to_scrap_other  = variables_to_scrap[variables_to_scrap['type']=="other"]
    var_input = variables_to_scrap_input['var'].tolist()
    path_input = variables_to_scrap_input['xpath'].tolist()
    var_other = variables_to_scrap_other['var'].tolist()
    path_other = variables_to_scrap_other['xpath'].tolist()

    #create empty list
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    wd = webdriver.Chrome('chromedriver', options=chrome_options)
    #enter nit code
    lin = "https://sistema.rgae.gob.gt/consulta-proveedores/proveedor/"+str(n)
    #print(lin)
    wd.get(lin)
    time.sleep(4)
    date = dt.now().isoformat()
    #click on detalle expediente
    try:
        try:
            try: 
                for i,j in zip(var_input,path_input):
                    #fill data into list
                    globals()[str(i)] = wd.find_element(By.XPATH,j).get_attribute('value')
                for i,j in zip(var_other,path_other):
                    #fill data into list
                    globals()[str(i)] = wd.find_element(By.XPATH,j).text
                estadoscrap = "ok"
                error = ""
                print(n, "oki")
            except WebDriverException:
                for i,j in zip(var_input,path_input):
                    #fill data into list
                    globals()[str(i)] = ""
                for i,j in zip(var_other,path_other):
                    #fill data into list
                    globals()[str(i)] = ""

                estadoscrap = "fail"
                error = "WebDriverException"
                print(n, "fail")   
        except TimeoutException:
            for i,j in zip(var_input,path_input):
                #fill data into list
                globals()[str(i)] = ""
            for i,j in zip(var_other,path_other):
                #fill data into list
                globals()[str(i)] = ""

            estadoscrap = "fail"
            error = "TimeoutException"
            print(n, "fail")            
    except NoSuchElementException as err:
        for i,j in zip(var_input,path_input):
            #fill data into list
            globals()[str(i)] = ""
        for i,j in zip(var_other,path_other):
            #fill data into list
            globals()[str(i)] = ""

        estadoscrap = "fail"
        error = "NoSuchElementException"
        print(n, "fail")
    #datos
    data = {'NIT': NIT,
        'razon': razon,
        'estadoactual': estadoactual,
        'fechainscribe': fechainscribe,
        'fechapre': fechapre,
        'tipocalifica': tipocalifica,
        'vigenciaultimapre': vigenciaultimapre,
        'nitrepre': nitrepre,
        'paisrepre': paisrepre,
        'pasaporterepre': pasaporterepre,
        'nombrerepre': nombrerepre,
        'nombrecomer': nombrecomer,
        'direccioncomer': direccioncomer,
        'estadoscrap': estadoscrap,
        'link': lin,
        'datescrap': date,
        'n' : n,
        'espe': espe,
        'err': error}
    #close browser
    wd.quit()
    #to dataframe
    tmp = pd.DataFrame([data])
    return tmp

####
# 02 Ejecucion test function
####

df = pd.read_excel('input/proveedores.xlsx')
df.shape
#select unique NIT codes
nits = df['NIT'].unique()

#testing subset
#nits = nits[0:10]

#scrapping
nn = pd.DataFrame()
g  = 1

for i in nits:
    print(round((g/len(nits))*100,2),"%  ", i)
    w  = scrapnit(i)
    nn = pd.concat([nn, w], ignore_index=True)
    g  = g + 1

#filter especialidades and code with ok scrap
ww = nn[nn['estadoscrap']=="ok"][['n', 'espe']]

#expand data to each row fro especialidad

ff = pd.DataFrame()
for n, t in zip(ww['n'],ww['espe']):
    print(n)
    if t!="":
        tmp = pd.read_csv(StringIO(t), sep='/n', header=None)
    else:
        tmp = pd.DataFrame()
    tmp['n'] = n
    ff = pd.concat([ff,tmp])
ff. columns = ['espe', 'n']
ff['espe code'] = ff['espe'].str.slice(0,4) 
ff['espe des']  = ff['espe'].str.slice(5,500)
ff = ff[['espe code', 'espe des', 'n']]

## export results
nn = nn.loc[:, nn.columns!='espe']

nn.to_csv('output/scrapnit.csv', index=False)

ff.to_csv('output/scrapnit_espe.csv', index=False)



#-*- coding:utf-8 -*-
import requests
import  lxml
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
import json
import pymongo

PRODUCT = "meifeng"
SUFF = "0712"

client = pymongo.MongoClient('localhost',27017)
car = client[PRODUCT]
car_list = car['car_list_{suff}'.format(suff=SUFF)]

BRANDS = json.load(open('{product}_brands_{suff}.json'.format(product=PRODUCT,suff=SUFF),'r'))

if __name__ == "__main__":
    temp_save = PRODUCT+"_text_"+SUFF
    if os.path.exists(temp_save) == False:
        os.mkdir(temp_save)
    for brand in BRANDS:
        autoBrandId = brand['k']
        print(autoBrandId)
        url = 'https://{product}.51cjml.com/resource/AutoMinByStep?setp=1&autoBrandId={bid}&version=v1'.format(product=PRODUCT,bid=autoBrandId)
        json_text = json.loads(requests.get(url).text)
        s1 = json_text['i']
        json.dump(s1,open(temp_save+'/'+str(autoBrandId)+'.json','w'))
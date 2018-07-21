#-*- coding:utf-8 -*-
import requests
import  lxml
import re
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



def getP(id,p,s):
    json_path = p + "_text_" + s + "/" + str(id) + ".json"
    json_text = json.load(open(json_path,'r'))[0]

    #车系 Y 英菲尼迪
    chexi = json_text['n']
    for item in json_text['i']:
        #车型1  东风英菲尼迪
        chexing1 = item['n']
        chexing1List = item['i']
        for i in chexing1List:
            #系 其他
            xi = i['n']
            #系2
            li = i['i']
            for j in li:
                che = j['n']  #QX50
                paiList = j['i']
                for k in paiList:
                    pai = k['n']
                    paiV = k['k']
                    for l in getData(paiV,p,s):
                        data = {}
                        data['车系'] = chexi
                        data['车型1'] = chexing1
                        data['车型2'] = xi
                        data['车型3'] = che
                        data['排量'] = pai
                        data['前后'] = l['前后']
                        data['型号'] = l['型号']
                        data['时间'] = l['时间']
                        data['属性'] = l['属性']
                        print(chexi," ",chexing1," ",xi," ",che," ",pai," ",paiV," ",data['前后'])
                        car_list.insert_one(data)

def getData(k,p,s):
    url = 'https://{p}.51cjml.com/Search/Result?ps=10&pi=1&f=&fb=&ver=v2&ak={k}&akt=0&cs=&pcs=&sts=0&cg=&qt=0&a=&p=&o=&c=&pc=&b=cookie&y=0&ap=&v=&fm='.format(p=p,k=k)
    soup = BeautifulSoup(requests.get(url).text,'lxml')
    returnList = []
    if soup.select('#hidTotalCount')[0].text == '0':
        data = {}
        data['前后'] = ''
        data['型号'] = ''
        data['时间'] = ''
        data['属性'] = ''
        returnList.append(data)
    else:
        tableBox = soup.select('.singleTableBox')
        for item in tableBox:
            name = item.select('.singleTableName')
            frontback = ''
            if name != []:
                frontback = name[0].text.strip()

            for i in range(20):
                class_str = '.tableBG'+str(i+1)
                tableBG = item.select(class_str)
                if tableBG == []:
                    break
                number = tableBG[0].select('.productName2')
                time = tableBG[0].select('.tdRight > span')
                parameter = tableBG[0].select('.be-parameterBox > span')
                if number != []:
                    data = {}
                    data['前后'] = frontback
                    data['型号'] = number[0].text.strip()
                    time_str = ''
                    par_str = ''
                    for t in time:
                        time_str = time_str + t.text.strip() + '\n'
                    for p in parameter:
                        par_str = par_str + p.text.strip() + '\n'
                    data['时间'] = time_str
                    data['属性'] = par_str
                    returnList.append(data)
                else:
                    data = {}
                    data['前后'] = frontback
                    data['型号'] = '当前无适配产品'
                    time_str = ''
                    for t in time:
                        time_str = time_str + t.text.strip() + '\n'
                    data['时间'] = time_str
                    data['属性'] = ''
                    returnList.append(data)
    return returnList


if __name__ == "__main__":
    if_save = False
    if if_save:
        save_path = PRODUCT + "_" + SUFF + ".xlsx"
        data = []
        for item in car_list.find({}, {'_id': 0}):
            data.append(item)
        data = pd.DataFrame(data)
        data.to_excel(save_path, index=False)
    else:
        count = 0
        for brand in BRANDS[count:]:
            print(count)
            autoBrandId = brand['k']
            getP(autoBrandId,PRODUCT,SUFF)
            count = count + 1



import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re
import json
import time
from datetime import datetime

def timestamp_to_str(timestamp):
    time_local = time.localtime(timestamp)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt[:-3]


class Xinjiangwhyspider(scrapy.Spider):
    name='xinjiangwhy'
    start_urls = ['http://www.btggwh.com/xjwly/']
    event_count=1
    event_page_end=2

    def start_requests(self):
        for i in range(self.event_count,self.event_page_end+1):
            url='http://www.btggwh.com/service/action/web/actionAndProjectListAll'
            myFormData = {'pageSize': '8',
                          'pageNum': str(i),
                          'type': '',
                          'libcode':'xjwly',
                          'timeFormat': 'YY-MM-dd' }
            yield scrapy.FormRequest(url, method='POST',formdata = myFormData, callback=self.event_parse,dont_filter = True)

    def event_parse(self,response):
        data=json.loads(response.body)
        #print(data)
        record_list=data['data']['list']
        for record in record_list:
            print(record)
            item=CultureEventItem()
            item['pav_name']='新疆生产建设兵团文化云'
            item['url']='http://www.btggwh.com/xjwly/view/whactivity/activity-info1.html?id='+str(record['id'])
            item['place']=record['addrDetail']
            item['activity_name']=record['name']
            item['activity_time']=datetime.fromtimestamp(record['startTime'] / 1000.0).strftime('%Y-%m-%d')+' '+datetime.fromtimestamp(record['endTime'] / 1000.0).strftime('%Y-%m-%d')
            #record['startTimeStr']+"到"+record['endTimeStr']
            url='http://www.btggwh.com/service/action/web/detailsActivity'
            myFormData={
                'id':str(record['id'])
            }
            yield scrapy.FormRequest(url,method='POST',formdata = myFormData, meta={'item':item},callback=self.event_text_parse,dont_filter = True)




    def event_text_parse(self,response):
        data=json.loads(response.body)
        #print(data['data']['actionSpecial'])
        item=response.meta['item']
        soup=BeautifulSoup(data['data']['actionSpecial']['specialDesc'],'html.parser')
        item['remark']=soup.text.replace('\n','').replace('\xa0','').replace('\u3000','')
        try:
            item['place']=data['data']['commonAddress']['addrName']+data['data']['commonAddress']['addrDetail']
        except:
            pass
        return item
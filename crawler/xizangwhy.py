import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re
import json
import time

def timestamp_to_str(timestamp):
    time_local = time.localtime(timestamp)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt[:-3]


class Xizangwhyspider(scrapy.Spider):
    name='xizangwhy'
    start_urls = ['http://xzzzqqyg.com/']
    event_count=1
    event_page_end=1

    def start_requests(self):
        for i in range(self.event_count,self.event_page_end+1):
            url='http://xzzzqqyg.com/activity/getFActivitySearch.show?activityFlag=0&activityTime=0&pageNum='+str(i)+'&pageSize=10&sort=0&title='
            yield scrapy.Request(url, callback=self.event_parse)

    def event_parse(self,response):
        data=json.loads(response.body)
        record_list=data['data']['list']
        for record in record_list:
            item=CultureEventItem()
            item['pav_name']='西藏群众艺术馆'
            item['organizer']=record['company']
            item['url']=record['linkAddress']
            item['place']=record['address']
            item['activity_name']=record['title']
            item['activity_time']=timestamp_to_str(record['startTime']/1000)+"到"+timestamp_to_str(record['endTime']/1000)
            url='http://xzzzqqyg.com/activity/getFActivityDetailForJoin.show?id='+str(record['contentId'])
            yield scrapy.Request(url,meta={'item':item},callback=self.event_text_parse)




    def event_text_parse(self,response):
        data=json.loads(response.body)
        item=response.meta['item']
        soup=BeautifulSoup(data['data']['list'][0]['content'],'html.parser')
        item['remark']=soup.text.replace('\n','').replace('\xa0','').replace('\u3000','')
        return item
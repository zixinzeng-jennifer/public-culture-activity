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


class Wuhanqygspider(scrapy.Spider):
    name='wuhanqyg'
    start_urls = ['https://whsqyg_stadium.hbqyg.cn/Activity/Index/index']
    event_count=1
    event_page_end=2

    def start_requests(self):
        for i in range(self.event_count,self.event_page_end+1):
            url='https://whsqyg_stadium.hbqyg.cn/Activity/Index/list?city_code=170100&keyword=&page_number='+str(i)+'&page_size=12&activity_category_type=0&district_code=0&custom_status=2'
            yield scrapy.Request(url, callback=self.event_parse)

    def event_parse(self,response):
        data=json.loads(response.body)
        record_list=data['DATA']['activity_list']['list']
        for record in record_list:
            item=CultureEventItem()
            item['pav_name']='武汉市群众艺术馆'
            item['organizer']=record['sponsor']
            item['url']='https://whsqyg_stadium.hbqyg.cn/'+record['detail_skip_url']
            item['place']=record['address']['format']+record['address']['detail']
            item['contact']=record['principal_phone']
            item['activity_name']=record['title']
            item['activity_type']=record['type_format']
            item['activity_time']=timestamp_to_str(record['start_time'])+"到"+timestamp_to_str(record['end_time'])
            yield scrapy.Request(item['url'],meta={'item':item},callback=self.event_text_parse)




    def event_text_parse(self,response):
        data=json.loads(response.body)
        item=response.meta['item']
        soup=BeautifulSoup(data,'html.parser')
        info=soup.find('rich-text')
        item['remark']=info.text.replace('\n','').replace('\xa0','').replace('\u3000','')
        return item
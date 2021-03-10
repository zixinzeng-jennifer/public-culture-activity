# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class YunNanSpider(scrapy.Spider):
    name = 'yunnanwhg'
    allowed_domains = ['ynswhg.cn']

    # 爬去机构动态所需的参数
    news_url = 'http://www.ynswhg.cn/Category_109/Index.aspx'
    news_base_url = 'http://www.ynswhg.cn/Category_109/Index_'
    news_count = 1
    news_page_end = 37

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.ynswhg.cn/Category_197/Index.aspx'

    # 爬去机构活动所需的参数
    event_url = 'http://www.ynswhg.cn/Category_111/Index.aspx'
    event_base_url = 'http://www.ynswhg.cn/Category_111/Index_'
    event_count = 1
    event_page_end = 4

    def start_requests(self):
        # 请求机构介绍信息
        yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def news_parse(self, response):
        origin_url = 'http://www.ynswhg.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', {"class": 'c_article_list'}).find('dd').find('ul')
        print(article_lists)
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '云南省文化馆'
                item['title'] = article.a.string.strip()
                item['url'] = origin_url + article.a['href']
                #print(str(article.text))
                item['time'] = re.findall(r'(\d{4}-\d{2}-\d{2})',str(article.text))[0]
                #print(item['time'])
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '.aspx', callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        content = soup.find("div", {"class": "c_main_box"})
        item['content'] = ""#str(content.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item


    def event_parse(self, response):
        origin_url = 'http://www.ynswhg.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('div', {"class": 'c_article_list'}).find("dd").find("ul")
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '云南省文化馆'
                item['activity_name'] = event.a.string.strip()
                item['activity_type'] = "公益活动"
                item['activity_time'] = re.findall(r'(\d{4}-\d{2}-\d{2})',str(event.text))[0]
                item['url'] = origin_url + event.a['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url+str(self.event_count) + '.aspx',callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        item['remark'] = ""
        return item

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {"id": 'center'}).text).strip()
        item['pav_name'] = '云南文化馆'
        item['pav_introduction'] = intro .replace('\xa0','').replace('\u3000\u3000', '')
        item['region'] = '云南'
        item['area_number'] = '14378.69平方米'
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

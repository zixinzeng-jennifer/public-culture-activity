# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class ChangchunlibSpider(scrapy.Spider):
    name = 'changchunlib'
    allowed_domains = ['ccelib.cn']
    start_urls = ['http://ccelib.cn/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.ccelib.cn/PCWeb/default/guanyu'

    # 爬去机构动态所需的参数
    news_url = 'http://www.ccelib.cn/PCWeb/default/newxw?pageIndex=1'
    news_base_url = 'http://www.ccelib.cn/PCWeb/default/newxw?pageIndex='
    news_count = 1
    news_page_end = 14

    # 爬去机构活动所需的参数
    event_url = 'http://www.ccelib.cn/PCNews/default/newhd?pageIndex=1'
    event_base_url = 'http://www.ccelib.cn/PCNews/default/newhd?pageIndex='
    event_count = 1
    event_page_end = 43

    def start_requests(self):

        # 请求机构介绍信息
        yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {'id': '10'}).text).strip()
        item['pav_name'] = '长春市图书馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
        item['region'] = '长春'
        item['area_number'] = '3.5万平方米'
        item['collection_number'] = '360万余册'
        item['branch_number'] = ''
        item['librarian_number'] = '178'
        item['client_number'] = '130万人'
        item['activity_number'] = '400~500'
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.ccelib.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', {"class": "nei1"})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '长春市图书馆'
                item['url'] = origin_url + article.find('a')['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count), callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        item['title'] = soup.find('div', {'class': 'nei1_title'}).text
        news_time = soup.find('div', {
            'style': 'text-align:center; margin-left:auto; margin-right:auto;position:relative; top:10px;'}).text
        item['time'] = re.findall(r'\d{4}-\d{1,2}-\d{1,2}', news_time)[0]
        contents = str(soup.find("div", {"class": "nei_z"}).text).strip().replace('\u3000', '').replace('\r',
                                                                                                        '').replace(
            '\n', '').replace(
            '\xa0', '').replace('\t', '')
        item['content'] = contents
        return item

    def event_parse(self, response):
        origin_url = 'http://www.ccelib.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('ul', {'class': 'floatG'})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '长春市图书馆'
                item['url'] = origin_url + event.find('a')['href']
                info = soup.find('span', {'class': 'info'}).text
                item['activity_time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', info)[0]
                item['place'] = re.findall(r'活动地点：(.+)', info)[0]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url + str(self.event_count), callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            item['activity_name'] = soup.find('div', {'class': 'du_left_title1'}).text
        except:
            pass
        content = soup.find('div', {"class", "du_left_main"}).text
        try:
            item['remark'] = str(content).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '')
        except:
            pass
        try:
            item['activity_introduction'] = re.findall(r'【活动内容】(.+?)\xa0', content)[0]
        except:
            pass
        try:
            item['age_limit'] = re.findall(r'【活动对象】(.+?)\xa0', content)[0]
        except:
            pass
        try:
            item['presenter'] = re.findall(r'主讲嘉宾：(.+?)\xa0', content)[0]
        except:
            pass
        try:
            item['presenter'] = re.findall(r'电影讲述人：(.+?)\xa0', content)[0]
        except:
            pass
        try:
            item['presenter_introduction'] = re.findall(r'主讲嘉宾简介：(.+?)。\xa0', content)[0]
        except:
            pass
        try:
            item['presenter_introduction'] = re.findall(r'嘉宾介绍：(.+?)。\xa0', content)[0]
        except:
            pass
        try:
            item['activity_introduction'] = re.findall(r'讲座内容概要：(.+?)。\xa0', content)[0]
        except:
            pass
        try:
            item['organizer'] = re.findall(r'主办单位：(.+?)\xa0', content)[0]
        except:
            pass
        try:
            item['contact'] = re.findall(r'【联系电话】 (.+?)\xa0', content)[0]
        except:
            pass
        return item

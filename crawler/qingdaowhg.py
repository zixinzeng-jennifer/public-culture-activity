# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class QingdaowhgSpider(scrapy.Spider):
    name = 'qingdaowhg'
    allowed_domains = ['qdqzysg.com']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.qdqzysg.com/about.aspx'

    # 爬去机构动态所需的参数
    news_url = 'http://www.qdqzysg.com/news.aspx?page=1&id=42'
    news_base_url = 'http://www.qdqzysg.com/news.aspx?page='
    news_count = 1
    news_page_end = 45

    def start_requests(self):
        # 请求机构介绍信息
        yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        # yield scrapy.Request(self.event_url, callback=self.event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('li', {'class': 'jianjie7'}).text).strip()
        item['pav_name'] = '青岛市文化馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '')
        item['region'] = '青岛'
        item['area_number'] = '9600平方米'
        item['collection_number'] = ''
        item['branch_number'] = '20'
        item['librarian_number'] = '98'
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.qdqzysg.com/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        target_htmls = soup.find_all('div', {'class': 'tw3'})
        for target in target_htmls:
            item = CultureNewsItem()
            try:
                item['pav_name'] = '青岛市文化馆'
                item['title'] = target.find('li', {'class': 'tw4'}).a.attrs['title']
                item['url'] = origin_url + target.find('li', {'class': 'tw4'}).a.attrs['href']
                item['time'] = str(target.find('li', {'class': 'tw5'}).find('span', {'class': 'time'}).text).strip()
                yield scrapy.Request(item['url'], meta={'item':item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '&id=42',callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        contents = soup.find('div',{'class':'zhengwen'}).find_all('p')
        text = []
        for content in contents:
            text.append(str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('\t',''))
        fulltext = ''.join(text)
        item['content'] = fulltext
        return item



# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class TianjinwygSpider(scrapy.Spider):
    name = 'tianjinqyg'
    allowed_domains = ['tjsqyg.com']
    start_urls = ['http://tjsqyg.com/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.tjsqyg.com/home/index'

    # 爬去机构动态所需的参数
    news_url = 'http://www.tjsqyg.com/info/list?page=1'
    news_base_url = 'http://www.tjsqyg.com/info/list?page='
    news_count = 1
    news_page_end = 20

    def start_requests(self):
        # 请求机构介绍信息
        yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        yield scrapy.Request(self.news_url, callback=self.news_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        # data = response.body
        # soup = BeautifulSoup(data, 'html.parser')
        item['pav_name'] = '天津市群众艺术馆'
        item['pav_introduction'] = ''
        item['region'] = '天津'
        item['area_number'] = ''
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.tjsqyg.com'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('ul', {"id": "ul_info"})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '天津市群众艺术馆'
                item['title'] = article.h3.string
                item['url'] = origin_url + article.a.attrs['href']
                item['time'] = article.find('span', {'class': 'span_date'}).text
                text = str(article.text).strip().replace('\n', '').replace('\r', '').replace('\xa0', '') \
                    .replace(' ', '')
                try:
                    item['content'] = str(re.findall(r'发布时间：\d{4}-\d{2}-\d{2}(.+)查看详情', text)[0])
                except:
                    pass
                yield item
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count), callback=self.news_parse)
        else:
            return None

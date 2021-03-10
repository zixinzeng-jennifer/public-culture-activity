# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class XiamenwhgSpider(scrapy.Spider):
    name = 'xiamenwhg'
    allowed_domains = ['xmwhg.com.cn']
    start_urls = ['http://xmwhg.com.cn/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.xmwhg.com.cn/bggk/bggk/'

    # 爬去机构动态所需的参数
    news_url = 'http://www.xmwhg.com.cn/xwzx/hdxx/index.htm?page=1'
    news_base_url = 'http://www.xmwhg.com.cn/xwzx/hdxx/index_'
    news_count = 1
    news_page_end = 39

    # 爬去机构活动所需的参数
    event_url = 'http://www.xmwhg.com.cn/jqzl/index.htm?page=1'
    event_base_url = 'http://www.xmwhg.com.cn/jqzl/index_'
    event_count = 1
    event_page_end = 71

    def start_requests(self):

        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {'class': 'TRS_Editor'}).text).strip()
        item['pav_name'] = '厦门市文化馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
        item['region'] = '厦门'
        item['area_number'] = '2.8万平方米'
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = '57'
        item['client_number'] = ''
        item['activity_number'] = '180'
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.xmwhg.com.cn/xwzx/hdxx/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        # article_lists = soup.find('div', {"class": "tit_r_c  pad_l35 pad_r30"})
        for article in soup.find_all("li", {'class': ''}):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '厦门市文化馆'
                item['title'] = article.a.string
                item['url'] = origin_url + article.a.attrs['href'][2:]
                item['time'] = article.span.string[1:-1]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count - 1) + '.htm?page=' + str(self.news_count),
                                 callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        contents = soup.find("div", {"class": "TRS_Editor"}).find_all('span')
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['content'] = fulltext
        return item

    def event_parse(self, response):
        origin_url = 'http://www.xmwhg.com.cn/jqzl/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        for event in soup.find_all('span', {'class': 'tred4 t18'}):
            item = CultureEventItem()
            try:
                item['pav_name'] = '厦门市文化馆'
                item['activity_type'] = '展览'
                item['activity_name'] = event.a.string
                item['url'] = origin_url + event.a.attrs['href'][2:]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url + str(self.event_count - 1) + '.htm?page=' + str(self.event_count),
                                 callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"id":"fontzoom"}).text
        try:
            item['source'] = str(soup.find('div',{'class':' f_c h24'}).text).strip().split('：')[1]
        except:
            item['source'] = ''

        try:
            item['place'] = re.findall(r'展览场地：(.+)',content)[0]
        except:
            item['place'] = ''

        try:
            item['activity_time'] = str(re.findall(r'展览时间：(.+)',content)[0])[:10]
        except:
            item['activity_time'] = ''

        try:
            item['organizer'] = re.findall(r'主办单位：(.+)',content)[0]
        except:
            item['organizer'] = ''

        try:
            item['activity_introduction'] = re.findall(r'展览介绍：(.+)',content)[0]
        except:
            item['activity_introduction'] = ''

        return item

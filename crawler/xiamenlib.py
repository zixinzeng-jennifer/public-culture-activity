# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class XiamenlibSpider(scrapy.Spider):
    name = 'xiamenlib'
    allowed_domains = ['xmlib.net']
    start_urls = ['http://xmlib.net/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.xmlib.net/dzzn/xtjj/'

    # 爬去机构动态所需的参数
    news_url = 'http://www.xmlib.net/xtdt/xtjx/index.htm'
    news_base_url = 'http://www.xmlib.net/xtdt/xtjx/index_'
    news_count = 0
    news_page_end = 134

    # 爬去机构活讲座需的参数
    jz_event_url = 'http://www.xmlib.net/dzhd/zsjz/index.htm'
    jz_event_base_url = 'http://www.xmlib.net/dzhd/zsjz/index_'
    jz_event_count = 0
    jz_event_page_end = 24

    # 爬去机构活展览需的参数
    zl_event_url = 'http://www.xmlib.net/dzhd/whzl/zlyg/index.htm'
    zl_event_base_url = 'http://www.xmlib.net/dzhd/whzl/zlyg/index_'
    zl_event_count = 0
    zl_event_page_end = 26

    # 爬去机构活培训需的参数
    px_event_url = 'http://www.xmlib.net/dzhd/gypx/index.htm'
    px_event_base_url = 'http://www.xmlib.net/dzhd/gypx/index_'
    px_event_count = 0
    px_event_page_end = 5

    def start_requests(self):

        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)
        yield scrapy.Request(self.zl_event_url, callback=self.zl_event_parse)
        yield scrapy.Request(self.px_event_url, callback=self.px_event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {'id': 'TRS_AUTOADD_1289182097531'}).text).strip()
        item['pav_name'] = '厦门市图书馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
        item['region'] = '厦门'
        item['area_number'] = '25732平方米'
        item['collection_number'] = '415.47万册'
        item['branch_number'] = '22'
        item['librarian_number'] = ''
        item['client_number'] = '439万人次'
        item['activity_number'] = '1110'
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.xmlib.net/xtdt/xtjx/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', {"class": "list"})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '厦门市图书馆'
                item['title'] = article.a.string
                item['url'] = origin_url + article.a.attrs['href'][2:]
                item['time'] = article.span.string[1:-1]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '.htm', callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        try:
            soup = BeautifulSoup(data, "html.parser")
            content = soup.find("div", {"class": "TRS_Editor"}).find('div', {'class': ''})
            item['content'] = str(content.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        except:
            item['content'] = ''
        return item

    def jz_event_parse(self, response):
        origin_url = 'http://www.xmlib.net/dzhd/zsjz/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('div', {'class': 'list'})
        for event in event_lists.find_all('li'):
            try:
                url = origin_url + event.a.attrs['href'][2:]
                ac_time = event.span.string[1:-1]
                xinxi = {'url': url, 'ac_time': ac_time}
                yield scrapy.Request(url, meta={'xinxi': xinxi}, callback=self.jz_event_text_parse)
            except Exception as err:
                print(err)

        if self.jz_event_count < self.jz_event_page_end:
            self.jz_event_count = self.jz_event_count + 1
            yield scrapy.Request(self.jz_event_base_url + str(self.jz_event_count) + '.htm',
                                 callback=self.jz_event_parse)
        else:
            return None

    def jz_event_text_parse(self, response):
        xinxi = response.meta['xinxi']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        item=CultureEventItem()
        try:
            p_tags = soup.find_all('p')
            for i in range(len(p_tags)):
                try:
                    head = str(p_tags[i].text).strip().split('：')[0]
                    body = (':'.join(str(p_tags[i].text).strip().split('：')[1:])).strip()
                    if head == '主办' or head == '主办单位' or head == '荣誉主办':
                        item['organizer'] = body
                    elif head == '地点' or head == '展览地点' or head == '展览地址' or head == '集合地点':
                        item['place'] = body
                    elif head == '主题' or head == '主  题':
                        item['activity_name'] = body
                    elif head=='时间':
                        item['activity_time']=body
                    elif head == '创意指导' or head == '主讲' or head == '主讲人':
                        item['presenter'] = body.replace('\xa0',' ')
                    elif head == '联系电话':
                        item['contact'] = body
                    elif head == '内容简介' or head == '主要内容' or head=='讲座内容':
                        if body != '':
                            item['activity_introduction'] = body
                        else:
                            item['activity_introduction'] = str(p_tags[i + 1].text).strip()
                    if len(item['activity_name'])>0 and len(item['presenter'])>0 and len(item['activity_time'])>0:
                        print("item complete")
                        item['activity_type']='讲座'
                        yield item
                        item=CultureEventItem()
                except:
                    pass
        except:
            pass

        """
        content = soup.find('div', {'class': 'TRS_Editor'})
        tbody = content.find('tbody')
        tr_count = 0
        td_count = 0
        if tbody:
            for tr in tbody.find_all('tr'):
                if tr_count == 0:
                    tr_count = tr_count + 1
                else:
                    item = CultureEventItem()
                    item['url'] = xinxi['url']
                    item['activity_time'] = xinxi['ac_time']
                    item['activity_type'] = '讲座'
                    item['pav_name'] = '厦门市图书馆'


                    for td in tr.find_all('td'):
                        if td_count == 0:
                            td_count = td_count + 1
                        else:
                            if td_count == 1:
                                item['presenter'] = td.find('p').text
                            elif td_count == 2:
                                item['activity_name'] = td.find('p').text
                            elif td_count == 3:
                                item['activity_introduction'] = td.find('p').text
                            td_count = td_count + 1

                    yield item
                td_count = 0
        """


    def zl_event_parse(self, response):
        origin_url = 'http://www.xmlib.net/dzhd/whzl/zlyg/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('div', {'class': "list"})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['activity_name'] = event.a.attrs['title']
                item['activity_time'] = event.span.string[1:-1]
                item['url'] = origin_url + event.a.attrs['href'][2:]
                item['pav_name'] = '厦门市图书馆'
                item['activity_type'] = '展览'
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.zl_event_text_parse)
            except Exception as err:
                print(err)
        if self.zl_event_count < self.zl_event_page_end:
            self.zl_event_count = self.zl_event_count + 1
            yield scrapy.Request(self.zl_event_base_url + str(self.zl_event_count) + '.htm',
                                 callback=self.zl_event_parse)

    def zl_event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            content = soup.find('div', {'class': 'TRS_Editor'})
            p_tags = content.find_all('p')
            for p in p_tags:
                try:
                    head = str(p.text).strip().split('：')[0]
                    body = str(p.text).strip().split('：')[1]
                    if head == '主办' or head == '主办单位' or head == '荣誉主办':
                        item['organizer'] = body
                    elif head == '地点' or head == '展览地点' or head == '展览地址':
                        item['place'] = body
                    elif head == '创意指导':
                        item['presenter'] = body.replace('\xa0',' ')
                except:
                    pass
        except:
            pass
        return item

    def px_event_parse(self, response):
        origin_url = 'http://www.xmlib.net/dzhd/gypx/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('div', {'class': 'list'})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['activity_name'] = event.a.attrs['title']
                item['activity_time'] = event.span.string[1:-1]
                item['url'] = origin_url + event.a.attrs['href'][2:]
                item['activity_type'] = '培训'
                item['pav_name'] = '厦门市图书馆'
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.px_event_text_parse)
            except Exception as err:
                print(err)
            if self.px_event_count < self.px_event_page_end:
                self.px_event_count = self.px_event_count + 1
                yield scrapy.Request(self.px_event_base_url + str(self.px_event_count) + '.htm',
                                     callback=self.px_event_parse)

    def px_event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            content = soup.find('div', {'class': 'TRS_Editor'})
            p_tags = content.find_all('p')
            for i in range(len(p_tags)):
                try:
                    head = str(p_tags[i].text).strip().split('：')[0]
                    body = str(p_tags[i].text).strip().split('：')[1]
                    if head == '主办' or head == '主办单位' or head == '荣誉主办':
                        item['organizer'] = body
                    elif head == '地点' or head == '展览地点' or head == '展览地址' or head == '集合地点':
                        item['place'] = body
                    elif head == '主题' or head == '主  题':
                        item['activity_name'] = body
                    elif head == '创意指导' or head == '主讲' or head == '主讲人':
                        item['presenter'] = body
                    elif head == '联系电话':
                        item['contact'] = body

                    elif head == '内容简介' or head == '主要内容':
                        if body != '':
                            item['activity_introduction'] = body
                        else:
                            item['activity_introduction'] = str(p_tags[i + 1].text).strip()
                except:
                    pass
        except:
            pass
        return item

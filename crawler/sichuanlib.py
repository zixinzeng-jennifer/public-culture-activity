# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class SichuanSpider(scrapy.Spider):
    name = 'sichuanlib'
    allowed_domains = ['sclib.org']
    start_urls = ['http://http://www.sclib.org/']


    # 爬去机构动态所需的参数
    news_url = 'http://www.sclib.org/list.htm?c=1521488440060372'
    news_base_url = 'http://www.sclib.org/list.htm?action=sourceList&m=1521488440060363&c=1521488440060372&k=&type=1&currentPage='
    news_count = 0
    news_page_end = 5

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.sclib.org/info.htm?id=1021510800316071'

    # 爬去机构活动所需的参数
    event_url = 'http://www.sclib.org/list.htm?m=1521490257728970&c=1521490257728974'
    event_base_url = 'http://www.sclib.org/list.htm?action=sourceList&m=1521490257728970&c=1521490257728974&k=&type=1&currentPage='
    event_count = 0
    event_page_end = 13

    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        
    def news_parse(self, response):
        origin_url = 'http://www.sclib.org'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find_all('div', {'class': 'info-list'})
        for article in article_lists:
            item = CultureNewsItem()
            try:
                item['pav_name'] = '四川省图书馆'
                item['title'] = article.a.string
                item['url'] = origin_url + article.a['href']
                item['time'] = article.span.string.strip()[1:-1]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as rr:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '.html', callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        content = soup.find("div", {"id": "content"})
        item['content'] = str(content.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item


    def event_parse(self, response):
        origin_url = 'http://www.sclib.org'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find_all('div', {'class': 'info-list'})
        for event in event_lists:
            item = CultureEventItem()
            try:
                item['pav_name'] = '四川省图书馆'
                item['activity_name'] = event.a.string
                if re.findall(r'（.*?）',event.a.string)[0]:
                    item['activity_type'] = re.findall(r'（.*?）',event.a.string)[0][1:-1]
                item['activity_time'] = event.span.string.strip()[1:-1]
                item['url'] = origin_url + event.a['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url+str(self.event_count),callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "info-content"})
        full_text = str(content.text).strip().replace('\u3000', '').replace('\xa0', '')
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\u3000', '').replace('\xa0', ''))
        # print(p_content)
        ########################################################################################
        item['remark'] = full_text.replace('\n', '')
        ########################################################################################
        # 活动地点 = place
        item['place'] = ''
        for i in range(len(p_content)):
            if '活动地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '活动地点' == p_content[i] or '五、培训地点:' == p_content[i]:
                item['place'] = p_content[i + 1]
                break
            elif '讲座地点：' in p_content[i]:
                index = p_content[i].index('讲座地点：')
                item['place'] = p_content[i][index:].split('：')[1]
                break
            elif '展览地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
        try:
            if re.findall(r'在(.*?)举办', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(.*?)举办', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'在(.*?)继续开讲', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(.*?)继续开讲', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'(.*?)将举办', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'，(.*?)将举办', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'活动地点是(.*?)。', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'活动地点是(.*?)。', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'在(四川省图书馆.{6})，', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(四川省图书馆.{6})，', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'，在(.*?)，', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'，在(.*?)，', content.text)[0]
        except:
            pass
        ########################################################################################
        
        item['presenter'] = ''
        for i in range(len(p_content)):
            if '一、活动主讲人：' in p_content[i]:
                item['presenter'] = p_content[i + 1]
                break
            elif '主 讲 人：' in p_content[i]:
                item['presenter'] = p_content[i].split('：')[1]
                break
            elif '主讲人：' in p_content[i]:
                item['presenter'] = p_content[i].split('：')[1]
                break
        try:
            if re.findall(r'(...)老师', content.text)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)老师', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'(...)先生', content.text)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)先生', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'(...)姐姐', content.text)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)姐姐', content.text)[0]
        except:
            pass
        ########################################################################################
        item['organizer'] = ''
        if re.findall(r'主办单位：(\s*(.*[馆院会司部委]))\s*相关信息',str(full_text)):
            item['organizer'] = re.findall(r'主办单位：(\s*(.*[馆院会司部委]))\s*相关信息',str(full_text))[0]          # 举办

        ########################################################################################
        item['age_limit'] = ''
        try:
            if re.findall(r'不限年龄', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'不限年龄', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', content.text)[0]
        except:
            pass
        ########################################################################################
        item['presenter_introduction'] = ''
        for i in range(len(p_content)):
            if '作者简介：' == p_content[i] or '主讲人简介：' == p_content[i]:
                item['presenter_introduction'] = p_content[i + 1]
                break
            elif '讲师简介：' in p_content[i]:
                item['presenter_introduction'] = p_content[i].split("：")[1]
                break
        ########################################################################################
        item['contact'] = ''
        for i in range(len(p_content)):
            if '预约电话：' in p_content[i]:
                item['contact'] = p_content[i].split('：')[1]
                break
        try:
            if re.findall(r'\d{4}—\d{8}', content.text)[0] and item['age_limit'] == '':
                item['contact'] = re.findall(r'\d{4}—\d{8}', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'\d{8}', content.text)[0] and item['age_limit'] == '':
                item['contact'] = re.findall(r'\d{8}', content.text)[0]
        except:
            pass
        ########################################################################################
        item['participation_number'] = ''
        ########################################################################################
        item['click_number'] = ''
        click = soup.find("div",{"class":"info_basic"}).string
        item['click_number'] = re.findall(r'点击：(\d+)',click)[0]
        ########################################################################################
        item['source'] = ''
        if re.findall(r'(（.*?部(  .*?)?）)',str(full_text))[0]:
            item['source'] = re.findall(r'(（.*?部）)',str(full_text))[0][1:-1]
        ########################################################################################
        item['activity_introduction'] = ''
        ########################################################################################
        return item
    
    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {"class": 'info-content'}).text).strip()
        item['pav_name'] = '四川省图书馆'
        item['pav_introduction'] = intro.replace('\u3000\u3000', '')
        item['region'] = '四川'
        item['area_number'] = '5.2万平方米'
        item['collection_number'] = '500余万册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = '6万余'
        item['activity_number'] = ''
        yield item

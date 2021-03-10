# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class NingXiaSpider(scrapy.Spider):
    name = 'ningxialib'
    allowed_domains = ['nxlib.cn']

    # 爬去机构动态所需的参数
    news_url = 'http://www.nxlib.cn/node/447.jspx'
    news_base_url = 'http://www.nxlib.cn/node/447_'
    news_count = 1
    news_page_end = 19

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.nxlib.cn/node/412.jspx'

    # 爬去机构活动所需的参数
    event_url = 'http://www.nxlib.cn/node/394.jspx'
    event_base_url = 'http://www.nxlib.cn/node/394_'
    event_count = 1
    event_page_end = 2

    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def news_parse(self, response):
        origin_url = 'http://www.nxlib.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        #print(soup)
        article_lists = soup.find('div', {"class": 'nyNewsList3'})
        #print(article_lists)
        for article in article_lists.find_all("dl"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '宁夏图书馆'
                item['title'] = article.a.dt.string
                item['url'] = origin_url + article.a['href']
                #print(item['url'])
                item['time'] = article.a.dd.time.string
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '.jspx', callback=self.news_parse)
            #print(self.news_base_url + str(self.news_count) + '.jspx')
        else:
            #print('没有运行')
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        content = soup.find("div", {"class": "art"})
        p_tags = content.find_all('p')
        full_text = ''
        for p in p_tags:
            full_text = full_text + str(p.text)
        item['content'] = full_text.replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item


    def event_parse(self, response):
        origin_url = 'http://www.nxlib.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('ul', {'class': 'nyNewsList'})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '宁夏图书馆'
                item['activity_name'] = event.a.span.string
                item['activity_type'] = '阅读推广'
                item['activity_time'] = event.a.time.string
                item['url'] = origin_url + event.a['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url+str(self.event_count) + '.jspx',callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "art"})
        p_tags = content.find_all('p')
        full_text = ''
        for p in p_tags:
            full_text = full_text + str(p.text)
        item['remark'] = full_text.replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\xa0', '').replace('\u3000', ''))
        click = content.ul.find_all('li')
        print(click)
        item['click_number'] = re.findall(r'<a id="info_views">(\d+)</a>次',str(click[-1]))[0]
        print(item['click_number'])
        # print(p_content)
        ########################################################################################
        item['remark'] = full_text .replace('\xa0','').replace('\n', '')
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
            if re.findall(r'在(济南市图书馆.{6})，', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(济南市图书馆.{6})，', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'，在(.*?)，', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'，在(.*?)，', content.text)[0]
        except:
            pass
        ########################################################################################
        item['activity_type'] = ''
        try:
            if '展览' in full_text:
                item['activity_type'] = '展览'
            elif '讲座' in full_text:
                item['activity_type'] = '讲座'
            elif '培训' in full_text:
                item['activity_type'] = '培训'
            elif '阅读' in full_text:
                item['activity_type'] = '阅读'
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
        for i in range(len(p_content)):
            if '主办单位：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            elif '举办单位：' == p_content[i] or '主办单位' == p_content[i]:
                item['organizer'] = p_content[i + 1]
                break
            elif '举办单位：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            elif '主 办：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            elif '举办：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            # 举办

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
        item['source'] = ''
        ########################################################################################
        item['activity_introduction'] = ''
        ########################################################################################
        return item

    def intro_parse(self, response):
        item = CultureBasicItem()
        item['pav_name'] = '宁夏图书馆'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find("div", {"class": "art"})
        p_tags = content.find_all('p')
        full_text = ''
        for p in p_tags:
            full_text = full_text + str(p.text)
        item['pav_introduction'] = full_text.replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        item['region'] = '宁夏'
        item['area_number'] = '3.32万平方米'
        item['collection_number'] = '190万册'
        item['branch_number'] = ''
        item['librarian_number'] = '139人'
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

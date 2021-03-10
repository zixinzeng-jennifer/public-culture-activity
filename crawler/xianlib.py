# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class XianlibSpider(scrapy.Spider):
    name = 'xianlib'
    allowed_domains = ['xalib.org.cn']
    start_urls = ['http://xalib.org.cn/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.xalib.org.cn/node/393.jspx'

    # 爬去机构活动所需的参数
    event_url = 'http://www.xalib.org.cn/node/395.jspx'
    event_base_url = 'http://www.xalib.org.cn/node/395_'
    event_count = 1
    event_page_end = 45

    def start_requests(self):

        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = soup.find('div', {'class': 'content_page'})
        contents = intro.find_all('p', {'style': 'LINE-HEIGHT: 33px; TEXT-INDENT: 40px; MARGIN: 5px 0px'})
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['pav_name'] = '西安图书馆'
        item['pav_introduction'] = fulltext
        item['region'] = '西安'
        item['area_number'] = '3万平方米'
        item['collection_number'] = '429万册'
        item['branch_number'] = '18'
        item['librarian_number'] = ''
        item['client_number'] = '110万次'
        item['activity_number'] = ''
        yield item

    def event_parse(self, response):
        origin_url = 'http://www.xalib.org.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('div', {'class': 'newsList2'})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '西安图书馆'
                item['activity_name'] = re.findall(r'\d、(.+)', event.a.text)[0]
                item['activity_time'] = event.find('span', {'class': 'time'}).text
                item['url'] = origin_url + event.a.attrs['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url + str(self.event_count) + '.jspx', callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "page_right"})
        p_tags = content.find_all('p')
        p_content = []
        full_text=[]
        for p in p_tags:
            p_content.append(str(p.text).strip().replace('\u3000', '').replace('\xa0', ''))
            full_text.append(p.text)
        item['remark'] = ''.join(p_content)

        try:
            item['place'] = re.findall(r'(西安图书馆.{1,10}厅)', ''.join(full_text))[0]
        except:
            item['place'] = ''
        if item['place'] == '':
            try:
                item['place'] = re.findall(r'地点：(.+)\n', ''.join(full_text))[0]
            except:
                item['place'] = ''
        try:
            item['participation_number'] = re.findall(r'参加活动的(.{1,4})位读者', ''.join(full_text))[0]
        except:
            item['participation_number'] = ''
        if item['participation_number'] == '':
            try:
                item['participation_number'] = re.findall(r'(\d{1,4})人', ''.join(full_text))[0]
            except:
                item['participation_number'] = ''
        if item['participation_number'] == '':
            try:
                item['participation_number'] = re.findall(r'(\d{1,4})余人', ''.join(full_text))[0]
            except:
                item['participation_number'] = ''
        try:
            item['organizer'] = re.findall(r'由(.{3,15})主办', ''.join(full_text))[0]
        except:
            item['organizer'] = ''
        if item['organizer'] == '':
            try:
                item['organizer'] = re.findall(r'主办部门：(.+)\n', ''.join(full_text))[0]
            except:
                item['organizer'] = ''
        try:
            item['activity_time'] = re.findall(r'(\d{4}年\d{1,2}月\d{1,2}日.{0,2}\d{4}年\d{1,2}月\d{1,2}日)', ''.join(full_text))[0]
        except:
            pass
        try:
            if '展览' in ''.join(full_text):
                item['activity_type'] = '展览'
            elif '讲座' in full_text:
                item['activity_type'] = '讲座'
            elif '培训' in full_text:
                item['activity_type'] = '培训'
            elif '阅读' in full_text:
                item['activity_type'] = '阅读'
        except:
            pass
        return item

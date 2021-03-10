# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class ChangchunwhgSpider(scrapy.Spider):
    name = 'changchunwhg'
    allowed_domains = ['ccqw.cn']
    start_urls = ['http://ccqw.cn/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.ccqw.cn/bgjs.html'

    # 爬去机构动态所需的参数
    news_url = 'http://www.ccqw.cn/xwzx/'
    news_base_url = 'http://www.ccqw.cn/xwzx/index_'
    news_count = 1
    news_page_end = 34

    # 爬去机构活动所需的参数
    event_url = 'http://www.ccqw.cn/hdyg/index.html'
    event_base_url = 'http://www.ccqw.cn/hdyg/index_'
    event_count = 1
    event_page_end = 25

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
        intro = str(soup.find('div', {'class': 'content'}).text).strip()
        item['pav_name'] = '长春市文化馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0',
                                                                                                           '').replace(
            '\ufeff', '')
        item['region'] = '长春'
        item['area_number'] = ''
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = '62'
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('ul', {"class": "list-menu m-b30"})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '长春市文化馆'
                item['title'] = article.a.string
                item['url'] = article.a.attrs['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
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
        item['time'] = re.findall(r'\d{4}-\d{1,2}-\d{1,2}', soup.find('div', {'class': 'content'}).text)[0]
        contents = soup.find("div", {"class": "content"}).find_all('p')
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['content'] = fulltext
        return item

    def event_parse(self, response):
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('ul', {'class': 'list-menu m-b30'})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '长春市文化馆'
                item['activity_name'] = event.a.string
                item['url'] = event.a.attrs['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url + str(self.event_count) + '.html', callback=self.event_parse)
        else:
            return None

    def rule_match(self, rule_id, text):
        text = str(text)
        if rule_id == 'place':
            result = ''
            if result == '':
                try:
                    result = re.findall(r'在(.{3,20})共同举办', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'在(.{3,20})举办', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'在(.{3,20})举行', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'在(.{3,20})拉开帷幕', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'在(.{3,20})开幕', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'在(.{3,20})开展', text)[0]
                except:
                    result = ''

        elif rule_id == 'activity_type':
            try:
                if '展览' or '艺术展' in text:
                    result = '展览'
                elif '讲座' in text:
                    result = '讲座'
                elif '培训' in text:
                    result = '培训'
                elif '阅读' in text:
                    result = '阅读'
                elif '比赛' or '大赛' in text:
                    result = '比赛'
            except:
                result = ''

        elif rule_id == 'activity_time':

            try:
                result = re.findall(r'(\d{4}年\d{1,2}月\d{1,2}日-\d{1,2})日', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'(\d{4}年\d{1,2}月\d{1,2}日-\d{1,2})月\d{1,2})日', text)[0]
                except:
                    result = ''


        elif rule_id == 'organizer':
            try:
                result = re.findall(r'由(.{3,30})主办', text)[0]
            except:
                result = ''
        elif rule_id == 'age_limit':
            try:
                result = re.findall(r'(\d{1,2}岁至\d{1,2}岁)', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'(\d{1,2}岁-\d{1,2}岁)', text)[0]
                except:
                    result = ''

        elif rule_id == 'participation_number':
            try:
                result = re.findall(r'(\d{1,4})名', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'(\d{1,4})余人', text)[0]
                except:
                    result = ''
        elif rule_id == 'contact':
            try:
                result = re.findall(r'(\d{4}-\d{8})', text)[0]
            except:
                result = ''

        return result

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "content"})
        item['source'] = str(content.find('h2').find_all('span')[0].text).split('：')[1].strip()
        activity_time = str(content.find('h2').find_all('span')[1].text).split('：')[1].strip()[:10]
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t', ''))
        text = ' '.join(p_content)
        item['remark'] = ''.join(p_content)
        ##############################################
        item['place'] = self.rule_match('place', text=text)
        item['activity_type'] = self.rule_match('activity_type', text=text)
        item['activity_time'] = self.rule_match('activity_time', text=text)
        if item['activity_time'] == '':
            item['activity_time'] = activity_time
        item['organizer'] = self.rule_match('organizer',text=text)
        item['participation_number'] =self.rule_match('participation_number',text=text)
        item['contact'] = self.rule_match('contact',text=text)
        return item

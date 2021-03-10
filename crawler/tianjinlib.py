# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import time
import re


class TianjinlibSpider(scrapy.Spider):
    name = 'tianjinlib'

    selenium_path = 'D:\WorkSpace\Culture-Bigdata\cultureBigdata\chromedriver.exe'
    # 爬去机构介绍所需的参数
    intro_url = 'http://www.tjl.tj.cn/ArticleChannel.aspx?ChannelID=287'

    # 爬去机构动态所需的参数
    news_url = 'http://www.tjl.tj.cn/ArticleChannel.aspx?ChannelID=241&pageindex=1'
    news_base_url = 'http://www.tjl.tj.cn/ArticleChannel.aspx?ChannelID=241&pageindex='
    news_count = 1
    news_page_end = 169

    # 爬去机构活动所需的参数
    event_url = 'http://www.tjl.tj.cn/Pages/TrainList.aspx?Campus=&StartTime2=&EndTime2=&Trainid=&page=1'
    event_base_url = 'http://www.tjl.tj.cn/Pages/TrainList.aspx?Campus=&StartTime2=&EndTime2=&Trainid=&page='
    event_count = 1
    event_page_end = 45

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
        intro = str(soup.find('div', {'class': 'text_con'}).text).strip()
        item['pav_name'] = '天津图书馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0',
                                                                                                           '').replace(
            '\t', '')
        item['region'] = '天津'
        item['area_number'] = '12万平米'
        item['collection_number'] = '1200万册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.tjl.tj.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', {"id": "rightcon"})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '天津图书馆'
                item['title'] = article.a.string
                item['url'] = origin_url + article.a.attrs['href']
                item['time'] = article.span.string
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
        contents = soup.find("div", {"class": "text_con"}).find_all('p')
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['content'] = fulltext
        return item

    def event_parse(self, response):
        origin_url = 'http://www.tjl.tj.cn/Pages/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        for event in soup.find_all('tr', {'class': 'gvRow'}):
            item = CultureEventItem()
            try:
                item['pav_name'] = '天津图书馆'
                item['activity_name'] = str(event.find_all('td', {'class': 'alignL'})[0].text).replace('\n', '')
                item['url'] = origin_url + event.find_all('td', {'class': 'alignL'})[0].find('a')['href']
                item['place'] = str(event.find_all('td', {'class': 'alignL'})[1].text).replace('\n', '')
                item['activity_time'] = event.find('td', {'class': 'alignC'}).text
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)

            except Exception as err:
                print(err)
        for event in soup.find_all('tr', {'class': 'tal'}):
            item = CultureEventItem()
            try:
                item['pav_name'] = '天津图书馆'
                item['activity_name'] = str(event.find_all('td', {'class': 'alignL'})[0].text).replace('\n', '')
                item['url'] = origin_url + event.find_all('td', {'class': 'alignL'})[0].find('a')['href']
                item['place'] = str(event.find_all('td', {'class': 'alignL'})[1].text).replace('\n', '')
                item['activity_time'] = event.find('td', {'class': 'alignC'}).text
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url + str(self.event_count), callback=self.event_parse)
        else:
            return None

    def rule_match(self, rule_id, text):
        text = str(text)
        if rule_id == 'activity_type':
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
        elif rule_id == 'presenter':
            try:
                result = re.findall(r'主\xa0讲\xa0人：(.{2,30})\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'主讲人：(.{2,30})\n', text)[0]
                except:
                    result = ''
            elif result == '':
                try:
                    result = re.findall(r'主 讲 人：(.{2,30})\n', text)[0]
                except:
                    result = ''
            elif result == '':
                try:
                    result = re.findall(r'领读人：(.{2,30})\n', text)[0]
                except:
                    result = ''
        elif rule_id == 'organizer':
            try:
                result = re.findall(r'主办单位：(.{3,30})\n', text)[0]
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
                result = re.findall(r'咨询电话：(.{8,20})\n', text)[0]
            except:
                result = ''
        elif rule_id == 'presenter_introduction':
            try:
                result = re.findall(r'主讲人简介：\n(.+)。\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'导读人简介：\n(.+)\n', text)[0]
                except:
                    result = ''
        elif rule_id == 'activity_introduction':
            try:
                result = re.findall(r'内容介绍：\xa0\n(.+)。\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'讲座内容：\n\xa0\n(.+)\n', text)[0]
                except:
                    result = ''
            elif result == '':
                try:
                    result = re.findall(r'讲座内容：\n(.+)。\n', text)[0]
                except:
                    result = ''
            elif result == '':
                try:
                    result = re.findall(r'内容简介：\xa0\n(.+)。\n', text)[0]
                except:
                    result = ''
        return result

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class": "content"}).text
        content2 = soup.find('div', {'class': 'info'}).find_all('span')
        item['source'] = str(content2[0].text).split('：')[1]
        item['click_number'] = str(content2[2].text).split('：')[1]
        item['presenter'] = self.rule_match('presenter', text=content)
        item['activity_type'] = self.rule_match('activity_type', text=content)
        item['presenter_introduction'] = self.rule_match('presenter_introduction', text=content)
        item['organizer'] = self.rule_match('organizer', text=content)
        item['age_limit'] = self.rule_match('age_limit', text=content)
        item['participation_number'] = self.rule_match('participation_number', text=content)
        item['contact'] = self.rule_match('contact', text=content)
        item['remark'] = str(content).strip().replace('\u3000', '').replace('\r', '').replace('\n', ' ').replace(
                '\xa0', '').replace('\t', '')
        return item

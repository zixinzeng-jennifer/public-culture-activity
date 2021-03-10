# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class GuangxiSpider(scrapy.Spider):
    name = 'guangxilib'
    allowed_domains = ['gxlib.org.cn']

    # 爬去机构动态所需的参数
    news_url = 'http://www.gxlib.org.cn/news_list.aspx?category_id=56'
    news_base_url = 'http://www.gxlib.org.cn/news_list.aspx?category_id=56&page='
    news_count = 1
    news_page_end = 96

    event_url='http://www.gxlib.org.cn/news_list.aspx?category_id=55'
    event_base_url = 'http://www.gxlib.org.cn/news_list.aspx?category_id=55&page='
    event_count = 1
    event_page_end = 7

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.gxlib.org.cn/content.aspx?page=about'

    # 爬去机构活动所需的参数

    
    # 爬去展览所需的参数
    zl_url = 'http://202.103.233.140:8004/zlhg_list.aspx?category_id=81&page=1'
    zl_base_url = 'http://202.103.233.140:8004/zlhg_list.aspx?category_id=81&page='
    zl_count = 1
    zl_page_end = 9
    
    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        #请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        # 请求展览信息
        yield scrapy.Request(self.zl_url, callback=self.zl_parse)
        
    def news_parse(self, response):
        origin_url = 'http://www.gxlib.org.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        #print(soup)
        article_lists = soup.find('ul', {"class": 'lby_r_list'})
        #print(article_lists)
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '广西壮族自治区图书馆'
                item['title'] = article.a.string
                item['url'] = origin_url + article.a['href']
                item['time'] = re.findall(r'\d{4}\/\d{0,1}\/\d{1,2}',article.span.string)[0]
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
        content = soup.find("div", {"class": "entry"})
        item['content'] = str(content.text).strip().replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item

    def zl_parse(self, response):
        origin_url = 'http://202.103.233.140:8004'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        #print(soup)
        zl_lists = soup.find('div', {'class': 'about_context_t ohide'})
        for zl in zl_lists.find_all('div',{'class':'news-list'}):
            item = CultureEventItem()
            #print(zl)
            try:
                item['pav_name'] = '广西壮族自治区图书馆'
                item['activity_name'] = zl.a.string.replace('\n','').strip()
                item['activity_type'] = '展览'
                item['activity_time'] = re.findall(r'展览日期：(.*)',zl.span.string)[0]
                item['url'] = origin_url + zl.a['href']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.zl_text_parse)
            except Exception as err:
                print(err)
        if self.zl_count < self.zl_page_end:
            self.zl_count = self.zl_count + 1
            print(self.zl_base_url+str(self.zl_count))
            yield scrapy.Request(self.zl_base_url+str(self.zl_count),callback=self.zl_parse)
        else:
            return None

    def zl_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "about_context_t ohide"})
        full_text = str(content.text).strip().replace('\xa0', '').replace('\u3000', '')
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\xa0', '').replace('\u3000', ''))
        # print(p_content)
        ########################################################################################
        item['remark'] = full_text .replace('\xa0','').replace('\n', '')
        ########################################################################################
        # 活动地点 = place
        item['place'] = ''

        ########################################################################################

        item['presenter'] = ''

        ########################################################################################
        item['organizer'] = ''
        try:
            if re.findall(r'主办单位：(.*)协办单位：',full_text):
                item['organizer'] = re.findall(r'主办单位：(.*)协办单位：',full_text)[0]
        except:
            pass
        ########################################################################################
        item['presenter_introduction'] = ''

        ########################################################################################
        item['contact'] = ''
               ########################################################################################
        item['participation_number'] = ''
                ########################################################################################
        item['activity_introduction'] = ''
        ########################################################################################
        return item

    def event_parse(self, response):
        origin_url = 'http://www.gxlib.org.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        # print(soup)
        article_lists = soup.find('ul', {"class": 'lby_r_list'})
        # print(article_lists)
        for article in article_lists.find_all("li"):
            item = CultureEventItem()
            try:
                item['pav_name'] = '广西壮族自治区图书馆'
                item['activity_name'] = article.a.string
                item['url'] = origin_url + article.a['href']
                item['activity_time'] = re.findall(r'\d{4}\/\d{0,1}\/\d{1,2}', article.span.string)[0].replace('/','-')
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
        content = soup.find('div', {"class", "entry"})
        full_text = str(content.text).strip().replace('\xa0', '').replace('\u3000', '').replace('\r','').replace('\t','').replace('\n','')
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\xa0', '').replace('\u3000', ''))
        # print(p_content)
        ########################################################################################
        item['remark'] = full_text .replace('\xa0','').replace('\n', '')

        ########################################################################################
        # 活动地点 = place
        item['place'] = ''
        for i in range(len(p_content)):
            if '地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '地   点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '活动地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '展览地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
        ########################################################################################

        item['presenter'] = ''
        for i in range(len(p_content)):
            if '主讲人：' in p_content[i]:
                item['presenter'] = p_content[i].split('：')[1]
                break
            elif '分享嘉宾：' in p_content[i]:
                name_intro = p_content[i].split('：')[1]
                item['presenter'] = re.findall(r'(.*)，',full_text)[0]
                break
        ########################################################################################
        item['organizer'] = ''
        for i in range(len(p_content)):
            if '主办：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
        ########################################################################################
        item['presenter_introduction'] = ''
        try:
            if re.findall(r'【主讲人简介】：  ((\s)*.*)'):
                item['presenter_introduction'] = re.findall(r'【主讲人简介】：  ((\s)*.*)',full_text)[0]
            elif '分享嘉宾：' in p_content[i]:
                name_intro = p_content[i].split('：')[1]
                name = re.findall(r'(.*)，',full_text)[0]
                item['presenter_introduction'] = name_intro[len(name_intro)-len(name)-1:]
        except:
            pass
        ########################################################################################
        item['contact'] = ''
               ########################################################################################
        item['participation_number'] = ''
                ########################################################################################
        item['activity_introduction'] = ''
        ########################################################################################
        return item

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {"class": 'entry'}).text).strip()
        item['pav_name'] = '广西壮族自治区图书馆'
        item['pav_introduction'] = intro .replace('\xa0','').replace('\u3000\u3000', '')
        item['region'] = '广西壮族自治区'
        item['area_number'] = '5.4万平方米'
        item['collection_number'] = '421万余册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

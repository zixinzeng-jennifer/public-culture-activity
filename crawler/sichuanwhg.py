# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class SiChuanwhgSpider(scrapy.Spider):
    name = 'sichuanwhg'
    allowed_domains = ['scc.org.cn']

    # 爬去机构动态所需的参数
    news_url = 'http://www.scc.org.cn/ggwhfw/gyzl/'
    news_base_url = 'http://www.scc.org.cn/ggwhfw/gyzl/index_'
    news_count = 1
    news_page_end = 6

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.hbqyg.cn/gwgk/bgjs/index.shtml'

    # 爬去机构活动所需的参数
    event_url = 'http://www.scc.org.cn/ggwhfw/gyzl/'
    event_base_url = 'http://www.scc.org.cn/ggwhfw/gyzl/index_'
    event_count = 1
    event_page_end = 6

    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def news_parse(self, response):
        origin_url = 'http://www.hbqyg.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        #print(soup)
        article_lists = soup.find('section', {"class": 'p_fw_zl'})
        #print(article_lists)
        for article in article_lists.find_all("dl"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '湖北省群众艺术馆'
                item['title'] = article.dy.a.string
                item['url'] = origin_url + article.a['href']
                item['time'] = article.span.string
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
        content = soup.find("div", {"class": "article"})
        item['content'] = str(content.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item


    def event_parse(self, response):
        origin_url = 'http://www.scc.org.cn/ggwhfw/gyzl/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('section', {"class":'p_fw_zl'})
        #type = soup.find('dd',{"class":"intro gray"})
        #print(event_lists)
        for event in event_lists.find_all('dl'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '四川省文化馆'
                item['activity_name'] = event.dt.a.string
                print(item['activity_name'])
                introduction = event.find_all("dd",{"class":"text gray"})[0].a.text
                #print(introduction)
                #print('1')
                item['activity_introduction'] = introduction.strip().replace('<h3>','').replace('</h3>','')
                #print('2')
                type = event.find('dd', {"class": "intro"}).find('a').string
                #print(type)
                item['activity_type'] = type
                item['url'] = origin_url + event.dt.a['href'][2:]
                #print("debug",event.find('dd', {"class": "intro"}).text)
                item['activity_time'] = re.findall(r'\d{4}-\d{2}-\d{2}',event.find('dd', {"class": "intro"}).text)[0]
                print(item['activity_time'])
                print(item['activity_name'])
                print(item['url'])
                print(item['activity_type'])
                print(item['activity_time'])
                print(item['activity_introduction'])
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url+str(self.event_count) + '.html',callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "p_dis_cont wow fadeInUp"})
        full_text = str(content.text).strip().replace('\xa0', '').replace('\u3000', '').replace('\u2003','').replace
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\xa0', '').replace('\u3000', ''))
                # print(p_content)
        ########################################################################################
        try:
            click = content.find('div',{'class': 'time f12 gray'}).span.text
            print("debug:",click)
            item['click_number'] = click#re.findall(r'阅读：(\d*)',click)[0]
        except:
            pass
        item['remark'] = full_text.replace('\xa0','').replace('\n', '')
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

        return item

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {"class": 'article'}).text).strip()
        item['pav_name'] = '湖北省群众艺术馆'
        item['pav_introduction'] = intro .replace('\xa0','').replace('\u3000\u3000', '')
        item['region'] = '湖北'
        item['area_number'] = ''
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class ShanghaiSpider(scrapy.Spider):
    name = 'shanghaiwhg'
    allowed_domains = ['http://shqyg.com/']

    # 爬去机构动态所需的参数
    news_url = ''
    news_base_url = ''
    news_count = 1
    news_page_end = 4

    # 爬去机构介绍所需的参数
    intro_url = ''

    # 爬去机构活动所需的参数
    event_url = 'http://shqyg.com/activity/list.html'


    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def news_parse(self, response):
        pass
        origin_url = ''
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        #print(soup)
        article_lists = soup.find('ul', {"id": 'zebra'})
        #print(article_lists)
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = ''
                item['title'] = article.a.string
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
        pass
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        content = soup.find("div", {"class": "TRS_Editor"})
        item['content'] = str(content.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item


    def event_parse(self, response):
        origin_url = 'http://shqyg.com/activity/list.html'
        driver=webdriver.Chrome('D://Workspace/Culture-Bigdata/cultureBigdata/chromedriver.exe')
        driver.get(self.event_url)
        for i in range(0, 30):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            i += 1
            time.sleep(1.5)
        driver.implicitly_wait(10)
        driver.implicitly_wait(3)
        data = driver.page_source
        soup = BeautifulSoup(data, 'html.parser')
        print(soup.prettify())
        event_lists = soup.find('ul', {'class': 'actListUl'})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '上海市群众艺术馆'
                item['activity_name'] = event.find('div',{'class':'titleEr'}).text.replace('\n','').strip()
                item['activity_time'] = event.find('div',{'class':'time'}).text.replace('\n','').strip()
                item['url'] = origin_url + event.a['href'][2:].strip()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)


    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "TRS_Editor"})
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
        intro = str(soup.find('div', {"class": 'TRS_Editor'}).text).strip()
        item['pav_name'] = '陕西省图书馆'
        item['pav_introduction'] = intro .replace('\xa0','').replace('\u3000\u3000', '')
        item['region'] = '陕西'
        item['area_number'] = '4.7万平方米'
        item['collection_number'] = '525万余册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

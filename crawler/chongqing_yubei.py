# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureEventItem, CultureNewsItem, CultureBasicItem
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time


class chongqing_yubei_Spider(scrapy.Spider):
    name = 'chongqing_yubei'
    #chrome_options = Options()
    #chrome_options.add_argument("--start-maximized");

    # allowed_domains = ['http://www.nmgbwy.com/']

    # 爬去机构介绍所需的参数
    # intro_url = 'http://www.nmgbwy.com/bwyjs.jhtml?contentId=147'

    selenium_path = "C://Users/Zixin Zeng/AppData/Local/chromedriver.exe"
    # 爬去机构讲座活动所需的参数
    event_url = 'http://219.153.116.11:9100/?q=64'


    def start_requests(self):
        # 请求机构介绍信息
        # yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        # yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        # yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    def event_parse(self, response):
        data=response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find_all('div', {'class': 'list-item'})
        for article in article_lists:
            item = CultureEventItem()
            try:
                item['pav_name'] = '渝北区公共文旅服务平台'
                link=article.find_all('span',{'class':'item-title'})[0]
                item['url'] = 'http://219.153.116.11:9100/' + link.a.attrs['href'][1:]
                item['activity_type']=article.find('font',{'class':'hdtype'}).text
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        time.sleep(5)

    def event_text_parse(self, response):
        #try:
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        item['activity_name'] = soup.find('div', {'class': 'main-content-head-left'}).text.strip()
        basic_info = soup.find_all('span', {'class': 'top-box-right-text'})
        item['organizer'] = basic_info[0].text[6:]
        item['activity_time'] = basic_info[1].text[6:]
        item['place'] = basic_info[2].text[6:]
        item['contact'] = ''
        item['presenter'] = basic_info[3].text[6:]
        lst = []
        a = soup.find_all('div', {'class': 'bottom-box-content'})[0]
        for p in a.find_all('p'):
            lst.append(p.text.strip())
        p_content = ''.join(lst)
        item['remark'] = ''.join(p_content)
        ########################################################################################

        ########################################################################################
        item['age_limit'] = ''
        try:
            if re.findall(r'不限年龄', p_content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'不限年龄', p_content)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', p_content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', p_content)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', p_content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', p_content)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', p_content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', p_content)[0]
        except:
            pass
        ########################################################################################
        item['presenter_introduction'] = soup.find_all('div', {'class': 'middle-box-body'})[0].text.strip()
        #except Exception as err:
            #print(err)
        ########################################################################################
        return item

# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import time


class NanjinglibSpider(scrapy.Spider):
    name = 'nanjinglib'
    allowed_domains = ['jslib.org.cn']
    start_urls = ['http://jslib.org.cn/']
    selenium_path = 'D:\WorkSpace\Culture-Bigdata\cultureBigdata\chromedriver.exe'

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.jslib.org.cn/pub/njlib/njlib_ntgk/201701/t20170109_150736.htm'

    # 爬去机构动态所需的参数
    news_url = 'http://www.jslib.org.cn/njlib_gqsb/#'
    news_count = 1
    news_page_end = 28

    # 爬去机构活动所需的参数
    event_url = 'http://www.jslib.org.cn/pub/njlib/njlib_wsbgt/njlib_jzbd/#'
    event_count = 1
    event_page_end = 12

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
        intro = str(soup.find('div', {'class': 'TRS_Editor'}).find('span').text).strip()
        item['pav_name'] = '南京图书馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
        item['region'] = '南京'
        item['area_number'] = '7.8万平方米'
        item['collection_number'] = '1200万册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = '100万'
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        click_Xpath = '//*[@id="pl"]/a[28]'
        origin_url = 'http://www.jslib.org.cn/njlib_gqsb/'
        driver.get(self.news_url)
        while self.news_count < self.news_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find_all('li')
            for article in article_lists:
                item = CultureNewsItem()
                try:
                    item['pav_name'] = '南京图书馆'
                    item['title'] = article.a.string
                    item['url'] = origin_url + article.a.attrs['href'][2:]
                    item['time'] = str(article.font.string).replace('\xa0', '')[4:]
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
                except Exception as err:
                    print(err)
            self.news_count = self.news_count + 1
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        contents = soup.find('div', {'class': 'TRS_Editor'}).find_all('p')
        full_text = []
        for content in contents:
            full_text.append(str(content.text).strip().replace('\xa0', '').replace('\n', ''))
        fulltext = ''.join(full_text)
        item['content'] = fulltext
        return item

    def event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        click_Xpath = '//*[@id="pl"]/a[12]'
        origin_url = 'http://www.jslib.org.cn/pub/njlib/njlib_wsbgt/njlib_jzbd/'
        driver.get(self.event_url)
        while self.event_count < self.event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find_all('li')
            for article in article_lists:
                item = CultureEventItem()
                try:
                    item['pav_name'] = '南京图书馆'
                    item['activity_name'] = article.a.string
                    item['url'] = origin_url + article.a.attrs['href'][2:]
                    item['activity_time'] = str(article.font.string).replace('\xa0', '')[4:]
                    item['activity_type'] = '讲座'
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.event_count = self.event_count + 1
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        contents = soup.find('div', {'class': 'TRS_Editor'}).find_all('p')
        full_text = []
        for content in contents:
            full_text.append(str(content.text).strip().replace('\xa0', '').replace('\n', '').replace('\u3000', ''))
        fulltext = ''.join(full_text)
        try:
            item['remark'] = fulltext
        except:
            item['remark'] = ''
        return item

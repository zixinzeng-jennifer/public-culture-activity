# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time






class ChongqingwhgSpider(scrapy.Spider):
    name = 'chongqingwhg'
    allowed_domains = ['cqqyg.cn']
    start_urls = ['http://cqqyg.cn/']

    selenium_path = 'C://Users/Zixin Zeng/AppData/Local/chromedriver.exe'
    # 爬去机构介绍所需的参数
    intro_url = 'https://www.cqqyg.cn/aboutUs/aboutUsAllInfo.do'

    # 爬去机构动态所需的参数
    news_url = 'https://www.cqqyg.cn/beipiaoInfo/czfrontindex.do?module=ZXZX'
    news_count = 1
    news_page_end = 52

    # 爬去机构活动所需的参数
    event_url = 'https://www.cqqyg.cn/frontActivity/activityList.do#'
    event_count = 1
    event_page_end = 3

    # 爬去机构活动所需的参数
    px_event_url = 'https://www.cqqyg.cn/frontActivity/activityList.do#'
    px_event_count = 1
    px_event_page_end = 5

    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        #yield scrapy.Request(self.px_event_url, callback=self.px_event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intros = soup.find_all('p', {'class': 'depict'})
        texts =[]
        for intro in intros:
            texts.append(intro.text)
        item['pav_name'] = '重庆群众文化云'
        item['pav_introduction'] = ''.join(texts)
        item['region'] = '重庆'
        item['area_number'] = ''
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = '20万'
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(self.selenium_path, chrome_options=chrome_options)
        notice_Xpath= '//*[@id="zxTypes"]/ul/li[4]/a'
        click_Xpath = '//*[@id="kkpager_btn_go"]'
        origin_url = 'https://www.cqqyg.cn'
        driver.get(self.news_url)
        driver.find_element_by_xpath(notice_Xpath).click()
        while self.news_count < self.news_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('ul',{'class': 'zxList'}).find_all('li')
            for article in article_lists:
                item = CultureNewsItem()
                try:
                    item['pav_name'] = '重庆群众文化云'
                    item['title'] = str(article.find('p', {'class': 'info fl'}).text).strip()
                    item['url'] = origin_url + article.a.attrs['href']
                    news_time = article.find('p', {'class': 'char fl'}).text
                    try:
                        item['time'] = re.findall(r'(\d{4}-\d{2}-\d{2})', news_time)[0]
                    except:
                        item['time'] = ''
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
        contents = soup.find('div', {'class': 'article'}).find_all('p')
        full_text = []
        for content in contents:
            full_text.append(str(content.text).strip().replace('\xa0', '').replace('\n', ''))
        fulltext = ''.join(full_text)
        item['content'] = fulltext
        return item

    def event_parse(self, response):
        chrome_options = Options()
        #chrome_options.add_argument('--headless')
        #chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(self.selenium_path, options=chrome_options)
        origin_url = 'https://www.cqqyg.cn'
        driver.get(self.event_url)
        click_Xpath = '//*[@id="kkpager_btn_go"]'
        while self.event_count < self.event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            print(soup.prettify())
            print(soup.find('ul', {'class': "hl_list"}))
            article_lists = soup.find('ul', {'class': "hl_list"}).find_all('li')#debug
            for article in article_lists:
                item = CultureEventItem()
                try:
                    item['pav_name'] = '重庆群众文化云'
                    item['activity_name'] = article.find('div', {'class': 'intro'}).find('a').text
                    item['url'] = origin_url + str(article.find('div', {'class': 'intro'}).find('a')['href'])[2:]
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.event_count = self.event_count + 1
            driver.find_element_by_link_text("下一页").click()
            print("下一页")
            time.sleep(1)
        driver.close()

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            item['activity_type'] = soup.find('div', {'id': 'tag'}).text
        except:
            item['activity_type'] = ''
        try:
            item['place'] = str(soup.find('div', {'class': 'al_r fl'}).find('p', {'class': 'site'}).span.string).\
                strip().replace('\r','').replace('\n','')
        except:
            item['place'] = ''
        try:
            item['activity_time'] = str(soup.find('div', {'class': 'al_r fl'}).find('p', {'class': 'time'}).
                                        span.string).strip().replace('\r','').replace('\n','').replace(' ','').replace('\t', '')
        except:
            item['activity_time'] = ''
        try:
            item['contact'] = str(soup.find('div', {'class': 'al_r fl'}).find('p', {'class': 'phone'}).span.string).\
                strip().replace('\r','').replace('\n','')
        except:
            item['contact'] = ''
        texts = soup.find('div', {'class': 'ad_intro'}).find_all('p')
        content = []
        for text in texts:
            content.append(text.text)
        fulltext=''.join(content)
        item['remark'] = fulltext.strip().replace('\r','').replace('\n','')
        return item

    def px_event_parse(self, response):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(self.selenium_path, chrome_options=chrome_options)
        origin_url = 'https://www.cqqyg.cn/cmsTrain/trainDetail.do?id='
        driver.get(self.event_url)
        click_Xpath = '//*[@id="kkpager_btn_go"]'
        while self.event_count < self.event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('ul', {'class': "hl_list clearfix"}).find_all('li')
            for article in article_lists:
                item = CultureEventItem()
                try:
                    item['pav_name'] = '重庆群众文化云'
                    item['activity_name'] = article.find('div', {'class': 'intro'}).find('a').text

                    item['activity_type'] = '培训'
                    item['activity_time'] = article.find('div', {'class': 'intro'}).find_all('p')[0].text

                    item['place'] = article.find('div', {'class': 'intro'}).find_all('p')[1].text

                    yield item
                except Exception as err:
                    print(err)
            self.px_event_count = self.px_event_count + 1
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def px_event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            item['age_limit'] = str(soup.find('div', {'class': 'age'}).text)[5:].strip().replace('\r', '').replace('\n', '')
        except:
            item['age_limit'] = ''
        try:
            item['activity_introduction'] = soup.find('div', {'id': 'courseIntroduction'}).text
        except:
            item['activity_introduction'] = ''
        texts = soup.find('div', {'class': 'peixunCourse'}).text
        item['remark'] = texts
        return item


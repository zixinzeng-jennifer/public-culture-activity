# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class ShanXiwhgSpider(scrapy.Spider):
    name = 'shanxiwhg'
    allowed_domains = ['sxsysg.com']
    start_urls = ['http://www.sxsysg.com/sn/user_index']
    selenium_path = 'D:\专业\小组\图书馆、文化馆调研\大二下\cultureBigdata\chromedriver.exe'

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.zjhzart.cn/news630.htm'

    # 爬去机构动态所需的参数
    news_url = 'http://www.sxsysg.com/sn/user_newsMore/'
    news_count = 1
    news_page_end = 7

    # 爬去机构培训活动所需的参数
    px_event_url = ''
    px_event_count = 1
    px_event_page_end = 2

    # 爬去机构培训活动所需的参数
    px_event_url = 'http://www.zjhzart.cn/news611.htm'
    px_event_count = 1
    px_event_page_end = 2

    # 爬去机构演出活动所需的参数
    yc_event_url = 'http://www.zjhzart.cn/NewsFreeService612.htm'
    yc_event_count = 1
    yc_event_page_end = 34

    # 爬去机构演出活动所需的参数
    zl_event_url = 'http://www.zjhzart.cn/NewsFreeService613.htm'
    zl_event_count = 1
    zl_event_page_end = 37

    # 爬去机构演出活动所需的参数
    jz_event_url = 'http://www.zjhzart.cn/NewsFreeService615.htm'
    jz_event_count = 1
    jz_event_page_end = 27

    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        #yield scrapy.Request(self.px_event_url, callback=self.px_event_parse)
        #yield scrapy.Request(self.yc_event_url, callback=self.yc_event_parse)
        #yield scrapy.Request(self.zl_event_url, callback=self.zl_event_parse)
        #yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('tbody').find('p').text).strip()
        item['pav_name'] = '杭州文化馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '')
        item['region'] = '杭州'
        item['area_number'] = '6500平方米'
        item['collection_number'] = ''
        item['branch_number'] = '8'
        item['librarian_number'] = '28'
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        origin_url = 'http://www.zjhzart.cn/'
        click_Xpath = '///*[@id="next"]/a'
        driver.get(self.news_url)
        while self.news_count < self.news_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('div', {"class": "list-left vote-listed"})
            #print(article_lists)
            for article in article_lists.find_all('div'):
                item = CultureNewsItem()
                try:
                    item['pav_name'] = '陕西公共文化数字平台'
                    item['title'] = article.dt.a.attrs['title']
                    item['url'] = origin_url + article.dt.a.attrs['href']
                    item['time'] = article.dd.string
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
        html = soup.find('div', {'class': 'pxxz_detailed'})
        p_tags = html.find_all('p')
        contents = []
        for p in p_tags:
            contents.append(
                str(p.text).strip().replace('\u3000', '').replace('\n', '').replace('\r', '').replace('\xa0', ''))
        full_text = ''.join(contents)
        item['content'] = full_text
        return item

    def px_event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        origin_url = 'http://www.zjhzart.cn/'
        click_Xpath = '//*[@id="ContentPlaceHolder1_AspNetPager1"]/table/tbody/tr/td[2]/a[4]'
        driver.get(self.px_event_url)
        while self.px_event_count < self.px_event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('div', {"class": "news_list"})
            for article in article_lists.find_all("dl"):
                item = CultureEventItem()
                try:
                    item['pav_name'] = '杭州文化馆'
                    item['activity_name'] = article.dt.a.attrs['title']
                    item['activity_type'] = '培训'
                    item['activity_time'] = article.dd.string
                    item['url'] = origin_url + article.dt.a.attrs['href']
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.px_event_count = self.px_event_count + 1
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def yc_event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        origin_url = 'http://www.zjhzart.cn/'
        click_Xpath = '//*[@id="ContentPlaceHolder1_AspNetPager1"]/table/tbody/tr/td[2]/a[7]'
        driver.get(self.yc_event_url)
        while self.yc_event_count < self.yc_event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('div', {"class": "news_list"})
            for article in article_lists.find_all("dl"):
                item = CultureEventItem()
                try:
                    item['pav_name'] = '杭州文化馆'
                    item['activity_name'] = article.dt.a.attrs['title']
                    item['activity_type'] = '演出'
                    item['activity_time'] = article.dd.string
                    item['url'] = origin_url + article.dt.a.attrs['href']
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.yc_event_count = self.yc_event_count + 1
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def zl_event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        origin_url = 'http://www.zjhzart.cn/'
        click_Xpath = '//*[@id="ContentPlaceHolder1_AspNetPager1"]/table/tbody/tr/td[2]/a[7]'
        driver.get(self.zl_event_url)
        while self.zl_event_count < self.zl_event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('div', {"class": "news_list"})
            for article in article_lists.find_all("dl"):
                item = CultureEventItem()
                try:
                    item['pav_name'] = '杭州文化馆'
                    item['activity_name'] = article.dt.a.attrs['title']
                    item['activity_type'] = '展览'
                    item['activity_time'] = article.dd.string
                    item['url'] = origin_url + article.dt.a.attrs['href']
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.zl_event_count = self.zl_event_count + 1
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def jz_event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        origin_url = 'http://www.zjhzart.cn/'
        click_Xpath = '//*[@id="ContentPlaceHolder1_AspNetPager1"]/table/tbody/tr/td[2]/a[7]'
        driver.get(self.jz_event_url)
        while self.jz_event_count < self.jz_event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('div', {"class": "news_list"})
            for article in article_lists.find_all("dl"):
                item = CultureEventItem()
                try:
                    item['pav_name'] = '杭州文化馆'
                    item['activity_name'] = article.dt.a.attrs['title']
                    item['activity_type'] = '讲座'
                    item['activity_time'] = article.dd.string
                    item['url'] = origin_url + article.dt.a.attrs['href']
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.jz_event_count = self.jz_event_count + 1
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        html = soup.find('div', {'class': 'pxxz_detailed'})
        p_tags = html.find_all('p')
        contents = []
        try:
            item['source'] = str(soup.find('td', {'id': 'ContentPlaceHolder1_td_source'}).text).split('：')[1]
        except:
            item['source'] = ''
        try:
            item['click_number'] = re.findall(r'点击次数：(\d+)次', soup.find('dl', {'class': 'pxxz_head'}).text)[0]
        except:
            item['click_number'] = ''
        item['place'] = ''
        item['activity_introduction'] = ''
        item['presenter_introduction'] = ''
        item['organizer'] = ''
        item['presenter'] = ''
        item['age_limit'] = ''

        for p in p_tags:
            try:
                if re.findall(r'展览地点：(.+)', p.text)[0] and item['place'] == '':
                    item['place'] = str(re.findall(r'展览地点：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'展览介绍：(.+)', p.text)[0] and item['activity_introduction'] == '':
                    item['activity_introduction'] = str(re.findall(r'展览介绍：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'主办单位：(.+)', p.text)[0] and item['organizer'] == '':
                    item['organizer'] = str(re.findall(r'主办单位：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'展　　厅：(.+)', p.text)[0] and item['activity_introduction'] == '':
                    item['activity_introduction'] = str(re.findall(r'展　　厅：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'演出地点：(.+)', p.text)[0] and item['place'] == '':
                    item['place'] = str(re.findall(r'演出地点：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'场馆：(.+)', p.text)[0] and item['place'] == '':
                    item['place'] = str(re.findall(r'场馆：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'【相关介绍】(.+)', p.text)[0] and item['activity_introduction'] == '':
                    item['activity_introduction'] = str(re.findall(r'【相关介绍】(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'演出介绍(.+)', p.text)[0] and item['activity_introduction'] == '':
                    item['activity_introduction'] = str(re.findall(r'【相关介绍】(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'在(.+)上演', p.text)[0] and item['place'] == '':
                    item['place'] = str(re.findall(r'在(.+)上演', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'主办:(.+)', p.text)[0] and item['organizer'] == '':
                    item['organizer'] = str(re.findall(r'主办:(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'主　　办:(.+)', p.text)[0] and item['organizer'] == '':
                    item['organizer'] = str(re.findall(r'主　　办:(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'演出团体：(.+)', p.text)[0] and item['presenter'] == '':
                    item['presenter'] = str(re.findall(r'演出团体：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'主　　讲：(.+)', p.text)[0] and item['presenter'] == '':
                    item['presenter'] = str(re.findall(r'主　　讲：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'主讲嘉宾：(.+)', p.text)[0] and item['presenter'] == '':
                    item['presenter'] = str(re.findall(r'主讲嘉宾：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'主讲简介：(.+)', p.text)[0] and item['presenter_introduction'] == '':
                    item['presenter_introduction'] = str(re.findall(r'主讲简介：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'讲师简介：(.+)', p.text)[0] and item['presenter_introduction'] == '':
                    item['presenter_introduction'] = str(re.findall(r'讲师简介：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'主要内容：(.+)', p.text)[0] and item['activity_introduction'] == '':
                    item['activity_introduction'] = str(re.findall(r'主要内容：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'地点：(.+)', p.text)[0] and item['place'] == '':
                    item['place'] = str(re.findall(r'地点：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'活动地点：(.+)', p.text)[0] and item['place'] == '':
                    item['place'] = str(re.findall(r'活动地点：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'地　　点：(.+)', p.text)[0] and item['place'] == '':
                    item['place'] = str(re.findall(r'地　　点：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'讲座简介：(.+)', p.text)[0] and item['activity_introduction'] == '':
                    item['activity_introduction'] = str(re.findall(r'讲座简介：(.+)', p.text)[0]).strip()
            except:
                pass
            try:
                if re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', p.text)[0] and item['age_limit'] == '':
                    item['age_limit'] = re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', p.text)[0]
            except:
                pass
            try:
                if re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', p.text)[0] and item['age_limit'] == '':
                    item['age_limit'] = re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', p.text)[0]
            except:
                pass
            try:
                if re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', p.text)[0] and item['age_limit'] == '':
                    item['age_limit'] = re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', p.text)[0]
            except:
                pass
            contents.append(
                str(p.text).strip().replace('\u3000', '').replace('\n', '').replace('\r', '').replace('\xa0', ''))
        full_text = ''.join(contents)
        item['remark'] = full_text

        return item

# -*- coding: utf-8 -*-

import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class NingbolibSpider(scrapy.Spider):
    name = 'ningbolib'
    allowed_domains = ['nblib.cn']
    start_urls = ['http://nblib.cn/']

    selenium_path = 'D:\WorkSpace\Culture-Bigdata\cultureBigdata\chromedriver.exe'


    # 爬去机构介绍所需的参数
    intro_url = 'https://www.nblib.cn/col/col1950/index.html'

    # 爬去机构动态所需的参数
    news_url = 'https://www.nblib.cn/col/col1953/index.html###'
    news_count = 1
    news_page_end = 72
    # 爬去机构活动所需的参数
    event_url = 'https://www.nblib.cn/col/col2401/index.html'
    event_count = 1
    event_page_end = 39

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
        intro = str(soup.find('div', {'class': 's_content'}).text).strip()
        item['pav_name'] = '宁波市图书馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
        item['region'] = '宁波'
        item['area_number'] = '3.18万平方米'
        item['collection_number'] = '235万册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = '150余万人次'
        item['activity_number'] = '700'
        yield item

    def news_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        click_Xpath = '//*[@id="pagelist"]/a[1]'
        origin_url = 'https://www.nblib.cn'
        driver.get(self.news_url)
        while self.news_count < self.news_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find('td', {'id': "newslist"}).find_all('tr')
            for article in article_lists:
                item = CultureNewsItem()
                try:
                    item['pav_name'] = '宁波图书馆'
                    item['url'] = origin_url + article.find('a')['href']
                    item['time'] = article.find('span', {'class': 'bt_date'}).string
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
                except Exception as err:
                    print(err)
            self.news_count = self.news_count + 1
            if self.news_count > 2:
                click_Xpath = '//*[@id="pagelist"]/a[3]'
            driver.find_element_by_xpath(click_Xpath).click()
            time.sleep(1)
        driver.close()

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        try:
            item['title'] = soup.find('div',{'id':'ivs_title'}).text
        except:
            item['title'] = ''
        contents = soup.find("div", {"id": "zoom"}).find_all('p')
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['content'] = fulltext
        return item

    def event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)
        origin_url = 'https://www.nblib.cn'
        driver.get(self.event_url)
        click_Xpath = '//*[@id="6648"]/table/tbody/tr/td/table/tbody/tr/td[6]/div'
        while self.event_count < self.event_page_end:
            driver.implicitly_wait(3)
            true_page = driver.page_source
            soup = BeautifulSoup(true_page, 'html.parser')
            article_lists = soup.find_all('div', {'class': "a_list"})
            for article in article_lists:
                item = CultureEventItem()
                try:
                    item['pav_name'] = '宁波图书馆'
                    item['activity_type'] = '讲座'
                    item['activity_name'] = re.findall(r'《(.+)》', str(article.find('a').text))[0]
                    item['url'] = origin_url + article.find('a')['href']
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
        try:
            item['source'] = re.findall(r'信息来源：(.+)\u3000',soup.find('td',{'class':'append_info'}).text)[0]
        except:
            item['source'] = ''
        try:
            item['presenter'] = re.findall(r'主讲人：(.+)\n',soup.find('div',{'id':'zoom'}).text)[0]
        except:
            item['presenter'] = ''
        try:
            activity_time= re.findall(r'时\u3000间：(.+)\n',soup.find('div',{'id':'zoom'}).text)[0]
            item['activity_time'] = str(re.findall(r'\d{4}年\d{1,2}月\d{1,2}日',activity_time)[0]).replace('年','-').replace('月','-').replace('日','')
        except:
            item['activity_time'] = ''
        try:
            item['place'] = re.findall(r'地\u3000点：(.+)\n',soup.find('div',{'id':'zoom'}).text)[0]
        except:
            item['place'] = ''
        try:
            item['organizer'] = re.findall(r'主办单位：(.+)\n',soup.find('div',{'id':'zoom'}).text)[0]
        except:
            item['organizer'] = ''
        try:
            item['presenter_introduction'] = re.findall(r'主讲人简介：(.+)',soup.find('div',{'id':'zoom'}).text)[0]
        except:
            item['presenter_introduction'] = ''
        try:
            item['remark'] = soup.find('div',{'id':'zoom'}).text.replace('\xa0','').replace('\n','').replace('\u3000','')
        except:
            item['remark'] = ''
        return item



'''        
        content = soup.find('div', {"class", "xl_show"})
        full_text = str(content.text).replace('\u3000', '').replace('\xa0', '')
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\u3000', '').replace('\xa0', ''))
        # print(p_content)
        ########################################################################################
        item['remark'] = full_text.replace('\n', '')
        ########################################################################################
        # 活动地点 = place
        item['place'] = ''
        for i in range(len(p_content)):
            if '活动地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '活动地点' == p_content[i] or '五、培训地点:' == p_content[i]:
                item['place'] = p_content[i + 1]
                break
            elif '讲座地点：' in p_content[i]:
                index = p_content[i].index('讲座地点：')
                item['place'] = p_content[i][index:].split('：')[1]
                break
            elif '展览地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
        try:
            if re.findall(r'在(.*?)举办', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(.*?)举办', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'在(.*?)继续开讲', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(.*?)继续开讲', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'(.*?)将举办', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'，(.*?)将举办', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'活动地点是(.*?)。', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'活动地点是(.*?)。', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'在(济南市图书馆.{6})，', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(济南市图书馆.{6})，', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'，在(.*?)，', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'，在(.*?)，', content.text)[0]
        except:
            pass
        ########################################################################################
        item['activity_type'] = ''
        try:
            if '展览' in full_text:
                item['activity_type'] = '展览'
            elif '讲座' in full_text:
                item['activity_type'] = '讲座'
            elif '培训' in full_text:
                item['activity_type'] = '培训'
            elif '阅读' in full_text:
                item['activity_type'] = '阅读'
        except:
            pass
        ########################################################################################
        item['presenter'] = ''
        for i in range(len(p_content)):
            if '一、活动主讲人：' in p_content[i]:
                item['presenter'] = p_content[i + 1]
                break
            elif '主 讲 人：' in p_content[i]:
                item['presenter'] = p_content[i].split('：')[1]
                break
            elif '主讲人：' in p_content[i]:
                item['presenter'] = p_content[i].split('：')[1]
                break
        try:
            if re.findall(r'(...)老师', content.text)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)老师', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'(...)先生', content.text)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)先生', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'(...)姐姐', content.text)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)姐姐', content.text)[0]
        except:
            pass
        ########################################################################################
        item['organizer'] = ''
        for i in range(len(p_content)):
            if '主办单位：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            elif '举办单位：' == p_content[i] or '主办单位' == p_content[i]:
                item['organizer'] = p_content[i + 1]
                break
            elif '举办单位：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            elif '主 办：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            elif '举办：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
            # 举办

        ########################################################################################
        item['age_limit'] = ''
        try:
            if re.findall(r'不限年龄', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'不限年龄', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', content.text)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', content.text)[0]
        except:
            pass
        ########################################################################################
        item['presenter_introduction'] = ''
        for i in range(len(p_content)):
            if '作者简介：' == p_content[i] or '主讲人简介：' == p_content[i]:
                item['presenter_introduction'] = p_content[i + 1]
                break
            elif '讲师简介：' in p_content[i]:
                item['presenter_introduction'] = p_content[i].split("：")[1]
                break
        ########################################################################################
        item['contact'] = ''
        for i in range(len(p_content)):
            if '预约电话：' in p_content[i]:
                item['contact'] = p_content[i].split('：')[1]
                break
        try:
            if re.findall(r'\d{4}—\d{8}', content.text)[0] and item['age_limit'] == '':
                item['contact'] = re.findall(r'\d{4}—\d{8}', content.text)[0]
        except:
            pass
        try:
            if re.findall(r'\d{8}', content.text)[0] and item['age_limit'] == '':
                item['contact'] = re.findall(r'\d{8}', content.text)[0]
        except:
            pass
        ########################################################################################
        item['participation_number'] = ''
        ########################################################################################
        item['click_number'] = ''
        ########################################################################################
        item['source'] = ''
        ########################################################################################
        item['activity_introduction'] = ''
        ########################################################################################
        return item
'''
# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureEventItem, CultureNewsItem, CultureBasicItem
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

class Hunan_yongzhou_whySpider(scrapy.Spider):
    name = 'dongguan_whg'
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized");
    
    #allowed_domains = ['http://www.nmgbwy.com/']

    # 爬去机构介绍所需的参数
    #intro_url = 'http://www.nmgbwy.com/bwyjs.jhtml?contentId=147'


    selenium_path="C://Users/Zixin Zeng/AppData/Local/chromedriver.exe"
    # 爬去机构讲座活动所需的参数
    event_url = 'http://www.dgswhg.com/frontActivity/frontActivityList.do?type=1'


    event_count_1 = 1
    event_page_end_1 = 306



    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        #yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    def event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path)

        #click_Xpath="/html/body/form/div[2]/div[2]/div/div/div[2]/div[1]/span[1]/a[10]"
        driver.get(self.event_url)
        time.sleep(15)
        while self.event_count_1 < self.event_page_end_1:
            driver.implicitly_wait(10)
            data = driver.page_source
            soup = BeautifulSoup(data, 'html.parser')
            article_lists = soup.find('div', {'class': 'in-activity'})
            for article in article_lists.find_all('li'):
                item = CultureEventItem()
                try:
                    item['pav_name'] = '文化莞家'
                    item['url'] = 'http://www.dgswhg.com' + article.a.attrs['href']
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.event_count_1 = self.event_count_1 + 1
            a = driver.find_element_by_link_text("下一页>>")#翻页
            #driver.find_element_by_xpath(click_Xpath).click()
            a.click()
            if (self.event_count_1 == 70):#跳过有bug的页面
                a = driver.find_element_by_link_text("下一页>>")  # 翻页
                a.click()
            time.sleep(5)
        driver.close()





    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        title = soup.find('div', {'class': 'title'})
        item['activity_name'] = title.h1.text.replace('\n', '')
        infos = soup.find('div', {'class': 'address'})
        item['activity_time'] = (infos.find('p',{'class': 'time'}).text.replace('\n', '')[3:].strip()+' '+infos.find('p',{'class': 'traffic'}).text.replace('\n', '')[3:].strip())
        item['place'] = infos.find('p',{'class': 'site'}).text.replace('\n', '')[3:]
        item['contact'] = infos.find('p',{'class': 'phone'}).text.replace('\n', '')[3:]
        for help in infos.find_all('p',{'class': 'help'}):
            if help.text.strip()[0:3]=="主办方":
                item['organizer']=help.text.strip()[4:]
        content = soup.find('div', {'class': 'ad_intro'})
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            if p is not None:
                p_content.append(str(p.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t', '').replace('&nbsp;',''))
        text = ' '.join(p_content)
        item['remark'] = ' '.join(p_content)
        item['activity_type'] = ''
        try:
            if '展览' in p_content:
                item['activity_type'] = '展览'
            elif '讲座' in p_content:
                item['activity_type'] = '讲座'
            elif '培训' in p_content:
                item['activity_type'] = '培训'
            elif '阅读' in p_content:
                item['activity_type'] = '阅读'
            elif '比赛' in p_content:
                item['activity_type'] = '比赛'
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
        return item

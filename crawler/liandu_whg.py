# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureEventItem, CultureNewsItem, CultureBasicItem
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import time

###未完成
class Hunan_yongzhou_whySpider(scrapy.Spider):
    name = 'liandu_whg'


    # allowed_domains = ['http://www.nmgbwy.com/']

    # 爬去机构介绍所需的参数
    # intro_url = 'http://www.nmgbwy.com/bwyjs.jhtml?contentId=147'

    selenium_path = "C://Users/Zixin Zeng/AppData/Local/chromedriver.exe"
    # 爬去机构讲座活动所需的参数
    event_url = 'http://www.ldwhg.cn/ld/act'
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized");
    desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
    desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出
    start_page=1
    end_page=7

    def start_requests(self):
        # 请求机构介绍信息
        # yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        # yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        # yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    def event_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path, chrome_options=self.chrome_options)
        driver.get(self.event_url)
        while self.start_page<=self.end_page:
            data = driver.page_source
            soup = BeautifulSoup(data, 'html.parser')
            # print(soup.prettify())
            article_lists = soup.find_all('li', {'class': 'kada-list-li-four'})
            len=length(article_lists)
            for i in range(len):
                item = CultureEventItem()
                try:
                    item['pav_name'] = '莲都区数字文化馆'
                    item['url'] = 'http://www.fcgqyg.cn/' + article.find_all('div',{'class':'img'})[0].a.attrs['href'][1:]
                    #item['activity_type']=article.find_all('span',{'class':'span2'})[0].text
                    yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                except Exception as err:
                    print(err)
            self.start_page+=1
            a = driver.find_element_by_link_text("下一页")  # 翻页
            a.click()
        time.sleep(5)
        driver.close()

    def event_text_parse(self, response):
        driver = webdriver.Chrome(self.selenium_path, chrome_options=self.chrome_options)
        item = response.meta['item']
        driver.get(item['url'])
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        infobox = soup.find_all('div', {'class': 'list-item-mess'})[0]
        item['activity_name'] = infobox.find_all('div', {'class': 'title-tag'})[0].h3.text.strip()
        types = infobox.find_all('div', {'class': 'title-tag'})[0].find_all('span', {'class': 'act-tag'})
        type_list = []
        for type in types:
            type_list.append(type.text.strip())
        item['activity_type'] = ' '.join(type_list)
        taglist = infobox.find_all('div', {"class": 'info-tag'})[0]
        tags = taglist.find_all('p')
        for tag in tags:
            if tag.text[0:4] == "活动时间":
                item['activity_time'] = tag.span.text.strip().replace('\xa0', '')
            elif tag.text[0:4] == "活动地点":
                item['place'] = tag.span.text.strip()
                if item['place'][-4:] == "查看地图":
                    item['place'] = item['place'][:-4]
            elif tag.text[0:4] == "联系方式":
                item['contact'] = tag.span.text.strip()
        content = soup.find_all('div', {'class': 'booking-notice'})  # 分为简介和详情
        p_tags = content[1].find_all('p')  # 详情
        p_content = []
        p_content.append(content[0].text.strip())
        for p in p_tags:
            if p is not None:
                if p.find('span') is not None:
                    p_content.append(
                        str(p.span.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t',
                                                                                                             '').replace(
                            '&nbsp;', ''))
                else:
                    p_content.append(
                        str(p.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t',
                                                                                                        '').replace(
                            '&nbsp;', ''))
        text = ''.join(p_content)
        item['remark'] = ' '.join(p_content)
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
        driver.close()
        return item

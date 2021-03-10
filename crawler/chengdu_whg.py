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
    name = 'chengdu_whg'
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized");

    # allowed_domains = ['http://www.nmgbwy.com/']

    # 爬去机构介绍所需的参数
    # intro_url = 'http://www.nmgbwy.com/bwyjs.jhtml?contentId=147'

    selenium_path = "C://Users/Zixin Zeng/AppData/Local/chromedriver.exe"
    # 爬去机构讲座活动所需的参数
    event_url = 'http://www.cdsszwhg.com/list-active.html?aid=b3b17b5e6e974bd8a0dcc1df7c0bd826'



    def start_requests(self):
        # 请求机构介绍信息
        # yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        # yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        # yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    def event_parse(self, response):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized");
        driver = webdriver.Chrome("C://Users/Zixin Zeng/AppData/Local/chromedriver.exe", chrome_options=chrome_options)
        driver = webdriver.Chrome(self.selenium_path)


        driver.get(self.event_url)
        time.sleep(10)
        for i in range(0, 100):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            i += 1
            time.sleep(1.5)
        driver.implicitly_wait(10)
        data = driver.page_source
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find_all('div', {'class': 'hdBox'})
        for article in article_lists:
            item = CultureEventItem()
            try:
                item['pav_name'] = '文化天府'
                item['url'] = 'http://www.cdsszwhg.com/' + article.a.attrs['href'][1:]
                print("DEBUG:url",item['url'])
                item['activity_type']=article.find_all('span',{'class':'span2'})[0].text
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        time.sleep(5)
        driver.close()

    def event_text_parse(self, response):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized");
            driver = webdriver.Chrome("C://Users/Zixin Zeng/AppData/Local/chromedriver.exe", chrome_options=chrome_options)
            item = response.meta['item']
            driver.get(item['url'])
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.close()
            top = soup.find('div', {'class': 'topBox'})
            top2=top.find_all('div',{'class':'col-xs-6'})
            item['activity_name'] = top2[0].h4.text.strip()
            infos = top2[1].find_all('p')
            item['activity_time'] = infos[2].text.strip()[5:]
            item['place'] = infos[0].text.strip()
            item['contact'] = infos[3].text.strip()[5:]

            content = soup.find('div', {'class': 'content'})
            p_tags = content.find_all('p')
            p_content = []
            for p in p_tags:
                if p is not None:
                    if p.find('span')is not None:
                        p_content.append(str(p.span.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t', '').replace('&nbsp;', ''))
                    else:
                        p_content.append(str(p.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t','').replace('&nbsp;', ''))
            text = ' '.join(p_content)
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
        except Exception as err:
            print(err)
        ########################################################################################
        return item

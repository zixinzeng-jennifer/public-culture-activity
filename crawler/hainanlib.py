# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class HainanSpider(scrapy.Spider):
    name = 'hainanlib'
    allowed_domains = ['hilib.com']
    start_urls = ['http://www.hilib.com/']


    # 爬去机构动态所需的参数
    news_url = 'http://www.zslib.com.cn/TempletPage/List.aspx?dbid=2&page=1'
    news_base_url = 'http://www.zslib.com.cn/TempletPage/List.aspx?dbid=2&page='
    news_count = 1
    news_page_end = 221

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.jnlib.net.cn/gyjt/201311/t20131105_2257.html'

    # 爬去机构活动所需的参数


    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        for i in range(1,1005):
            page = (i-1)
            url = 'http://action.hilib.com:8089/action/web/index.do?offset=' + str(page)
            yield scrapy.Request(url, callback=self.event_parse)
        # 请求机构活动信息
        #yield scrapy.Request(self.event_url, callback=self.event_parse)
        

    '''
    def news_parse(self, response):
        origin_url = 'http://www.zslib.com.cn/TempletPage/List.aspx?dbid=2&page=1'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', {"class": "gl_list"})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '广东省立中山图书馆'
                item['title'] = article.a.string
                item['url'] = origin_url + article.a.attrs['href'][2:]
                item['time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.span.string)[0]
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
        content = soup.find("div", {"class": "xl_show"})
        item['content'] = str(content.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item

    '''
    def event_parse(self, response):

        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_all = soup.find_all('div', {'class': 'fl_lf hdzx_div'})

        for event in event_all:
            item = CultureEventItem()
            list1 =event.find('div',{'class':'hdzx_txt'}).text.split('\n')
            try:
                item['pav_name'] = '海南省图书馆'
                item['activity_name'] = list1[0].replace('\r','').replace(' ','')
                item['place'] = list1[2].replace('\r','').replace(' ','')
                item['url'] = 'http://action.hilib.com:8089/action/web/' + event.a.attrs['href']
                item['remark'] = event.find('div',{'class':'hdzx_layer_2'}).text.replace('&nbsp;', '').replace('\n', '').replace('\r', '').replace('\xa0', '')
                item['organizer'] = '海南省图书馆'
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
                break
            except Exception as err:
                print(err)

    
    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find_all('td', {'height': '25'})
        item['activity_time'] = content[2].text[6:16]
        print(item['activity_time'])
        return item

        '''
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
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
    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {"class": 'TRS_Editor'}).text).strip()
        item['pav_name'] = '海南省图书馆'
        item['pav_introduction'] = intro.replace('\u3000\u3000', '')
        item['region'] = '海南'
        item['area_number'] = '2.5万平方米'
        item['collection_number'] = '164万余册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = '17万'
        item['activity_number'] = ''
        yield item

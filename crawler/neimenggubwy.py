# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureEventItem, CultureNewsItem, CultureBasicItem
import re


class NeimenggubwySpider(scrapy.Spider):
    name = 'neimenggubwy'
    #allowed_domains = ['http://www.nmgbwy.com/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.nmgbwy.com/bwyjs.jhtml?contentId=147'



    # 爬去机构讲座活动所需的参数
    event_url = 'http://www.nmgbwy.com/jqhd/index.jhtml?contentId=173'
    event_base_url = 'http://www.nmgbwy.com/jqhd/index.jhtml?contentId='
    event_base_url_1 = 'http://www.nmgbwy.com/jqhd/index'
    event_base_url_2 = '.jhtml?contentId=173'

    event_count_1 = 1
    event_page_end_1 = 13



    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)
        #yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    def event_parse(self, response):
        #original_url = 'http://www.nmglib.com/ntzx/ntdt/'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', {'class': 'container-fluid'})
        #print("AAAAA______________:",article_lists)
        if article_lists:
            #print("BBBBBB_____________")
            LI = article_lists.find_all('li')
            if LI:
                print()
        for article in article_lists.find_all('div', {'style': 'height:150px;  margin-top: 10px;margin-left: 5px;'}):
            #print("AAAAA______________:",article)
            item = CultureEventItem()
            try:
                item['pav_name'] = '内蒙古博物院'
                item['activity_name'] = article.a.string
                print(item['activity_name'])
                item['url'] = article.a.attrs['href']
                item['activity_time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.find('div', {'style': 'margin-top:10px;   color: #9F9F9F '}).text)[0]
                #print("???____________________???")
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count_1 < self.event_page_end_1:
            self.event_count_1 = self.event_count_1 + 1
            yield scrapy.Request(self.event_base_url_1 + "_"+ str(self.event_count_1) + self.event_base_url_2  + '.html', callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {'style': 'margin:33px;text-align:left;'})
        p_tags = content.find_all('p')

        p_content = []
        for p in p_tags:
            p_tag1 = p.find_all('p')
            for m in p_tag1:
                if m is not None:

                    p_content.append(str(m.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t', '').replace('&nbsp;',''))
        text = ' '.join(p_content)
        item['remark'] = ''.join(p_content)
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
            if re.findall(r'在(内蒙古博物院.{6})，', content.text)[0] and item['place'] == '':
                item['place'] = re.findall(r'在(内蒙古博物院.{6})，', content.text)[0]


        except:
            pass
        ########################################################################################
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

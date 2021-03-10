# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time


class XiZangSpider(scrapy.Spider):
    name = 'xizanglib'
    allowed_domains = ['tdcn.org.cn']

    # 爬去机构动态所需的参数
    news_url = 'http://www.tdcn.org.cn/site/lib/articleList.do?curChannelId=773'
    news_base_url = 'http://www.tdcn.org.cn/site/lib/articleList.do?cpage='
    news_count = 1
    news_page_end = 3

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.tdcn.org.cn/site/lib/article.do?articleId=2974&curChannelId=381'

    # 爬去机构活动所需的参数
    event_url = 'http://www.sxlib.org.cn/hd/hdyg/qb/'
    event_base_url = 'http://www.sxlib.org.cn/hd/hdyg/qb/index_'
    event_count = 1
    event_page_end = 4

    def start_requests(self):
        # 请求机构介绍信息
        yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.event_url, callback=self.event_parse)

    def news_parse(self, response):
        origin_url = 'http://www.tdcn.org.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        #print(soup)
        article_lists = soup.find('div', {"class": 'culturl_list'})
        #print(article_lists)
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '西藏自治区图书馆'
                item['title'] = article.h3.a.string
                item['url'] = origin_url + article.a['href']
                item['time'] = re.findall(r'\d{4}-\d{2}-\d{2}',article.h4.string)[0]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '&curChannelId=773', callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        content = soup.find("div", {"class": "detail_content"})
        p_tags = content.find_all('p')
        full_text = ''
        for p in p_tags:
            full_text = full_text + str(p.text)
        item['content'] = full_text.replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item


    def event_parse(self, response):
        origin_url = 'http://www.sxlib.org.cn/hd/hdyg'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('ul', {'id': 'zebra'})
        for event in event_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '陕西省图书馆'
                item['activity_name'] = event.a.string.replace('\n','').strip()
                item['activity_type'] = re.findall(r'(.{2})】',event.a.string)[0]
                item['activity_time'] = event.span.string.strip()
                item['url'] = origin_url + event.a['href'][2:].strip()
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)
        if self.event_count < self.event_page_end:
            self.event_count = self.event_count + 1
            yield scrapy.Request(self.event_base_url+str(self.event_count) + '.html',callback=self.event_parse)
        else:
            return None

    def event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        content = soup.find('div', {"class", "TRS_Editor"})
        full_text = str(content.text).strip().replace('\xa0', '').replace('\u3000', '')
        p_tags = content.find_all('p')
        p_content = []
        for p in p_tags:
            p_content.append(str(p.text).replace('\xa0', '').replace('\u3000', ''))
        # print(p_content)
        ########################################################################################
        item['remark'] = full_text .replace('\xa0','').replace('\n', '')
        ########################################################################################
        # 活动地点 = place
        item['place'] = ''
        for i in range(len(p_content)):
            if '地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '地   点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '活动地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
            elif '展览地点：' in p_content[i]:
                item['place'] = p_content[i].split('：')[1]
                break
        ########################################################################################

        item['presenter'] = ''
        for i in range(len(p_content)):
            if '主讲人：' in p_content[i]:
                item['presenter'] = p_content[i].split('：')[1]
                break
            elif '分享嘉宾：' in p_content[i]:
                name_intro = p_content[i].split('：')[1]
                item['presenter'] = re.findall(r'(.*)，',full_text)[0]
                break
        ########################################################################################
        item['organizer'] = ''
        for i in range(len(p_content)):
            if '主办：' in p_content[i]:
                item['organizer'] = p_content[i].split('：')[1]
                break
        ########################################################################################
        item['presenter_introduction'] = ''
        try:
            if re.findall(r'【主讲人简介】：  ((\s)*.*)'):
                item['presenter_introduction'] = re.findall(r'【主讲人简介】：  ((\s)*.*)',full_text)[0]
            elif '分享嘉宾：' in p_content[i]:
                name_intro = p_content[i].split('：')[1]
                name = re.findall(r'(.*)，',full_text)[0]
                item['presenter_introduction'] = name_intro[len(name_intro)-len(name)-1:]
        except:
            pass
        ########################################################################################
        item['contact'] = ''
               ########################################################################################
        item['participation_number'] = ''
                ########################################################################################
        item['activity_introduction'] = ''
        ########################################################################################
        return item

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        item['pav_name'] = '西藏自治区图书馆'
        item['pav_introduction'] = '西藏图书馆是自治区“八五”重点建设项目之一， 1991年动工修建，1996年正式开馆，建筑部面积17534平方米，工程总投资为1843万元。目前馆内设有采编部（下设藏编部和汉编部）、典藏部、阅览部等业务部门及少儿阅览室、港台外文阅览室、电子阅览室、期刊阅览室、藏文阅览室、开架外借室。2003年和2008年根据上级安排及事业发展的需要，设立了全国文化信息资源共享工程西藏自治区分中心和西藏古籍保护中心。目前我馆藏书量36余万册、报刊杂志1000余种、少儿读物（含报刊）3万余种。电子资源有地方特色资源“八大藏戏”、“西藏藏北赛马文化”专题资源库、电子图书、各类讲座、文艺、少儿节目等视频供读者查阅。以藏文图书作为特色馆藏的藏文古籍达15000余函、10万余件，这些图书大多为木刻版，部分用金、银、玛瑙等各种矿物质手写而成，具有极高的文献、文物、艺术价值，其中包括2007年入选《国家珍贵古籍名录》的元抄本《因明正解藏论》和明抄本《苯教经咒集要》。2002年被文化部评为“全国读者喜爱的图书馆”、2006年被区直工委评为“先进基层党组织”、2007年被中华全国妇女联合会评为“巾帼文明岗”，并多次被评为文化厅系统先进集体。'
        item['region'] = '西藏'
        item['area_number'] = '17534平方米'
        item['collection_number'] = '36余万册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class ChongqinglibSpider(scrapy.Spider):
    name = 'chongqinglib'
    allowed_domains = ['cqlib.cn']
    start_urls = ['http://cqlib.cn/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.cqlib.cn/?q=node/27'

    # 爬去机构动态所需的参数
    news_url = 'http://www.cqlib.cn/?q=-notice'
    news_base_url = 'http://www.cqlib.cn/?q=-notice&page='
    news_count = 1
    news_page_end = 86

    # 爬去机构活动所需的参数
    jz_event_url = 'http://www.cqlib.cn/?q=120'#http://www.cqlib.cn/?q=lecture'
    jz_event_base_url = 'http://www.cqlib.cn/?q=120&page='#'http://www.cqlib.cn/?q=lecture&page='
    jz_event_count = 1
    jz_event_page_end = 7

    zl_event_url='http://www.cqlib.cn/?q=92'
    zl_event_base_url='http://www.cqlib.cn/?q=92&page='
    zl_event_count=1
    zl_event_page_end=3

    def start_requests(self):

        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)
        yield scrapy.Request(self.zl_event_url,callback=self.zl_event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {'class': 'field-items'}).text).strip()
        item['pav_name'] = '重庆图书馆'
        item['pav_introduction'] = intro.replace('\u3000', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
        item['region'] = '重庆'
        item['area_number'] = '5万余平方米'
        item['collection_number'] = '460多万册'
        item['branch_number'] = ''
        item['librarian_number'] = '240余人'
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.cqlib.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('ul', {"class": "detail-ul"})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '重庆图书馆'
                item['title'] = str(article.div.a.string).strip()
                item['url'] = origin_url + article.div.a.attrs['href']
                item['time'] = article.span.string
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count - 1), callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        item['time'] = soup.find('span', {'class': 'release-time'}).text
        contents = soup.find("div", {"class": "field-items"}).find_all('p')
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['content'] = fulltext
        return item

    def rule_match(self, rule_id, text):
        text = str(text)
        if rule_id == 'activity_type':
            if ('展览' or '艺术展') in text:
                result = '展览'
            elif '讲座' in text:
                result = '讲座'
            elif '培训' in text:
                result = '培训'
            elif '阅读' in text:
                result = '阅读'
            elif ('比赛' or '大赛') in text:
                result = '比赛'
            elif ('放映' or '电影') in text:
                result = '电影'
            else:
                result = ''
        elif rule_id == 'place':
            try:
                result = re.findall(r'地点：(.+)\n', text)[0]
            except:
                result = ''
        elif rule_id == 'activity_time':
            try:
                result = re.findall(r'时间：(.+)\n', text)[0]
            except:
                result = ''
        elif rule_id == 'presenter':
            try:
                result = re.findall(r'主\xa0讲\xa0人：(.{2,30})\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'主讲人：(.{2,30})\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'主 讲 人：(.{2,30})\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'领读人：(.{2,30})\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'讲师：(.{2,30})\n', text)[0]
                except:
                    result = ''
        elif rule_id == 'organizer':
            try:
                result = re.findall(r'主办单位：(.{3,30})\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'主办：(.{3,30})\n', text)[0]
                except:
                    result = ''

        elif rule_id == 'age_limit':
            try:
                result = re.findall(r'(\d{1,2}岁至\d{1,2}岁)', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'(\d{1,2}岁-\d{1,2}岁)', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'(\d{1,2}-\d{1,2}岁)', text)[0]
                except:
                    result = ''

        elif rule_id == 'participation_number':
            try:
                result = re.findall(r'(\d{1,4})名', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'(\d{1,4})余人', text)[0]
                except:
                    result = ''
        elif rule_id == 'contact':
            try:
                result = re.findall(r'咨询电话：(.{8,20})\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'电话：(.{8,15})\n', text)[0]
                except:
                    pass
        elif rule_id == 'presenter_introduction':
            try:
                result = re.findall(r'主讲人简介：\n(.+)。\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'导读人简介：\n(.+)\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'嘉宾：(.+)\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'讲师：(.+})\n', text)[0]
                except:
                    result = ''
        elif rule_id == 'activity_introduction':
            try:
                result = re.findall(r'内容介绍：\xa0\n(.+)。\n', text)[0]
            except:
                result = ''
            if result == '':
                try:
                    result = re.findall(r'讲座内容：\n\xa0\n(.+)\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'讲座内容：\n(.+)。\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'内容简介：\xa0\n(.+)。\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'内容：(.+)\n', text)[0]
                except:
                    result = ''
            if result == '':
                try:
                    result = re.findall(r'内容介绍：(.+)。\n', text)[0]
                except:
                    result = ''
        return result

    def jz_event_parse(self, response):
        origin_url = 'http://www.cqlib.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        #print(soup.prettify())
        for event in soup.find_all('div',{'class':'main-box-content-item'}):
            print("found items")
            item = CultureEventItem()
            try:
                info=event.find('div',{'class':'item-txt'})
                item['pav_name'] = '重庆图书馆'
                item['url'] = origin_url + info.find('span',{'class':'lectureTitle'}).a['href']
                item['activity_type'] = '讲座'
                item['organizer'] = '重庆图书馆'
                item['activity_name']=info.find('span',{'class':'lectureTitle'}).text.strip()
                item['activity_time']=info.find('span',{'class':'lectureDate'}).text.strip()[3:]
                item['presenter']=info.find('span',{'class':'lecturePerson'}).text.strip()[3:]
                item['remark']=info.find('span',{'class':'lectureDesc'}).text.strip()[3:]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.jz_event_text_parse)
            except Exception as err:
                print(err)
        if self.jz_event_count < self.jz_event_page_end:
            self.jz_event_count = self.jz_event_count + 1
            yield scrapy.Request(self.jz_event_base_url + str(self.jz_event_count), callback=self.jz_event_parse)


    def jz_event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            item['presenter_introduction']=soup.find('span',{'class':'body-description-right'}).text.strip().replace('\xa0','').replace('\u3000','').replace('\n','')
        except:
            item['presenter_introduction']=''
        """
        item['activity_time'] = soup.find('span', {'class': 'release-time'}).text
        item['place'] = soup.find('div', {'class': 'field field-name-field-address field-type-text field-label-above'})\
            .find('div', {'class': 'field-item even'}).text
        texts = soup.find('div',{'class':'field-item even'}).find_all('p')
        content = []
        for text in texts:
            content.append(text.text)
        item['remark'] = ''.join(content)
        fulltext=''.join(content)
        try:
            item['presenter'] = re.findall(r'主讲人：(.{2,10})\xa0\xa0\xa0', fulltext)[0]
        except:
            try:
                item['presenter'] = re.findall(r'主讲人：(.{2,10})\u3000\u3000', fulltext)[0]
            except:
                item['presenter'] = ''
        try:
            item['presenter_introduction'] = re.findall(r'\xa0\xa0\xa0(.+)', fulltext)[0]
        except:
            item['presenter_introduction'] = ''
        """
        return item

    def zl_event_parse(self,response):
        origin_url = 'http://www.cqlib.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')

        for event in soup.find_all('div',{'class':'main-box-content-item'}):
            item = CultureEventItem()
            try:
                info = event.find('div', {'class': 'item-txt'})
                item['pav_name'] = '重庆图书馆'
                item['url'] = origin_url + info.find('span', {'class': 'lectureTitle'}).a['href']
                item['activity_type'] = '展览'
                item['organizer'] = '重庆图书馆'
                item['activity_name'] = info.find('span', {'class': 'lectureTitle'}).text.strip()
                item['activity_time'] = info.find('span', {'class': 'lectureDate'}).text.strip()[5:]
                item['organizer'] = info.find('span', {'class': 'lecturePerson'}).text.strip()[5:]
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.zl_event_text_parse)
            except Exception as err:
                print(err)
        if self.zl_event_count < self.zl_event_page_end:
            self.zl_event_count = self.zl_event_count + 1
            yield scrapy.Request(self.zl_event_base_url + str(self.zl_event_count), callback=self.zl_event_parse)


    def zl_event_text_parse(self,response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            item['remark'] = soup.find('span',
                                                       {'class': 'body-description-right'}).text.strip().replace('\xa0',
                                                                                                                 '').replace(
                '\u3000', '').replace('\n', '')+soup.find('div',{'class':'body-content'}.text.strip().replace('\xa0',
                                                                                                                 '').replace(
                '\u3000', '').replace('\n', ''))
        except:
            item['remark'] = ''
        return item
# item = CultureEventItem()


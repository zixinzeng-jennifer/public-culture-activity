# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
import re


class WuhanlibSpider(scrapy.Spider):
    name = 'wuhanlib'
    allowed_domains = ['whlib.org.cn']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.whlib.org.cn/node/466.jspx'

    # 爬去机构动态所需的参数
    news_url = 'http://www.whlib.org.cn/node/425.jspx'
    news_base_url = 'http://www.whlib.org.cn/node/425_'
    news_count = 1
    news_page_end = 28

    # 爬去机构活动所需的参数
    jz_event_url = 'http://jz.whlib.org.cn/webs/cata_cataNews.action?cataPage=notice&cataid=53&title=&beginTime=&endTime=&tag=2&pag=1'
    jz_event_base_url = 'http://jz.whlib.org.cn/webs/cata_cataNews.action?cataPage=notice&cataid=53&title=&beginTime=&endTime=&tag=2&pag='
    jz_event_count = 1
    jz_event_page_end = 51

    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.jz_event_url, meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                            callback=self.jz_event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        contents = soup.find('div', {'class': 'art'}).find_all('p')
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['pav_name'] = '武汉图书馆'
        item['pav_introduction'] = fulltext
        item['region'] = '武汉'
        item['area_number'] = ''
        item['collection_number'] = '310万册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        origin_url = 'http://www.whlib.org.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', {"class": "newsList"})
        # print(article_lists)
        for article in article_lists.find_all("li"):
            # print(article)
            item = CultureNewsItem()
            try:
                item['pav_name'] = '武汉图书馆'
                item['title'] = re.findall(r'\d、(.+)', article.a.text)[0]
                item['url'] = origin_url + article.a.attrs['href']
                item['time'] = article.find('span', {'class': 'time'}).text
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '.jspx', callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        contents = soup.find("div", {"class": "art"}).find_all('p')
        text = []
        for content in contents:
            neirong = str(content.text).strip().replace('\u3000', '').replace('\r', '').replace('\n', '').replace(
                '\xa0', '').replace('\t', '')
            text.append(neirong)
        fulltext = ''.join(text)
        item['content'] = fulltext
        return item

    def jz_event_parse(self, response):
        origin_url = 'http://jz.whlib.org.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        event_lists = soup.find('table')
        for event in event_lists.find_all('tr', {'align': 'center'}):
            item = CultureEventItem()
            try:
                item['pav_name'] = '武汉图书馆'
                item['activity_name'] = str(event.find('td', {'align': 'left'}).a.text).strip()
                item['url'] = origin_url + event.find('td', {'align': 'left'}).a['href']
                item['presenter'] = event.find('td', {'width': '59'}).text
                item['activity_type'] = '讲座'
                item['activity_time'] = str(event.find('td', {'width': '109'}).text).strip()
                yield scrapy.Request(item['url'], meta={'item': item,'dont_redirect': True, 'handle_httpstatus_list': [302]}, callback=self.jz_event_text_parse)
            except Exception as err:
                print(err)
        if self.jz_event_count < self.jz_event_page_end:
            self.jz_event_count = self.jz_event_count + 1
            yield scrapy.Request(self.jz_event_base_url + str(self.jz_event_count),
                                 meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                       callback=self.jz_event_parse)
        else:
            return None

    def jz_event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            content = soup.find('span', {"style": "font-family:宋体;font-size:14pt;font-weight:normal;"})
            full_text = str(content.text).strip().replace('\u3000', '').replace('\xa0', '')
            item['presenter_introduction'] = full_text
        except:
            item['presenter_introduction'] = ''
        return item

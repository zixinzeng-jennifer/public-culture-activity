# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
import re
import time
import json
import ast


class ShanghaiSpider(scrapy.Spider):
    name = 'shanghaiwhy'

    allowed_domains=['www.whjd.sh.cn']
    # 爬去机构动态所需的参数
    news_url = ''
    news_base_url = ''
    news_count = 1
    news_page_end = 4

    # 爬去机构介绍所需的参数
    intro_url = ''

    # 爬去机构活动所需的参数
    event_url = ''
    event_count=0

    def start_requests(self):

        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        #yield scrapy.Request(self.event_url, callback=self.event_parse)
        for i in range(1, 1196):
            url = 'http://www.whjd.sh.cn/frontIndex/activityQueryList.do'
            headers = {'Host': 'www.whjd.sh.cn',
                       'Origin':'http://www.whjd.sh.cn',
                       'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                       'Referer': 'http://www.whjd.sh.cn/frontActivity/activityList.do',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
                       'Accept': 'application/json, text/javascript, */*; q=0.01',
                       'Connection': 'keep-alive',
                       'Accept - Encoding': 'gzip, deflate, br',
                       'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                       'X-Requested-With':'XMLHttpRequest',
                       #'Content-Length':'117',
                       #'Cookie':'JSESSIONID=0058AB27EA1D909EB1058D4734DE247E; Hm_lvt_522dc691323a30767cdac92bab378b53=1613406618; Hm_lvt_eec797acd6a9a249946ec421c96aafeb=1613406627; Hm_lpvt_eec797acd6a9a249946ec421c96aafeb=1613406779; acw_tc=2f61f26516134534775904223e0c5186965e96f361adb7def78dd014a5c85e; Hm_lpvt_522dc691323a30767cdac92bab378b53=1613453517'
                       }
            myFormData = {
                        'sortType':'8',
                        'page': str(i),
                        'activityArea': '57'
                        }
            print(myFormData)
            time.sleep(5)
            print("-----------第" + str(i) + "页-----------")

            yield scrapy.FormRequest(url,
                                     headers = headers,
                                     method='POST',  # GET or POST
                                     formdata = myFormData,       # 表单提交的数据
                                     callback=self.event_parse,
                                     dont_filter=True)

    def news_parse(self, response):
        pass
        origin_url = ''
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('ul', {"id": 'zebra'})
        for article in article_lists.find_all("li"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = ''
                item['title'] = article.a.string
                item['url'] = origin_url + article.a['href']
                item['time'] = article.span.string
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '.html', callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        pass
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, "html.parser")
        content = soup.find("div", {"class": "TRS_Editor"})
        item['content'] = str(content.text).replace('\u3000', '').replace('\xa0', '').replace('\n', '')
        return item


    def event_parse(self, response):
        data=response.body
        content=ast.literal_eval(data.decode('utf8'))
        file=open('test.txt','w',encoding='utf8')
        file.write(content)
        file.close()
        file=open("test.txt",'r',encoding='utf8')
        my_text=''
        for line in file.readlines():
            my_text+=line.strip()
        content=json.loads(my_text)
        file.close()
        self.event_count+=1
        print("page:",self.event_count)
        print("DEBUG:",type(content))
        for event in content['list']:
            item=CultureEventItem()
            try:
                item['pav_name']='上海市文化嘉定云'
                item['activity_name']=event['activityName'].strip()
                item['place']=event['activityAddress'].strip()
                item['activity_time']=event['activityEndTime'].strip()
                item['url']='http://www.whjd.sh.cn/frontActivity/frontActivityDetail.do?activityId='+event['activityId']
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)





    def event_text_parse(self, response):
        item=response.meta['item']
        soup=BeautifulSoup(response.body,'html.parser')
        try:
            p_tags=soup.find('div',{'class':'extra'}).find_all('p')
            for p in p_tags:
                content=p.text.strip().replace('\n','').replace('\u3000','').replace('\xa0','')
                if content[:5]=='主办单位：':
                    item['organizer']=(content[5:]).strip()
        except Exception as err:
            print(err)
        item['remark']=soup.find('div',{'class':'ad_intro'}).text.strip().replace('\n','').replace('\u3000','').replace('\xa0','')
        return item
        """
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
        """

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        intro = str(soup.find('div', {"class": 'TRS_Editor'}).text).strip()
        item['pav_name'] = '陕西省图书馆'
        item['pav_introduction'] = intro .replace('\xa0','').replace('\u3000\u3000', '')
        item['region'] = '陕西'
        item['area_number'] = '4.7万平方米'
        item['collection_number'] = '525万余册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

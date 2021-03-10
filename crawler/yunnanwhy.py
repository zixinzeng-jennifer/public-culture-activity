# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time

import os
import codecs
import json
import sys

#最新爬取时间：2021年1月27日
#最新活动记录：https://www.ynggwhy.cn/activity/detail/1341934930519281664
'''
GET /api-web/web/app/ccActivity/app_pass/dataPage?pageSize=8&pageNum=1&orderType=0&type=&systemFlag=0&_t=1611752173003 HTTP/1.1
Host: www.ynggwhy.cn
Connection: keep-alive
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://www.ynggwhy.cn/activity
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Cookie: hbAppId=hbY3dGDs5jDBxn6RTX; dataAppId=daKkDxc2MW42rSwAEZ; districtCode=530000; ip=223.73.220.97; venueNum=




'''






class YunnanwhySpider(scrapy.Spider):
    name = 'yunnanwhy'
    #allowed_domains = ['jlsdmu.com/']
    selenium_path = 'C://Users/Zixin Zeng/AppData/Local/chromedriver.exe'
    #chrome_options=Options()
    #driver=webdriver.Chrome(selenium_path, options=chrome_options)
    def start_requests(self):
        for i in range(1,43):

            #formdata = {"currentPage":str(i)}
            url = 'https://www.ynggwhy.cn/api-web/web/app/ccActivity/app_pass/dataPage?pageSize=8&pageNum='+str(i)+'&orderType=0&type=&systemFlag=0'
            driver.get(url)
            data=driver.page_source

            headers = {'Host': 'www.ynggwhy.cn',
            'Referer': 'https://www.ynggwhy.cn/activity',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Accept':'application/json, text/plain, */*',
            'Connetion':'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            #'cookie':'hbAppId=hbY3dGDs5jDBxn6RTX; dataAppId=daKkDxc2MW42rSwAEZ; districtCode=530000; ip=223.73.220.97;venueNum='
            }
            myFormData = {'pageSize': '8',
            'orderType': '0',
            'pageNum': str(i),
            'type': '',
            'systemFlag': '0',}

            print("-----------第"+str(i)+"页-----------")
            
            yield scrapy.FormRequest(url,
                         #headers = headers,
                         method = 'GET',             # GET or POST
                         #formdata = myFormData,       # 表单提交的数据
                         callback = self.event_parse,
                         dont_filter = True,)
            
            #event_parse(self,data)
            #yield scrapy.Request(url,callback=self.event_parse)


    def event_parse(self, response):
        #result = json.loads(response.body.decode('utf-8').encode('utf-8'))
        #result = json.loads(response.body.decode('utf-8').encode('utf-8'))
        print(result)
	
        records = result['data']['result']
        item = CultureEventItem()
        for record in records:
            detail_id = record['id']
            item['place'] = record['address']
            item['pav_name'] = '云南省文化云'
            item['click_number'] = record['clickNum']
            url = "https://www.ynggwhy.cn/api-web/web/app/ccActivity/app_pass/detail/"+ detail_id
            item['url'] = url
            headers1 = {'Host': 'www.ynggwhy.cn',
            'Cookie': 'hbAppId=hbY3dGDs5jDBxn6RTX; dataAppId=daKkDxc2MW42rSwAEZ; districtCode=530000; ip=124.205.77.115',
            'Referer': 'https://www.ynggwhy.cn/activity/detail/'+str(detail_id),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
            }

            yield scrapy.FormRequest(url,
                         headers = headers1,
                         method = 'GET',             # GET or POST

                         callback = self.event_text_parse,
                         meta={'item': item},
                         dont_filter = True)

    def event_text_parse(self, response):
        result = json.loads(response.body.decode('utf-8').encode('utf-8'))

        item = response.meta['item']
        
        item['activity_time'] = result['data']['startTime']
        item['activity_name'] = result['data']['name']
        item['organizer'] = result['data']['venueName']
        item['activity_type']= result['data']['typeName']
        item['contact'] = result['data']['contactInfo']
        contents = result['data']['content']
        soup = BeautifulSoup(contents,'html.parser')
        p_contents = soup.find_all('p')
        content =[]
        for p_content in p_contents:
            content.append(p_content.text)
            fulltext = ''.join(content)
            item['remark'] = fulltext.strip().replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t', '')
        return item


    '''
    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        item['pav_name'] = '广东省文化馆'
        item['pav_introduction'] = "广东省文化馆（广东省非物质文化遗产保护中心）成立于1956年，是广东省人民政府设立的专门从事群众文化工作和非物质文化传承保护工作的正处级公益一类事业单位。其主要职责任务有：组织开展具有导向性、示范性的群众文化艺术活动；辅导农村、社区、企业等开展群众文化活动，辅导、培训辖区内文化馆、站业余干部及文艺活动业务骨干，组织、指导、研究群众性文艺创作活动；组织开展群众文艺理论研究，搜集、整理、保护民族民间文化艺术遗产；负责广东省文化志愿者总队及全省文化志愿者队伍建设、管理、培训工作和文化志愿服务开展；执行全省非物质文化遗产保护的规划、计划和工作规范，组织实施全省非物质文化遗产的普查、认定、申报、保护和交流传播工作。馆内设有办公室、活动部、培训部、创作部、信息部、团队部、拓展部、省非物质文化遗产保护中心办公室共八个部室。       作为我省现代公共文化服务体系建设和公共文化服务的重要参与者、提供者，广东省文化馆始终坚持在省委、省政府和省文化厅的领导下，围绕党和政府的中心工作，以满足群众文化需求为立足点，以改善群众文化生活为目标，充分发挥省馆龙头示范作用，不断完善和创新现代公共文化服务，努力实现好、维护好、保障好广大人民群众的基本公共文化权益；以高度的历史责任感和使命感，着力推进现代公共文化服务体系建设，为我省建设文化强省和幸福广东，实现“三个定位、两个率先”的总目标做出应有的贡献。"
        item['region'] = '广东'
        item['area_number'] = ''
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item
    '''
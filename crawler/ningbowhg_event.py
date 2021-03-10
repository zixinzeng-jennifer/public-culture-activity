# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem

import re
import time

import os
import codecs
import json
import sys
import datetime

def stamp_to_str(timeStamp):
    dateArray = datetime.datetime.utcfromtimestamp(timeStamp/1000)
    otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    return otherStyleTime

class Ningbowhg_eventSpider(scrapy.Spider):
    name = 'ningbowhg_event'
    #allowed_domains = ['jlsdmu.com/']


    # 爬去机构活动所需的参数


    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        for i in range(1,134):
            #formdata = {"currentPage":str(i)}
            url = 'http://www.nb1r1y.com/activity/getFActivitySearch.show?activityFlag=0&activityTime=0&pageNum='+str(i)+'&pageSize=10&sort=0&title='
            yield scrapy.FormRequest(url,callback=self.event_parse)


    def event_parse(self, response):
        result = json.loads(response.body.decode('utf-8').encode('utf-8'))
        #print(result)
        records = result['data']['list']
        item = CultureEventItem()
        for record in records:
            detail_id = record['contentId']
            item['pav_name'] = '宁波文化馆'
            url = "http://www.nb1r1y.com/activity/getFActivityDetailForJoin.show?id="+ str(detail_id)
            item['url'] = 'http://www.nb1r1y.com/nbs/user_activityDetail/'+str(detail_id)
            item['activity_time']=stamp_to_str(record['startTime'])+"到"+stamp_to_str(record['endTime'])
            yield scrapy.FormRequest(url, meta={'item': item},callback=self.event_text_parse)

    def event_text_parse(self, response):
        result = json.loads(response.body.decode('utf-8').encode('utf-8'))

        item = response.meta['item']
        
        #item['activity_time'] = result['data']['list']['activityDate']

        item['activity_name'] = result['data']['list'][0]['title']
        item['organizer'] = result['data']['list'][0]['company']
        item['place'] = result['data']['list'][0]['address']
        #item['activity_type']= result['data']['list']['categoryName']
        #item['url'] = result
        print(item['activity_name'])
        contents = result['data']['list'][0]['content']
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
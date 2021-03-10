# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureNewsItem, CultureBasicItem, CultureEventItem

import re
import time
from urllib.parse import unquote
import os
import codecs
import json
import sys


class Yunnan_dali_whySpider(scrapy.Spider):
    name = 'yunnan_dali_why'
    #allowed_domains = ['jlsdmu.com/']


    
    def start_requests(self):
        for i in range(1,2):
            headers = {'Host': 'www.dlzqzysg.com',
            'Referer': 'http://www.dlzqzysg.com/dlis/user_activityMore',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type':'application/json;charset=UTF-8',
            'If-Modified-Since': '0',
            'Pragma': 'no-cache',
            'project': 'qj',}

                
            url = 'http://www.dlzqzysg.com/activity/getFActivitySearch.show?activityFlag=0&activityTime=0&pageNum='+str(i)+'&pageSize=16&sort=0&title='
            print("-----------第"+str(i)+"页-----------")
            yield scrapy.FormRequest(url,
                         headers = headers,
                         method = 'GET',             # GET or POST
                         callback = self.event_parse,
                         dont_filter = True,)

    def event_parse(self, response):
        item = CultureEventItem()
        
        result = json.loads(response.body.decode('utf-8').encode('utf-8'))
        records = result['data']['list']
        for record in records:
            detail_id = record['contentId']
            item['pav_name'] = '云南大理文化云'
            item['activity_name'] = record['title']
            url = 'http://www.dlzqzysg.com/activity/getFActivityDetailForJoin.show?id='+str(detail_id)
            item['url'] = 'http://www.dlzqzysg.com/dlis/user_activityDetail/'+str(detail_id)
            item['place'] = record['address']
            item['organizer'] = record['company']

            yield scrapy.FormRequest(url,
                         method = 'GET',             # GET or POST
                         callback = self.event_text_parse,
                         meta={'item': item},
                         dont_filter = True)
        
    def event_text_parse(self, response):
        result = json.loads(response.body.decode('utf-8').encode('utf-8'))

        item = response.meta['item']
        content1 = result['data']['list'][0]
        item['activity_time'] = content1['startTime']
        if content1['content']!=None:
            contents = unquote(content1['content'])
            soup = BeautifulSoup(contents,'html.parser')
            p_contents = soup.find_all('p')
            content =[]
            for p_content in p_contents:
                content.append(p_content.text)
            if content !=[]:
                fulltext = ''.join(content)
                item['remark'] = fulltext.strip().replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t', '').replace('\xa0','').replace('<br>','').replace('</br>','').replace('<b>','').replace('</b>','')
            else:
                item['remark'] = contents.replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\t', '').replace('\xa0','').replace('<br>','').replace('</br>','').replace('<b>','').replace('</b>','')

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
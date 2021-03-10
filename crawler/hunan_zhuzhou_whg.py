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


class ShanxiwhySpider(scrapy.Spider):
    name = 'hunan_zhuzhou'
    #allowed_domains = ['jlsdmu.com/']


    def start_requests(self):
        for i in range(1,5):
            headers = {'Host':'www.hnzzwhg.com',
            'Referer': 'http://www.hnzzwhg.com/zzs/user_activityMore/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',}

            url = 'http://www.hnzzwhg.com/activity/getFActivitySearch.show?activityFlag=0&activityTime=0&pageNum='+str(i)+'&pageSize=10&sort=0&title='
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
            item['pav_name'] = '湖南株洲文化馆'
            url = 'http://www.hnzzwhg.com/activity/getFActivityDetailForJoin.show?id='+str(detail_id)
            item['activity_name'] = record['title']
            item['place'] = record['address']
            item['activity_type'] = record['dlabelList']
            item['activity_time'] = record['createTime']
            item['organizer'] = record['pname']
            item['url'] = record['linkAddress']
            headers1 = {':Host': 'www.hnzzwhg.com',
            'referer': 'http://www.hnzzwhg.com/zzs/user_activityDetail/'+str(detail_id),}

            yield scrapy.FormRequest(url,
                         headers = headers1,
                         method = 'GET',             # GET or POST
                         callback = self.event_text_parse,
                         meta={'item': item},
                         dont_filter = True)
        
    def event_text_parse(self, response):
        result = json.loads(response.body.decode('utf-8').encode('utf-8'))

        item = response.meta['item']
        contents = result['data']
        item['activity_time'] = contents['activityStartTime']
        item['remark'] = contents['brief']
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
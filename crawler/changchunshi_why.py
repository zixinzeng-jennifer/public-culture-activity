# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureEventItem, CultureNewsItem, CultureBasicItem
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time


def timestamp_to_date(time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
    time_array = time.localtime(time_stamp)
    str_date = time.strftime(format_string, time_array)
    return str_date

class ChangchunwhySpider(scrapy.Spider):
    name = 'changchunwhy'
    # allowed_domains = ['http://www.nmgbwy.com/']

    # 爬去机构讲座活动所需的参数
    event_url = 'http://www.jlswhg.com/ccs/user_activityMore/'


    event_count = 1
    event_page_end = 4





    def start_requests(self):
        # 请求机构介绍信息
        # yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        # yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        for i in range(self.event_count,self.event_page_end+1):
            url="http://www.jlswhg.com/activity/getFActivitySearch.show?activityFlag=0&activityTime=0&activityTypeId=1&menuId=19&pageNum="+str(i)+"&pageSize=10&sort=0&title="
            yield scrapy.Request(url, callback=self.event_parse)
        # yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    '''
    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        item['pav_name'] = '内蒙古图书馆'
        item['pav_introduction'] = \
            '内蒙古图书馆是自治区最早建立的公共图书馆，其发展历史可上溯到清光绪34年（公元1908年）11月归化城副都统三多在旧城小东街文昌庙内创办的“归化城图书馆”。1925年改名为“绥远省立图书馆”。日寇侵占期间，蒙古文化馆改为蒙古文化研究所，并于1942年迁往张家口。1945年由于战乱，原蒙古文化研究所的藏书损失过半。1947年4月，绥远省政府将残余图书运回归绥，于11月4日恢复省立图书馆。1949年8月，省立图书馆迁入原省立国民教育馆旧址，成为绥远省社会教育推行委员管辖下的图书馆。' \
            '1950年5月，奉绥远省文教厅的指示，在原绥远省社会教育推行委员会的基础上筹建省图书馆。先在工人文化宫后的小院开办了一个图书室，同年10月，该室迁至新城鼓楼，正式命名为“绥远省人民图书馆”。1957年，内蒙古自治区成立十周年时，在呼和浩特人民公园内建成建筑面积2830平方米馆舍，设计藏书容量30万册。该馆舍于1957年3月竣工使用，于5月1日庆祝内蒙古自治区成立十周年之日，由内蒙古自治区主席乌兰夫亲自剪彩开馆。' \
            '1965年12月，内蒙古科学技术图书馆并入内蒙古图书馆，成为内蒙古图书馆科技部。1984年5月又将科技部交给内蒙古科委。图书馆进入了一个全面发展的新时期。藏书由建国初期的3万余册增加到140余万册，远远超过了馆舍原设计藏书容量。' \
            '1985年内蒙古政府决定新建内蒙古图书馆。新馆地址位于呼和浩特市乌兰察布西路，占地2.8万平方米，总建筑面积2万平方米。1995年4月8日，新馆建设破土动工，1997年7月8日竣工，1998年5月28日新馆正式开馆接待读者。新馆开放后，每年接待读者50多万人次，受到社会各界广泛关注，已成为自治区最大的功能齐全、设施先进的公共图书馆。2008年1月内蒙古图书馆改扩建工程正式启动，历时近两年的时间，2009年10月1日土建工程完工，并试开放接待读者。2010年5月1日正式开放。改扩建后的图书馆馆舍面积近3万平方米，为读者提供了大型阅览室和休闲区，改变了传统图书馆的借阅方式，使读者和图书实现零距离接触。'\
            '内蒙古图书馆从2011年开始实行免费服务，长期坚持无节假日为读者开放，周开放时间达64个小时。我馆现有藏书365万册，数字资源131.27T,藏书具有公共图书馆的综合性和广泛性，兼具民族和地方特色。先后成立了“全国文化信息资源共享工程内蒙古分中心”、“内蒙古古籍保护中心”、“全国文化信息资源共享工程蒙古语资源建设中心”、“中国国际蒙古文文献收藏研究中心”，还开设有少年儿童图书馆和残疾人图书馆。在坚持阵地服务的同时，还先后在社区、部队、学校、企业、监狱等开展馆外服务。 '\

        item['region'] = '内蒙古'
        item['area_number'] = '3万平方米'
        item['collection_number'] = '365万册'
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item
    '''
    selenium_path = 'C://Users/Zixin Zeng/AppData/Local/chromedriver.exe'
    def event_parse(self, response):
        result = json.loads(response.body.decode('utf-8').encode('utf-8'))
        event_lists=result['data']['list']

        for event in event_lists:
            item=CultureEventItem()
            try:
                item['pav_name'] = '长春文化馆'
                item['activity_name']=event['title']
                item['url'] = event['linkAddress']
                #print(event['startTime'])
                item['activity_time']=timestamp_to_date(event['startTime']/1000)+"到"+timestamp_to_date(event['endTime']/1000)
                #re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.find('div', {'class': 'info'}).p.span.text)[0]
                yield scrapy.Request('http://www.jlswhg.com/activity/getFActivityDetailForJoin.show?id='+str(event['contentId']), meta={'item': item}, callback=self.event_text_parse)
            except Exception as err:
                print(err)



    def event_text_parse(self, response):
        item = response.meta['item']
        data=json.loads(response.body)
        print("item-data:",data['data']['list'][0])
        soup=BeautifulSoup(data['data']['list'][0]['content'],'html.parser')
        content=soup.text.replace('\n','').replace('\u3000','').replace('\xa0','')
        print("debug:",content)
        p_content=[]
        for p in soup.find_all('p'):
            p_content.append(p.text.replace('\n','').replace('\u3000','').replace('\xa0',''))
        """
        p_tags = content.find_all('p')
        """
        item['remark'] = content
        item['place'] = data['data']['list'][0]['address']
        """
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
        """
        ########################################################################################
        item['activity_type'] = ''
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
            if re.findall(r'(...)老师', content)[0] and item['presenter'] == '':
                temp=re.findall(r'(...)老师', content)[0].split()[-1]
                if(temp[-1]==')'):
                    item['presenter']==''
                elif(len(temp)==1):
                    item['presenter'] = temp+"老师"
                else:
                    item['presenter']=temp
        except:
            pass
        try:
            if re.findall(r'(...)先生', content)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)先生', content)[0]
        except:
            pass
        try:
            if re.findall(r'(...)姐姐', content)[0] and item['presenter'] == '':
                item['presenter'] = re.findall(r'(...)姐姐', content)[0]
        except:
            pass
        ########################################################################################
        item['organizer'] = data['data']['list'][0]['company']
        """
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
        """
        ########################################################################################
        item['age_limit'] = ''
        try:
            if re.findall(r'不限年龄', content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'不限年龄', content)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d~[1‐9]?\d岁)', content)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d岁-[1‐9]?\d岁)', content)[0]
        except:
            pass
        try:
            if re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', content)[0] and item['age_limit'] == '':
                item['age_limit'] = re.findall(r'([1‐9]?\d-[1‐9]?\d岁)', content)[0]
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
            if '联系人：' in p_content[i]:
                item['contact'] = p_content[i].split('：')[1]
                break
        try:
            if re.findall(r'\d{4}—\d{8}', content)[0] and item['age_limit'] == '':
                item['contact'] = re.findall(r'\d{4}—\d{8}', content)[0]
        except:
            pass
        try:
            if re.findall(r'\d{8}', content)[0] and item['age_limit'] == '':
                item['contact'] = re.findall(r'\d{8}', content)[0]
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

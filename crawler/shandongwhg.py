# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureEventItem, CultureNewsItem, CultureBasicItem
import re


class ShandongwhgSpider(scrapy.Spider):
    name = 'shandongwhg'
    #allowed_domains = ['nmglib.com/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.sdpcc.cn/about/wenhuaguan.html'

    # 爬去机构动态所需的参数
    news_url = 'http://www.sdpcc.cn/list/zixun.html'
    news_base_url = 'http://www.sdpcc.cn/list/zixun/'
    news_count = 1
    news_page_end = 20

    # 爬去机构讲座活动所需的参数
    zl_event_url = 'http://www.sdpcc.cn/list/dongtai.html'
    zl_event_base_url = 'http://www.sdpcc.cn/list/dongtai/'
    zl_event_count = 1
    zl_event_page_end = 84

    # 爬去机构讲座活动所需的参数
    #jz_event_url = 'http://www.nmglib.com/zjzl/jz/'
    #jz_event_base_url = 'http://www.nmglib.com/zjzl/jz_'
    #jz_event_count = 1
    #jz_event_page_end = 6

    def start_requests(self):
        # 请求机构介绍信息
        #yield scrapy.Request(self.intro_url, callback=self.intro_parse)
        # 请求机构动态信息
        #yield scrapy.Request(self.news_url, callback=self.news_parse)
        # 请求机构活动信息
        yield scrapy.Request(self.zl_event_url, callback=self.zl_event_parse)
        #yield scrapy.Request(self.jz_event_url, callback=self.jz_event_parse)

    def intro_parse(self, response):
        item = CultureBasicItem()
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        item['pav_name'] = '山东省文化馆'
        item['pav_introduction'] = \
            '山东省文化馆（山东省非物质文化遗产保护中心）是山东省人民政府设立的公益性文化事业机构，隶属于山东省文化和旅游厅，国家一级文化馆，是全省重大群众文化活动组织指导策划中心、公共文化辅导培训中心、群众文艺作品创作及群众文化理论研究中心、非物质文化遗产保护中心，担负着对全省各级文化馆（站）业务指导，组织开展全省导向性、示范性群众文化活动，组织开展全省各级文化馆（站）业务干部和业余文艺骨干辅导培训，传播普及文化知识，开展对外文化交流，挖掘整理保护非物质文化遗产等职能。 山东省文化馆始建于1957年，建馆时为山东省群众艺术馆，1965年更名为山东省文化馆，1971年更名为山东省艺术馆，2007年经省编办批准同意加挂山东省非物质文化遗产保护中心牌子。2013年更名为山东省文化馆(省非物质文化遗产保护中心)。建馆初期，仅有一栋1600平方米二层砖木钢筋混凝土结构的综合业务楼；原馆址坐落于济南市市中区杆南西街27号，1998年12月，翻建的5500平方米的业务楼投入使用。新馆是在原山东省博物馆的基础上改造完成的，2012年4月批准立项，2012年5月开工建设， 2013年改建完成，建筑面积14200平方米。' \
            '新馆风貌 新馆位于济南市经十一路十四号，与名胜千佛山毗邻，交通便利。主楼大厅设有大型壁画《齐风鲁韵、盛世群星》，东西两侧设计了《稷下争鸣》和《杏坛六艺》锻铜浮雕壁画，凸显了现代群众文化和齐鲁文化的相互融合。 室内划分为群众文化活动区、专业研究和办公区、非物质文化遗产传习展示区三大区域，设有多功能厅、各专业艺术门类排练厅、辅导培训教室、书画展厅、非物质文化遗产传习厅和精品陈列厅、群星舞台、图书资料室、电子阅览室、视听体验室、群星画廊等群众文化活动场所20余处。 室外划分为群众文化广场区域、东庭院区域和中庭院区域三个区域。其中，群众文化活动广场占地面积约4000平方米，能够举办1000余人中小型文化活动；东庭院区域为中老年活动广场，面积500平方米，建有小型演出戏台；中庭院区域为少儿活动区，面积720平方米，建有山东省少年儿童大画廊，二楼、三楼环廊为聚雅艺术空间。' \
            '机构设置 山东省文化馆（山东省非物质文化遗产保护中心）各艺术门类齐全，拥有音乐、舞蹈、戏剧、曲艺、美术、书法、摄影、非物质文化遗产保护与研究等一批高素质的专业技术人员，设有办公室、行政科、财务科、老干部科、活动策划部、创作演出部、辅导培训部、美术摄影部、展览陈列部、调研编辑部、数字文化部、志愿服务部、社会艺术普及中心、非物质文化遗产保护中心办公室、保护研究部等15个职能部科室。' \
            '荣誉称号 山东省文化馆（山东省非物质文化遗产保护中心）始终秉承"面向公众，服务基层，服务社会"的办馆宗旨，为推动山东群众文化的繁荣发展做出了巨大贡献，获得了许多荣誉。荣获第十届中国艺术节筹办组织工作先进集体并记集体二等功，被国家文化部、人事部授予"全国文化先进集体"，全国文化文物系统先进党组织，全国维护妇女儿童权益先进集体；被国家民政部、文化部、残疾人联合会评为爱心助残先进单位；2017年12月被山东省精神文明建设委员会授予省级精神文明单位称号。7人次获文化部颁发的"文艺志书编纂成果奖"，一人享受国务院津贴待遇并被文化部授予特殊贡献个人奖，两人被文化部、人事部授予"全国文化系统先进工作者"称号，一人被文化部评为"群文之星"并被省政府授予先进工作者称号，两人被文化部评为全国非物质文化遗产保护先进个人，19人次荣立一、二、三等功。'\
            '业务成果◆ 组织承担多项全国及全省性大型群众文化活动，大型群众文化活动获文化部第十四届"群星奖"服务奖 近年来，承担并圆满完成了国家和省委、省政府多项重大公益活动，2007年大型群众文化活动荣获文化部第十四届"群星奖"服务奖，2008年北京奥运会"中国故事--祥云小屋"文化展示活动获北京奥组委和国家文化部"最受欢迎奖"，2009年承担第十一届全运会开幕式仪式前演出活动、国庆60周年天安门广场游行山东彩车的设计制作活动，2010年上海世博会山东活动周的迎宾演出、沿街巡游和非物质文化遗产传习区展示活动以及两届中国非物质文化遗产博览会等；◆ 成功举办了"歌颂新中国，喜迎全运会系列群众文化活动"、山东省农村文化艺术节、文化广场、文化"四进社区"、非物质文化遗产进校园、"文化齐鲁、和美山东"全省少年儿童大画廊、"文明山东从我做起"少年儿童美术书画大展等全省性、导向性、示范性群众文化系列活动和文化惠民项目。◆ 公共文化辅导培训不断创新，"齐风鲁韵"传习大课堂获第十五届"群星奖"项目奖；◆ 重点打造培训品牌"齐风鲁韵"传习大课堂，共举办各类培训班200余期，2010年获第十五届"群星奖"项目奖；◆ 创新基层公共文化辅导培训方式，以省馆为龙头，以市馆为骨干，以县（市区）馆为基础，建立并完善为基层服务的长效机制，创建了"山东省百个基层文化辅导示范点网状辅导体系建设"，2012年被评为全省农村公共文化服务"优秀实践奖"；◆ 创新公共文化服务手段，利用网络和文化资源共享工程开展公共文化服务，制作的《教你学国画》等课件在文化资源共享工程播放；◆ 加大免费开放力度，常年举办各类免费文化艺术培训班，培养基层文艺骨干，并组建了"山东省群星艺术团"、"梦之翼女子合唱团""少儿书画院"、"少儿歌舞团"、"夕阳红艺术团"、"管弦民族乐团"等文艺团队；◆ 社会文化艺术考级工作规范有序，规模不断扩大，曾多次被省文化厅评为艺术考级先进单位。◆ 强化精品意识，群众文艺创作及理论研究成果斐然多年来，业务人员创作了大量优秀文艺、美术作品，仅在省级以上报刊发表、展演的就达上万件，获"群星奖"、"蒲公英奖"等国家政府奖项30多件，获省级政府奖百余件；编辑出版了《民间音乐概论》、《文化站长业务手册》、《群众文化论文集》等上百部群众文艺研究、辅导类专著，发表数百篇学术论文、几十部长篇小说和十几部戏剧作品。'\
        
        item['region'] = '山东'
        item['area_number'] = '1.4万平方米'
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    def news_parse(self, response):
        original_url = 'http://www.sdpcc.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', class_="news-list")
        #print("AAAAA______________:",article_lists)
        if article_lists:
            #print("BBBBBB_____________")
            LI = article_lists.find_all('div',class_="item item-img")
            if LI:
                print()
        for article in article_lists.find_all('div',class_="item item-img"):
            item = CultureNewsItem()
            try:
                item['pav_name'] = '山东省文化馆'
                item['title'] = article.a.find('div',class_="fl").find('h3',class_="self-ellipsis").string
                item['url'] = original_url + article.a.attrs['href']
               # item['time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.a.find('div',class_="fl").p.find('i',class_='time').text)[4]
                #print("???____________________???")
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
            except Exception as err:
                print(err)
        if self.news_count < self.news_page_end:
            self.news_count = self.news_count + 1
            yield scrapy.Request(self.news_base_url + str(self.news_count) + '.html', callback=self.news_parse)
        else:
            return None

    def news_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        try:
            p_tags=soup.find_all('p')
            p_content=[]
            for p in p_tags:
                p_content.append(p.text.replace('\u3000','').replace('\n','').replace('\xa0',''))
            item['remark']=''.join(p_content)
           # print('guguguguguguguguguggugugugu'+item['content'])
        except:
            item['content'] = ''
            #print('guguguguguguguguguggugugugu')
        return item

    def zl_event_parse(self, response):
        original_url = 'http://www.sdpcc.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('div', class_="news-list")
        #print("AAAAA______________:",article_lists)
        if article_lists:
            #print("BBBBBB_____________")
            LI = article_lists.find_all('div',class_="item item-img")
            if LI:
                print()
        for article in article_lists.find_all('div',class_="item item-img"):
            item = CultureEventItem()
            try:
                item['pav_name']='山东省文化馆'
                item['activity_name'] = article.a.find('div',class_="fl").find('h3',class_="self-ellipsis").string
                item['url'] = original_url + article.a.attrs['href']
                item['activity_time'] =''
                item['activity_type'] = '活动'
               # item['time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.a.find('div',class_="fl").p.find('i',class_='time').text)[0]
                
                #print("???____________________???")
                yield scrapy.Request(item['url'], meta={'item': item}, callback=self.zl_event_text_parse)
            except Exception as err:
                print(err)
        if self.zl_event_count < self.zl_event_page_end:
            self.zl_event_count = self.zl_event_count + 1
            yield scrapy.Request(self.zl_event_base_url + str(self.zl_event_count) + '.html', callback=self.zl_event_parse)
        else:
            return None

    def zl_event_text_parse(self, response):
        item = response.meta['item']
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        item['activity_time']=soup.find_all('div',{'class':'content'})[0].find('div',{'class':'news-info'}).text.strip().replace('&nbsp;','').replace('\u3000', '').replace('\n', '').replace('\xa0', '').replace('\t','')[3:13]
        try:
            p_tags = soup.find_all('div',{'class':'content'})[0].find_all('p')
            p_content = []
            for p in p_tags:
                p_content.append(p.text.replace('\u3000', '').replace('\n', '').replace('\xa0', '').replace('\t',''))
            item['remark'] = ''.join(p_content)
        # print('guguguguguguguguguggugugugu'+item['content'])
        except:
            item['content'] = ''
            # print('guguguguguguguguguggugugugu')
        return item

    #def jz_event_parse(self, response):
     #   original_url = 'http://www.nmglib.com/zjzl/jz/'
      #  data = response.body
       # soup = BeautifulSoup(data, 'html.parser')
        #article_lists = soup.find('div', class_="zy_ntgg")
        #print("AAAAA______________:",article_lists)
      #  if article_lists:
            #print("BBBBBB_____________")
        #    LI = article_lists.find_all('li')
         #   if LI:
          #      print()
       # for article in article_lists.ul.find_all('li'):
        #    item = CultureNewsItem()
         #   try:
          #      item['pav_name'] = '内蒙古图书馆'
           #     item['title'] = article.a.string
            #    item['url'] = original_url + article.a.attrs['href'][2:]
             #   item['time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.find('span').text)[0]
                #print("???____________________???")
               # yield scrapy.Request(item['url'], meta={'item': item}, callback=self.jz_event_text_parse)
          #  except Exception as err:
           #     print(err)
      #  if self.jz_event_count < self.jz_event_page_end:
       #     self.jz_event_count = self.jz_event_count + 1
        #    yield scrapy.Request(self.jz_event_base_url + str(self.jz_event_count) + '.html', callback=self.jz_event_parse)
       # else:
        #    return None


  #  def jz_event_text_parse(self, response):
   #     item = response.meta['item']
    #    data = response.body
     #   soup = BeautifulSoup(data, 'html.parser')
      #  try:
       #     item['content'] = str(soup.find('div', {'class': 'xxy_nr'}).text).strip().replace('\u3000', '').replace(
        #        '\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
       # except:
        #    item['content'] = ''
       # return item

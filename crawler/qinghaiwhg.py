# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from cultureBigdata.items import CultureEventItem, CultureNewsItem, CultureBasicItem
import re


class   QinghaiwhgSpider(scrapy.Spider):
    name = 'qinghaiwhg'
    #allowed_domains = ['nmglib.com/']

    # 爬去机构介绍所需的参数
    intro_url = 'http://www.qhshwhg.com/column/61.html'

    # 爬去机构动态所需的参数
   # news_url = 'http://www.jxsqzysg.com/portal/category/info?cid=10&pnid=nav6&snid=subnav54'
    #news_base_url = 'http://www.sdpcc.cn/list/zixun/'
   # news_count = 1
    #news_page_end = 20

    # 爬去机构讲座活动所需的参数
    zl_event_url = 'http://www.qhshwhg.com/column/103.html'
    zl_event_base_url = 'http://www.qhshwhg.com/column/103_'
    zl_event_count = 1
    zl_event_page_end = 1

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
        item['pav_name'] = '青海省文化馆'
        item['pav_introduction'] = \
            '青海省文化馆始建于1957年，是国家设立的公益性事业单位，是繁荣群众文化的主导性业务职能部门和龙头单位。'\
            '主要职责：主承办政府主办的各类公共文化服务活动；组织、策划各类公共文化艺术活动；为群众提供各种健康有益的文化服务；组织群众文艺作品创作、辅导；负责区域内业务干部、文艺骨干的培训、辅导工作，引导、指导基层文化艺术机构和团队建设；负责群众文化的调研和优秀民族民间文化资源的调查、挖掘、整理、研究、保护、管理和合理利用，承担非物质文化遗产的保护；组织展示群众文化艺术成果，为群众提供综合配套服务的重要平台；开展对外文化交流，弘扬中华民族优秀文化。'\
            '工作机构：馆内设办公室、财务部、文艺活动部、公共文化服务部、调查研究部、非遗办公室、美术摄影部、数字文化服务中心、《群文天地》杂志社、《藏族民俗文化》杂志社。“十二五”期间，青海省文化馆在挖掘、继承、弘扬青海民族民间艺术；组织、策划、宣传全省各类大型文化活动；开展各类艺术培训、创作、理论研究方面做出了不懈的努力，得到了各级领导的肯定和社会各界的称誉。'\
            '青海省文化馆和业务干部共获得各类奖项94个，其中省文化馆获国家级奖项15个，省部级奖项3个，厅级奖项4个。2013年，品牌活动“西北五省（区）花儿演唱会”荣膺第十届中国艺术节项目类群星奖。欢乐乡村行巡回演出项目荣获2013年文化志愿者基层服务年示范项目。2015年，青海省文化馆由中央宣传部、中央文明办、教育部、科技部、司法部、农业部、文化部、国家卫生计生委、国家新闻出版广电总局、共青团中央、全国妇联、中国科协等12部委授予“全国文化科技卫生‘三下乡’先进集体”称号。同年，在第四次全国文化馆评估中，评估组用“工作扎实，引领示范作用突出；文化活动不落东部，富有特色；汉藏两刊全国首屈一指，改革、管理走在全国前列，达到等级馆必备条件。”对青海省文化馆的工作开展给予了积极的肯定和评价。          2016年出版图书《河湟民间文艺代表作丛书》获得青海省第十一次哲学社会科学优秀成果著作类三等奖；被评为先进基层党组织、省级精神文明建设先进单位。2017年“魅力乌拉特”第三届中国西部民歌会优秀组织奖......其中，2015年12月，根据新馆设施建设达到省级一级馆的标准和青海省文化馆在面向社会开展公共文化服务取得的成绩，青海省文化馆被文化部评为省级一级馆。近年来，在省委、省政府的关怀，省委宣传部、省财政厅、省文化新闻出版厅支持下，青海省文化馆新馆作为全省“十二五”期间的重点文化惠民工程，于2016年12月29日开馆试运行。新馆位于西宁市西关大街新宁广场南侧，省图书馆、省美术馆连体建筑东侧，占地面积8000平方米。'\
            '设有四大功能区：一是群众文化培训展示区、青海特色文化展示区、回廊展示区等，展示群众文化成果的三大展区（占总面积的5%）；二是是美摄交流室、静态培训教室、舞蹈（综合）排练室等提供各种群众辅导、培训、交流的功能设施（占地面积36%）；三是电子阅览室、数字文化服务中心等在线群众文化服务活动，提供数字化信息浏览平台的功能设施（占地面积2%）；四是拥有457个座位的群星剧场、126个座位的多功能厅（占总面积的45%），常年为各个年龄段、不同层次的群众进行全民文化艺术普及。新馆开放后，青海省文化馆将依托“阵地服务、流动服务、数字化服务”，以“服务立馆、品牌兴馆、数字强馆”为宗旨，进一步完善“一项工程”，做强八个团队，做大八个品牌。以“一项工程”为抓手，面向基层全力推进“双级联动，服务基层”的工作机制，拓宽文化惠民的新途径；以“西北五省（区）花儿演唱会、‘欢乐乡村’巡演活动、青海省群文干部技能大赛、《群文天地》和《藏族民俗文化》两刊等”品牌活动为引领，在弘扬优秀民族文化，保护、传承非物质文化遗产，加强队伍建设，丰富农（牧）民文化生活，开创文化惠民新局面；以省厅和文化部全国公共文化服务中心签署“汉藏文化交流项目”，国家推进数字文化馆建设为契机，加快数文化馆建设，实现线上服务配送、线下资源共享、移动终端信息推送、现场数字体验、互联网+模式将群众文化服务面通过数字化延伸拓展。通过举办全省群文专业各艺术门类业务干部培训班和基层文化馆馆长培训班，在“送文化”的基础上，最终实现“种文化”的目的，进而夯实文化惠民的基础。（文：省文化馆调研部）'\
            
        item['region'] = '青海'
        item['area_number'] = '8000平方米'
        item['collection_number'] = ''
        item['branch_number'] = ''
        item['librarian_number'] = ''
        item['client_number'] = ''
        item['activity_number'] = ''
        yield item

    #def news_parse(self, response):
        #original_url = 'http://www.sdpcc.cn'
     #   data = response.body
      #  soup = BeautifulSoup(data, 'html.parser')
       # article_lists = soup.find('ul', class_="n_l")
        #print("AAAAA______________:",article_lists)
      #  if article_lists:
            #print("BBBBBB_____________")
       #     LI = article_lists.find_all('div',class_="item item-img")
        #    if LI:
         #       print()
       # for article in article_lists.find_all('li'):
        #    item = CultureNewsItem()
         #   try:
          #      item['pav_name'] = '青海省文化馆'
           #     item['title'] = article.a.find('div',class_="fl").find('h3',class_="self-ellipsis").string
            #    item['url'] = original_url + article.a.attrs['href']
               # item['time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.a.find('div',class_="fl").p.find('i',class_='time').text)[4]
                #print("???____________________???")
             #   yield scrapy.Request(item['url'], meta={'item': item}, callback=self.news_text_parse)
           # except Exception as err:
            #    print(err)
       # if self.news_count < self.news_page_end:
        #    self.news_count = self.news_count + 1
         #   yield scrapy.Request(self.news_base_url + str(self.news_count) + '.html', callback=self.news_parse)
       # else:
        #    return None

    #def news_text_parse(self, response):
     #   item = response.meta['item']
      #  data = response.body
       # soup = BeautifulSoup(data, 'html.parser')
       # try:
        #    item['content'] = str(soup.find('div', {'class': 'content'}).text).strip().replace('\u3000', '').replace(
         #       '\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
           # print('guguguguguguguguguggugugugu'+item['content'])
        #except:
         #   item['content'] = ''
            #print('guguguguguguguguguggugugugu')
       # return item

    def zl_event_parse(self, response):
        #original_url = 'http://www.sdpcc.cn'
        data = response.body
        soup = BeautifulSoup(data, 'html.parser')
        article_lists = soup.find('ul', class_="n_l")
        #print("AAAAA______________:",article_lists)
        if article_lists:
            #print("BBBBBB_____________")
            LI = article_lists.find_all('li')
            if LI:
                print()
        for article in article_lists.find_all('li'):
            item = CultureEventItem()
            try:
                item['pav_name'] = '青海省文化馆'
                item['activity_name'] = article.a.text[1:]
                item['url'] = article.a.attrs['href']
                item['activity_time'] = re.findall(r'(\d{4}-\d{1,2}-\d{1,2})', article.span.text)[0]
                item['activity_type'] = '活动'
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
        try:
            content = str(soup.find('div', {'class': 'right_content_con'}).text).strip().replace('\u3000', '').replace(
                '\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
        except:
            content = ''
        item['remark']=content
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

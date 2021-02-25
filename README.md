# public-culture-activity     
Contains code for "Uncovering Topics of Chinese Public Cultural Activities in 2020 with Text Clustering", full paper for JCDL 2021.      
Input files should be in json format.     

Input Example:(*Note: activity_name, activity_time, remark, geo are required)    

{"pav_name": "安徽蚌埠文化云",    
"activity_name": "2020非遗活态文化摄影作品基层巡展一一走进淮上区槐花园社区",    
"activity_time": "2020-11-17",    
"url": "http://www.bbszwhy.com/Cloud/Module/Activity/Show/Show.html?id=5fae44483b4d140e944a0e02",    
"activity_type": "展览",    
"place": "淮上区槐花园社区",  
"organizer": "蚌埠市文化馆",    
"remark": "一、活动名称2020非遗活态文化摄影作品基层巡展二、活动时间11月17日周二上午9：30～11：30三、活动地点淮上区槐花园社区四、主办单位蚌埠市文化和旅游局五、承办单位蚌埠市文化馆（市非遗保护中心），蚌埠市文化馆联盟六、活动内容本次展览内容主要为本土的非遗文化，图文并茂地展示我市国家级、省级、市级、区级非物质文化遗产项目。七、参与方式无须报名，直接到活动现场即可参与。", "geo": "anhui"}  


Major Environment Requirements:     
jieba    
tensorflow-2.3.0     
keras    
sklearn    

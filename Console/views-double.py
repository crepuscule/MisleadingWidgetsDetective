'''
1. 用户功能 <<
2. 存储评测结果 << 
3. 将管理和评测彻底分开，做好评测的主页面，要求登录才能进入评测(中午)
3. 上线使用管理界面跑程序的功能(中午)
'''
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from threading import Thread
from bson import ObjectId
import re
import time
import datetime
import bcrypt
import math
import csv
import os
from . import HelpMeDownload

#DBNAME = 'db_DroidBotMW'
#DBNAME = 'db_Droidbot1128'
#DBNAME = 'db_DroidBotMW_tfidf'
#DBNAME = 'db_Fdoidtest_1000'
DBIP = '127.0.0.1'
DBPORT = 27017
#DBNAME = 'db_googleplay_13k'
#DBNAME = 'db_f_droid_9h'
DBNAME = 'db_universal_set'
RAWAPKFOREST = 'rawapkforest'
#HOST_NAME = 'http://219.216.64.42:8000/'
HOST_NAME = 'http://219.216.64.127:8000/'
#HOST_NAME = 'http://uimanager.crepuscule.site:8601/'
STATIC_PATH = HOST_NAME + 'static'
PICTURE_PATH = 'http://219.216.64.127'
#PICTURE_PATH = 'http://127.0.0.1'
#PICTURE_PATH = 'http://uimanager.crepuscule.site:8601/static'
CONFIG_PATHS = '/home/dl/users/wangruifeng/05MisleadingWidgets/androidwidgetclustering'
CURRENT_APP_SET_PATH = '/home/dl/users/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/static/applist.txt'

# 应该可以避免而从算法系统中读出的:
RAW_ROOT = '/data/wangruifeng/datasets/DroidBot_Epoch/raw_data/'
ZIP_ROOT = '/data/wangruifeng/datasets/DroidBot_Epoch/zips/'
COVER_ICON_TXT_PATH = '/data2/user_codes/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/Console/needcover.txt'
COVER_ICON_CSV_PATH = '/data2/user_codes/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/Console/tneedcover.csv'

# #>>Basic  ---------------------------------------------------------------------------------------------------------------
# path('',views.homepage),
# path('home',views.homepage),

def isAtPackageList(api,package_list):
    import re
    # 这么做的目的是，不让android直接就匹配，要不然误进很多api
    # 正则表达式，从开头开始的小写字母或者\.，遇到大写就结束了，这样可以匹配出包名
    package_regex = re.compile('^[a-z\.]+')
    package_regex_result = package_regex.match(api)
    if package_regex_result == None:
        print('无法获取包名！')
        return '',False # 无法获取包名！
    else:
        package = package_regex_result.group(0).rstrip('.')

    print('searching >>%s<< in package_list...' % package)
    if package in package_list:
        return package,True
    return package,False

def readTxt(path):                                                                                                   
    #path += '.txt'                                                                                                       
    file_handle=open(path,mode='r')                                                                                       
    lines = file_handle.readlines()                                                                                       
    file_handle.close()                                                                                                   
    content = []                                                                                                          
    for i in lines:                                                                                                       
        content.append(i.strip('\n').strip(' '))                                                                                     
    print(path,',',len(content),' records read.')                                                                         
    return content

'''
def writeTxt(content,path):                                                                            
    #path += '.txt'                                                                                         
    file_handle=open(path,mode='w')                                                                         
    file_handle.write(content)                                                                   
    file_handle.close()                                                                                     
    print(path,',',len(content),' records writen.') 
'''

def writeTxt(content,path,mode='w'):
    #path += '.txt'
    file_handle=open(path,mode=mode)
    file_handle.write("\n".join(content))
    file_handle.close()
    print(path,',',len(content),' records writen.')

def readDict(path,readType="ordered"):
    #path += '.json'
    import json
    from collections import OrderedDict
    readfile = open(path,mode='r')
    if readType == "ordered":
        content = json.loads(readfile.read(), object_pairs_hook=OrderedDict)
    else:
        content = json.loads(readfile.read())
    readfile.close()
    print(path,',',len(content),' keys read.')
    return content

def writeDict(content,path):
    #path += '.json'
    import json
    writefile = open(path,mode='w')
    writefile.write(json.dumps(content))
    writefile.close()
    print(path,',',len(content.keys()),' keys read.')
    


# Basic
def homepage(request):
    #根据需要选择HttpRespone或者HttpResponse
    # 获取数据库信息
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']
            subtaskDict['link'] = '/Console/console/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/homepage.html', context)

def loadInterpreter(configPaths, projectName="", subtask_name=""):
    import sys, os
    sys.path.append(os.path.abspath(configPaths)) 
    sys.path.append(os.path.abspath(configPaths)+'/Assistant/') 
    import Interpreter
    from importlib import reload
    reload(Interpreter)
    # use 1, 2 to use different config file
    #self.config = configuration.initConfig(2)
    #return configuration.initConfig(1)
    if projectName == "" or subtask_name == "":
        interpreter = Interpreter.Interpreter()
        return interpreter
    interpreter = Interpreter.Interpreter(projectName+'.'+subtask_name)
    return interpreter#.ParsingConfig()

# Basic
def loadDataBase(configPaths):
    import sys, os
    sys.path.append(os.path.abspath(configPaths)+'/Base/') 
    import DataBaseProcessor
    from importlib import reload
    reload(DataBaseProcessor)
    # use 1, 2 to use different config file
    #self.config = configuration.initConfig(2)
    #return configuration.initConfig(1)
    dataBaseProcessor = DataBaseProcessor.DataBaseProcessor()
    dataBaseProcessor.DBNAME = DBNAME
    dataBaseProcessor.rawApkForestName = RAWAPKFOREST
    return dataBaseProcessor

def writeEvaluation(content):
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    findResult = dataBaseProcessor.queryUsers({'username':username})

def objectId2Time(objectid):
    timestamp = time.mktime(objectid.generation_time.timetuple())
    #dateArray = datetime.datetime.fromtimestamp(timestamp)
    #otherStyleTime = dateArray.strftime("%Y.%m.%d %H:%M")
    time_str = datetime.datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')
    return time_str

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def index(request):
    #根据需要选择HttpRespone或者HttpResponse
    return JsonResponse({'message':'Hello world'})
    #return HttpResponse("Hello world")
# #<<Basic  ---------------------------------------------------------------------------------------------------------------

# #>>Users  ---------------------------------------------------------------------------------------------------------------
# path('login',views.login),
# path('users',views.users),
# path('addUser',views.addUser),
# path('deleteUser',views.deleteUser),

def login(request):
    username = request.GET.get('username','')
    password = request.GET.get('password','')

    password = password.encode('utf-8')
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    findResult = dataBaseProcessor.queryUsers({"password":1,'job':1,'email':1},{'username':username})
    print('findResult',findResult)
    true_password = findResult[0]['password']
    if bcrypt.checkpw(password, true_password):
        print("match")
        return JsonResponse({'msg':'True','username':username})
    return JsonResponse({'msg':'False'})

def users(request):
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    findResult = dataBaseProcessor.queryUsers({'_id':1,'username':1,'job':1,'email':1})
    context = {'userList':findResult,'staticPath':STATIC_PATH}
    print('in users',findResult)
    for i in range(len(findResult)):
        findResult[i]['no'] = findResult[i]['_id']
    return render(request, 'Console/users.html', context)

# Uesrs
def addUser(request):
    username = request.GET.get('username','user001')
    password = request.GET.get('password','user001')
    email = request.GET.get('email')
    job = request.GET.get('job')
    password = password.encode('utf-8')

    salt = bcrypt.gensalt(rounds=8)
    hashed = bcrypt.hashpw(password, salt)
    print('addUser:',{"username":username,"password":password,"job":job,'email':email})
    # db operator
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    insertResult = dataBaseProcessor.saveUsers({"username":username,"password":hashed,"job":job,'email':email})
    print(insertResult)
    context = {'userList':insertResult,'staticPath':STATIC_PATH, 'msg':'Add User %s Successfully!' % username}
    return JsonResponse({'msg':'Add User Successfully!'})

def deleteUser(request):
    user_id = request.GET.get('user_id')
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    print('deleteing id=',user_id)
    deleteResult = dataBaseProcessor.deleteUser(ObjectId(user_id))
    context = {'userList':deleteResult,'staticPath':STATIC_PATH}
    print('deleteResult',deleteResult)
    return JsonResponse({'msg':'Delete Successfully!'})

# #<<Users---------------------------------------------------------------------------------------------------------------

# #>>Console ---------------------------------------------------------------------------------------------------------------
## Console/console.html
# path('console',views.console),
# path('changedb/<str:db_name>',views.chooseDataBase),
# path('changeapkforest/<str:apkforest>',views.chooseRawApkForest),
# ## 用于检查有多少算法程序在本机执行
# path('checkRun',views.checkRun),
# ## Console/submitRun.html
# path('submitRun',views.submitRun),
# ## 进行数据集的预聚类，标注,去噪
# path('rawdatabase/<str:database>',views.tagRawDataBase),
# path('tagrawdatabase',views.submitRawDataBaseTag),
# path('apkforestlist',views.apkforestlist),
# path('apkforest/<str:apkforestName>',views.apkforest),
# path('apkForestSubmit',views.apkforestsubmit),
# ## 将app检查列表化简去重
# path('checkapp',views.checkAPPs),

def console(request):
    from pymongo import MongoClient
    default_cmd = '''
#尝试kpca降维到700,300,150的效果对比
A o kpcaExampleProject
######################### DP
# 已经提前处理过

A s spm_kpca700_optics
######################### DT
DT apktree csvsets

######################### IF
#IF extif spm
IF usedefault

######################### DE
DE vector

DE cutdim kpca,700
######################### VC
VC run
#VC eval
######################### OD
OD run
#OD eval

A s spm_kpca300_optics
DE cutdim kpca,300
######################### VC
VC run
#VC eval
######################### OD
OD run
#OD eval
    '''
    connection = MongoClient(DBIP, DBPORT)
    db_list = connection.database_names()
    db_list.remove('local')
    db_list.remove('admin')

    dataBaseList = []
    for db in db_list:
        dataBaseListItem = dict()
        dataBaseListItem['name'] = db
        save_path = RAW_ROOT + db + '/'
        try:
            remark =  '\n'.join(readTxt(save_path+'remark.txt'))
        except:
            remark = 'Click to Remark'
        dataBaseListItem['remark'] = remark
        dataBaseListItem['remarkLink'] = '/Console/remarkdatabase/%s' % db
        dataBaseListItem['tagLink'] = '/Console/tagrawdatabase/%s' % db
        dataBaseListItem['chooseLink'] = '/Console/changedb/%s' % db
        dataBaseList.append(dataBaseListItem)

    print(db_list)

    # apkforestlist
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    client = dataBaseProcessor.getConnection()
    collist = client.collection_names()
    apkForestList = []
    for line in collist:
        if '.' not in line and '_' not in line:
            # 作为列表之一
            apkForestListItem = dict()
            apkForestListItem['name'] = line
            apkForestListItem['tagLink'] = '/Console/apkforest/%s'  % line
            apkForestListItem['chooseLink'] = '/Console/changeapkforest/%s' % line
            apkForestList.append(apkForestListItem)

    context = {'default_cmd':default_cmd,'apkForestList':apkForestList,'staticPath':STATIC_PATH,'dataBaseList':dataBaseList,'current_db':DBNAME,'current_apkforest':RAWAPKFOREST}
    return render(request, 'Console/console.html', context)


# Console
def chooseDataBase(request,db_name=''):
    global DBNAME
    if db_name != '':
        DBNAME = db_name 
    return console(request)

def allDataBase(request):
    connection = MongoClient(DBIP, DBPORT)
    db_list = connection.database_names()
    res = {'db_list':db_list}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})

# Console
def chooseRawApkForest(request,apkforest=''):
    global RAWAPKFOREST
    if apkforest != '':
        RAWAPKFOREST = apkforest 
    return console(request)
    

# Console
@async
def callFun(cmd):
    import os
    from subprocess import PIPE
    import psutil
    writeTxt(cmd,CONFIG_PATHS+'Assistant/cmdline.txt')
    # 使用linux命令运行
    exectuePath = 'cd '+CONFIG_PATHS
    exectuor = '/home/crepuscule/anaconda3/envs/python3.6/bin/python3.6 '
    print(exectuePath + ' && '+exectuor + 'Assistant/Interpreter.py '+CONFIG_PATHS+'Assistant/cmdline.txt')
    os.system(exectuePath + ' && '+exectuor + 'Assistant/Interpreter.py '+CONFIG_PATHS+'Assistant/cmdline.txt')
    #interpreter = loadInterpreter(CONFIG_PATHS)
    #interpreter.sequenceCMD(cmd,'S')
    # 使用ps命令看一下有没有相关程序运行就行了，然后通过回调ajax返回就可以了

# Console
def checkRun(request):
    import os
    import psutil
    returnValue = os.popen('ps aux | grep "/home/crepuscule/anaconda3/envs/python3.6/bin/python3.6 Assistant/Interpreter.py" | wc -l')
    #returnValue = os.popen('ps aux | grep firefox | wc -l')
    returnValue = int(returnValue.read())
    if returnValue < 2:
        returnValue = 0
    else:
        returnValue -= 2
    res = {'running_num':returnValue,'cpu_percent':psutil.cpu_percent(),'mem_percent':psutil.virtual_memory().percent}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})

# Console
def print_object(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))

# Console
def submitRun(request):
    print("async submitRun start.")
    # 获取命令
    cmd = request.POST.get("cmd")
    callFun(cmd)
    # 返回主页//需要了解有几个脚本正在运行
    print("async submitRun done.")
    print('cmd:',cmd)
    res = {'msg':'success!'}
    #return JsonResponse(res,json_dumps_params={'ensure_ascii': False})
    return console(request)

# Console
# 给数据库进行评论
def remarkDataBase(request):
    global RAW_ROOT
    database = request.GET.get('database')
    remark = request.GET.get('remark')

    save_path = RAW_ROOT + database + '/'
    print(database,'=>',remark)
    if remark != '':
        writeTxt(remark,save_path+'remark.txt','w')
    #    updateMetaData({'$set':{'remark':remark}})
    res = {'msg':'success'}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})
        

# Console
# 读取预聚类的csv文件，构造成一个json然后显示
# 算法上应该直接可以执行，存储在db_pure_big的目录下
''' return apkforest.html
'''
def tagRawDataBase(request, database=DBNAME):
    # 读取csv文件
    global RAW_ROOT
    save_path = RAW_ROOT + database + '/'
    f = open(save_path+'info.csv','r') # 专门有用于构建的项目？
    lines = csv.reader(f)


    if os.path.exists(save_path+'abandon.txt'):
        abandon_list = readTxt(save_path+'abandon.txt') # 专门有用于构建的项目？
        print('raw abandon_list:',abandon_list)
    else:
        abandon_list = []


    #rawapkTree = collect_rawapkforest.find({},{'path':1,"app" : 1, "widget" : 1,'image_cluster_no':1}).sort("_id",1)
    rawapkTreeList = []
    max_cluster = 0
    for row in lines:
        #  如果path在抛弃清单里面，不加入
        if row[1] in abandon_list:
            print('abandon_list:',row[1])
            continue
        rawapkTreetemp = {'path':row[1],'app':row[0],"widget":'---','image_cluster_no':row[2]}
        # path为id，用path引导软删除
        rawapkTreeList.append(rawapkTreetemp)
        if int(rawapkTreetemp['image_cluster_no']) > max_cluster:
            max_cluster = int(rawapkTreetemp['image_cluster_no'])
    f.close()
    
    # 异常退出，没有进行聚类
    if len(rawapkTreeList) == 0:
        return HttpRespone('尚未进行聚类，无法人工审核该数据集.使用IC search搜索参数,IC run运行聚类')

    # 在线标注
    BaseDir= RAW_ROOT + '%s/input_data/' % database
    context = {'picturePath':PICTURE_PATH,'BaseDir':BaseDir,'rawapkTree':rawapkTreeList,'staticPath':STATIC_PATH,'current_db':database,'current_apkforest':'PRECLUSTER','new_max_cluster':max_cluster,'tagType':'rawdatabase'}
    return render(request,'Console/apkforest.html',context)
    
# Console
def submitRawDataBaseTag(request,database=DBNAME):
    '''
    tagResult = request.GET.get('tagResult')
    # 对删除的文件直接执行更名命令
    '''
    global RAW_ROOT
    BaseDir= RAW_ROOT + '%s/input_data/' % database
    save_path = RAW_ROOT + database + '/'

    widgets = request.POST.get('widgets')
    print(request.POST,'---------')
    widgets = widgets.rstrip(';')

    abandon_list = []
    for widget_path in widgets.split(';'):
        # 将传过来的文件进行改名
        abandon_list.append(widget_path)
        try:
            os.rename(BaseDir+widget_path,BaseDir+widget_path+'.abandon')
        except:
            print('not found '+BaseDir+widget_path)
    writeTxt(abandon_list,save_path+'abandon.txt','a')
    res = {'msg':'success'}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})


# Console
def apkforestlist(request):
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    client = dataBaseProcessor.getConnection()
    collist = client.collection_names()
    apkforestlist = []
    for line in collist:
        if '.' not in line and '_' not in line:
            # 作为列表之一
            apkforestlist.append((line,'/Console/apkforest/%s'  % line ))
    context = {'apkForestList':apkforestlist,'staticPath':STATIC_PATH}
    return render(request,'Console/apkforests.html',context)

# Console
def apkforest(request, apkforestName='MW_lle'):
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collect_rawapkforest = db[apkforestName]
    rawapkTree = collect_rawapkforest.find({},{'path':1,"app" : 1, "widget" : 1,'image_cluster_no':1}).sort("_id",1)
    rawapkTreeList = []
    max_cluster = 0
    for i in rawapkTree:
        rawapkTreetemp = dict(i)
        rawapkTreetemp['id'] = rawapkTreetemp['_id']
        rawapkTreeList.append(rawapkTreetemp)
        if int(rawapkTreetemp['image_cluster_no']) > max_cluster:
            max_cluster = int(rawapkTreetemp['image_cluster_no'])
    context = {'picturePath':PICTURE_PATH,'BaseDir':'/data/wangruifeng/datasets/DroidBot_Epoch/raw_data/%s/input_data/' % DBNAME,'rawapkTree':rawapkTreeList,'staticPath':STATIC_PATH,'current_db':DBNAME,'current_apkforest':apkforestName,'new_max_cluster':max_cluster,'tagType':'apkforest'}
    return render(request,'Console/apkforest.html',context)

# Console
def apkforestsubmit(request):
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    dataBaseProcessor.DBNAME = DBNAME
    dataBaseProcessor.rawApkForestName = request.POST.get('apkforestName')
    widgets = request.POST.get('widgets')
    print(request.POST,'---------')
    widgets = widgets.rstrip(';')
    idUpath = []
    for widget in widgets.split(';'):
        idUpath.append([ObjectId(widget),'-2'])
    dataBaseProcessor.updateRawAPKForest_Cluster(idUpath)
    print(idUpath)
    res = {'msg':'success'}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})

# Console
def checkAPPs(request):
    global CURRENT_APP_SET_PATH
    applist = request.GET.get('applist')
    applist = applist.rstrip('\n')
    needapplist = []
    current_app_set = set(open(CURRENT_APP_SET_PATH,'r').read().rstrip('\n').split('\n'))
    for app in applist.split('\n'):
        print('=>',app)
        if app not in current_app_set:
            needapplist.append(app)
            current_app_set.add(app)
        else:
            print(app,'hased!')
    current_app_file = open(CURRENT_APP_SET_PATH,'w')
    current_app_file.write('\n'.join(list(current_app_set)))
    
    print('needapplist:',"\n".join(needapplist))
    return JsonResponse({'needapplist':"\n".join(needapplist)})

# #<<Console---------------------------------------------------------------------------------------------------------------

# #>>Projects---------------------------------------------------------------------------------------------------------------
## Console/projects.html
# path('projects',views.projects),
## Console/subtask.html
# path('subtask/<str:projectName>/<str:subtask_name>',views.subtask),
def projects(request):
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']
            subtaskDict['link'] = '/Console/subtask/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/projects.html', context)

def subtask(request, projectName='MW_pca', subtask_name='spm_pca300_optics3'):
    #根据需要选择HttpRespone或者HttpResponse
    #dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    #dataBaseProcessor.projectName = projectName
    #dataBaseProcessor.subtask_name = subtask_name
    #dataBaseProcessor.configTableName = dataBaseProcessor.projectName+'_config'
    #dataBaseProcessor.metaDataTableName = dataBaseProcessor.projectName + '_metadata'        
    #dataBaseProcessor.apkTreeTableName = dataBaseProcessor.subtask_name+'_apktree'         
    #config = dataBaseProcessor.getConfig({'INSTANCE_NAME':projectName})
    #metadata = dataBaseProcessor.getConfig({'subtask_name':subtask_name})
    #context = {'configLists': dataBaseProcessor.getConfig()}
    interpreter = loadInterpreter(CONFIG_PATHS, projectName, subtask_name)
    config = interpreter.config
    parsingConfig = interpreter.ParsingConfig()
    metadata = interpreter.DBP.queryMetaData({'projectName':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    metadata[0]['projectName'] = projectName
    print('metadata', metadata)
    print('config', config)

    canPreview = parsingConfig['CLUSTER_PICTURE_RESULT_DIR']['isExist']
    if canPreview == False: canPreview = ' disabled="disabled"'
    else: canPreview = ''
    context = {'metadata':metadata[0], 'configLists':parsingConfig, 'staticPath':STATIC_PATH, 'language':'zh', 'clusterPictureDir':config['CLUSTER_PICTURE_RESULT_DIR'], 'canPreview':canPreview}
    #return JsonResponse({'message':'Hello world'})
    return render(request, 'Console/subtask.html', context)
    #return HttpResponse("Hello world")
# #<<Projects---------------------------------------------------------------------------------------------------------------

# #>>Gallerys---------------------------------------------------------------------------------------------------------------
## Console/gallerys.html
# path('gallerys',views.gallerys),
def gallerys(request):
    # 获取所有 parsingConfig['CLUSTER_PICTURE_RESULT_DIR']['isExist'] 为True的项目子任务
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']
            subtaskDict['cluster_link'] = '/Console/album/%s/%s/cluster/none' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDict['outlier_link'] = '/Console/album/%s/%s/outlier/none' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/gallerys.html', context)

# #<<Gallerys---------------------------------------------------------------------------------------------------------------

# #>>Tags---------------------------------------------------------------------------------------------------------------
# path('tags',views.tags),
# Console/album_outlier.html
# path('album/<str:projectName>/<str:subtask_name>/<str:galleryId>/<str:hightlightClusterId>/<int:cluster_no>',views.album),
# path('tagging/<str:projectName>/<str:subtask_name>/<str:widget_id>',views.tagging),
# # Console/evaluate.html
# path('evaluateHome',views.evaluateHome),
# path('evaluate/<str:projectName>/<str:subtask_name>',views.evaluate),
# path('evaluateSubmit',views.evaluateSubmit),
# 实际上不需要，但是先这样
# path('submitSuspects',views.submitSuspects),

def resoluteAPI(apis,stanard_android_api,method='simple'):
    if method == 'custom':
        api_type_set = set()
        for api in apis:
            package,status = isAtPackageList(api,stanard_android_api)
            if status == False:
                api_type_set.add('other')
                continue
            print('----->',package.split('.'))
            print('----->',package.split('.')[1:2])
            api_type = '.'.join(package.split('.')[1:2])#'.'.join(api.split('.')[1:3])
            # 将来可以对包建立一个map库对应起来
            api_type_set.add(api_type[:10])
        return list(api_type_set)
    else:
        api_type_set = set()
        for api in apis:
            api_type = '.'.join(api.split('.')[1:3])
            # 将来可以对包建立一个map库对应起来
            api_type_set.add(api_type[:21])
        return list(api_type_set)

def isCanShow(apps_dict):
    #{'app1':2,'app2':3,'app3'1}
    # app数量大于3
    appnum = len(list(apps_dict.keys()))
    if appnum < 2:#3
        return False
    ## 总控件数量大于5
    c = list(apps_dict.values())
    sum_c = sum(c)
    if sum_c < 3:#5
        return False
    c = [i/sum_c for i in c]
    if len(c) < 0:
        return False
    result=0; 
    '''
    for x in c: 
        result+=(-x)*math.log(x,2)
    if result < 0.91:
        return False
    '''
    return True

def fetchAppWebsiteInfo(curdbname,app):
    # 首先尝试获取存储的json文件
    global RAW_ROOT
    app_json_path = RAW_ROOT + 'app_json.json'
    try:
        app_json = readDict(app_json_path,'noordered') # 专门有用于构建的项目？
    except:
        app_json = dict()
        global ZIP_ROOT
        # 如果没有，直接读取一个当前DBNAME对应的系统文件夹，生成这种json文件
        zip_json_path = RAW_ROOT + 'app_json.json'
        # 应当从zip中读取
        raw_zip_paths = ['views_info_f_droid_1538/','views_info_google_play_13k_12011736/','views_info_google_play_13k_12021120/','views_info_google_play_13k_12071659/','views_info_google_play_1435_apps_rerun/']
        for raw_folder_path in raw_zip_paths:
            for app_folder_name in os.listdir(ZIP_ROOT+raw_folder_path):
                if 'f_droid' in raw_folder_path:
                    website = 'https://f-droid.org/en/packages/'
                else:
                    website = 'https://play.google.com/store/apps/details?id='
                if app_folder_name not in app_json:
                    app_json[app_folder_name] = dict()
                app_json[app_folder_name]['website'] = website
        writeDict(app_json,app_json_path) # 专门有用于构建的项目？

    # 正常的流程
    app_search_name = app.replace('.apk','')
    app_search_name = re.sub(r"_\d+","",app_search_name)
    website = app_json[app]['website']+app_search_name
    print('fetchAppWebsiteInfo:',website)
    return website
                    

    # jon文件中，各个app对应的库均在其中，得知库后会发送web请求，如果请求无效则更换地址，实在不行在原地址上加上标识

def displayInfoInjetor(curdbname,apkInfoTree):
    # rawapkTree: {'image_cluster_no':{"$ne":'-2'}}, {"path" : 1, "app" : 1, "widget" : 1,"method_api":1, "suspect":1}
    # apkTree: {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1}
    # apkInfoTree.append((rawapkTree[i], apkTree[i])
    
    ##### 用于给异常排序，对于每一个簇号相同的一起排序
    # 首先将所有cluster_no相同的找出，然后逐步的给他们动态排序
    cluster_no_dict = dict()
    for tree_item in apkInfoTree:
        # 当前控件的cluster_no
        cur_cluster_no = tree_item[1]['cluster_no']
        icon_name = tree_item[0]['path'].split('/')[-1]
        if cur_cluster_no in cluster_no_dict:
            cluster_no_dict[cur_cluster_no].append((tree_item[0]['widget'],tree_item[1]['outlier_score'],icon_name))
        else:
            cluster_no_dict[cur_cluster_no] = [(tree_item[0]['widget'],tree_item[1]['outlier_score'],icon_name)]
        
    for cluster_key,cluster_value in cluster_no_dict.items():
        cluster_no_dict[cluster_key].sort(key=lambda x:float(x[1]))
        
    ##### 异常排序部署阶段；插入报表信息
    for i in range(len(apkInfoTree)):
        tree_item = apkInfoTree[i]
        # 当前控件的cluster_no
        cur_cluster_no = tree_item[1]['cluster_no']
        # cluster_no_dict[cur_cluster_no] => [('2021_034342','-0.45'),('2021_034342','-0.45')]
        cur_widget_index = cluster_no_dict[cur_cluster_no].index((tree_item[0]['widget'],tree_item[1]['outlier_score']))
        apkInfoTree[i][1]['outlier_sort'] = cur_widget_index
        # 一些用于报表的属性
        apkInfoTree[i][1]['appwebsite'] = fetchAppWebsiteInfo(DBNAME,tree_item[0]['app'])

def getCheckoutIndex(cluster_list):
    # 给定一个簇列表，得出其Top1/3/5,Top20%,therhold>4.9,therhold_outlier>0.55的临界下标
    top_n_index = 0
    top_20percent_index = 0
    threshold = 0.49
    threshold_index = 0
    threshold_outlier_threshold = 0.55
    threshold_outlier_threshold_index = 0
    
    # 先按数学序数计算，最后统一减去1，注意本身就是0
    cluster_length = len(cluster_list)
    if cluster_length <= 5:
        top_n_index = 1
    elif cluster_length <= 10:
        top_n_index = 3
    else:
        top_n_index = 5
    top_20percent_index = int(cluster_length * 0.2)
    # 这是里面最后一个大于0.49的后一个项的下标，所以减1之后是最后一个大于0.49的
    # 如果没有大于0.49的，threshold_index=-1
    for index in range(cluster_length):
        if cluster_list[index][1] < therhold:
            threshold_index = index-1
            break

    return top_n_index-1,top_20percent_index-1,threshold_index

'''
1. 用户功能 <<
2. 存储评测结果 << 
3. 将管理和评测彻底分开，做好评测的主页面，要求登录才能进入评测(中午)
3. 上线使用管理界面跑程序的功能(中午)
'''
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from threading import Thread
from bson import ObjectId
import re
import time
import datetime
import bcrypt
import math
import csv
import os
from . import HelpMeDownload

#DBNAME = 'db_DroidBotMW'
#DBNAME = 'db_Droidbot1128'
#DBNAME = 'db_DroidBotMW_tfidf'
#DBNAME = 'db_Fdoidtest_1000'
DBIP = '127.0.0.1'
DBPORT = 27017
#DBNAME = 'db_googleplay_13k'
#DBNAME = 'db_f_droid_9h'
DBNAME = 'db_universal_set'
RAWAPKFOREST = 'rawapkforest'
#HOST_NAME = 'http://219.216.64.42:8000/'
HOST_NAME = 'http://219.216.64.127:8000/'
#HOST_NAME = 'http://uimanager.crepuscule.site:8601/'
STATIC_PATH = HOST_NAME + 'static'
PICTURE_PATH = 'http://219.216.64.127'
#PICTURE_PATH = 'http://127.0.0.1'
#PICTURE_PATH = 'http://uimanager.crepuscule.site:8601/static'
CONFIG_PATHS = '/home/dl/users/wangruifeng/05MisleadingWidgets/androidwidgetclustering'
CURRENT_APP_SET_PATH = '/home/dl/users/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/static/applist.txt'

# 应该可以避免而从算法系统中读出的:
RAW_ROOT = '/data/wangruifeng/datasets/DroidBot_Epoch/raw_data/'
ZIP_ROOT = '/data/wangruifeng/datasets/DroidBot_Epoch/zips/'

# #>>Basic  ---------------------------------------------------------------------------------------------------------------
# path('',views.homepage),
# path('home',views.homepage),

def isAtPackageList(api,package_list):
    import re
    # 这么做的目的是，不让android直接就匹配，要不然误进很多api
    # 正则表达式，从开头开始的小写字母或者\.，遇到大写就结束了，这样可以匹配出包名
    package_regex = re.compile('^[a-z\.]+')
    package_regex_result = package_regex.match(api)
    if package_regex_result == None:
        print('无法获取包名！')
        return '',False # 无法获取包名！
    else:
        package = package_regex_result.group(0).rstrip('.')

    print('searching >>%s<< in package_list...' % package)
    if package in package_list:
        return package,True
    return package,False

def readTxt(path):                                                                                                   
    #path += '.txt'                                                                                                       
    file_handle=open(path,mode='r')                                                                                       
    lines = file_handle.readlines()                                                                                       
    file_handle.close()                                                                                                   
    content = []                                                                                                          
    for i in lines:                                                                                                       
        content.append(i.strip('\n').strip(' '))                                                                                     
    print(path,',',len(content),' records read.')                                                                         
    return content

'''
def writeTxt(content,path):                                                                            
    #path += '.txt'                                                                                         
    file_handle=open(path,mode='w')                                                                         
    file_handle.write(content)                                                                   
    file_handle.close()                                                                                     
    print(path,',',len(content),' records writen.') 
'''

def writeTxt(content,path,mode='w'):
    #path += '.txt'
    file_handle=open(path,mode=mode)
    file_handle.write("\n".join(content))
    file_handle.close()
    print(path,',',len(content),' records writen.')

def readDict(path,readType="ordered"):
    #path += '.json'
    import json
    from collections import OrderedDict
    readfile = open(path,mode='r')
    if readType == "ordered":
        content = json.loads(readfile.read(), object_pairs_hook=OrderedDict)
    else:
        content = json.loads(readfile.read())
    readfile.close()
    print(path,',',len(content),' keys read.')
    return content

def writeDict(content,path):
    #path += '.json'
    import json
    writefile = open(path,mode='w')
    writefile.write(json.dumps(content))
    writefile.close()
    print(path,',',len(content.keys()),' keys read.')
    


# Basic
def homepage(request):
    #根据需要选择HttpRespone或者HttpResponse
    # 获取数据库信息
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']
            subtaskDict['link'] = '/Console/console/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/homepage.html', context)

def loadInterpreter(configPaths, projectName="", subtask_name=""):
    import sys, os
    sys.path.append(os.path.abspath(configPaths)) 
    sys.path.append(os.path.abspath(configPaths)+'/Assistant/') 
    import Interpreter
    from importlib import reload
    reload(Interpreter)
    # use 1, 2 to use different config file
    #self.config = configuration.initConfig(2)
    #return configuration.initConfig(1)
    if projectName == "" or subtask_name == "":
        interpreter = Interpreter.Interpreter()
        return interpreter
    interpreter = Interpreter.Interpreter(projectName+'.'+subtask_name)
    return interpreter#.ParsingConfig()

# Basic
def loadDataBase(configPaths):
    import sys, os
    sys.path.append(os.path.abspath(configPaths)+'/Base/') 
    import DataBaseProcessor
    from importlib import reload
    reload(DataBaseProcessor)
    # use 1, 2 to use different config file
    #self.config = configuration.initConfig(2)
    #return configuration.initConfig(1)
    dataBaseProcessor = DataBaseProcessor.DataBaseProcessor()
    dataBaseProcessor.DBNAME = DBNAME
    dataBaseProcessor.rawApkForestName = RAWAPKFOREST
    return dataBaseProcessor

def writeEvaluation(content):
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    findResult = dataBaseProcessor.queryUsers({'username':username})

def objectId2Time(objectid):
    timestamp = time.mktime(objectid.generation_time.timetuple())
    #dateArray = datetime.datetime.fromtimestamp(timestamp)
    #otherStyleTime = dateArray.strftime("%Y.%m.%d %H:%M")
    time_str = datetime.datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')
    return time_str

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def index(request):
    #根据需要选择HttpRespone或者HttpResponse
    return JsonResponse({'message':'Hello world'})
    #return HttpResponse("Hello world")
# #<<Basic  ---------------------------------------------------------------------------------------------------------------

# #>>Users  ---------------------------------------------------------------------------------------------------------------
# path('login',views.login),
# path('users',views.users),
# path('addUser',views.addUser),
# path('deleteUser',views.deleteUser),

def login(request):
    username = request.GET.get('username','')
    password = request.GET.get('password','')

    password = password.encode('utf-8')
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    findResult = dataBaseProcessor.queryUsers({"password":1,'job':1,'email':1},{'username':username})
    print('findResult',findResult)
    true_password = findResult[0]['password']
    if bcrypt.checkpw(password, true_password):
        print("match")
        return JsonResponse({'msg':'True','username':username})
    return JsonResponse({'msg':'False'})

def users(request):
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    findResult = dataBaseProcessor.queryUsers({'_id':1,'username':1,'job':1,'email':1})
    context = {'userList':findResult,'staticPath':STATIC_PATH}
    print('in users',findResult)
    for i in range(len(findResult)):
        findResult[i]['no'] = findResult[i]['_id']
    return render(request, 'Console/users.html', context)

# Uesrs
def addUser(request):
    username = request.GET.get('username','user001')
    password = request.GET.get('password','user001')
    email = request.GET.get('email')
    job = request.GET.get('job')
    password = password.encode('utf-8')

    salt = bcrypt.gensalt(rounds=8)
    hashed = bcrypt.hashpw(password, salt)
    print('addUser:',{"username":username,"password":password,"job":job,'email':email})
    # db operator
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    insertResult = dataBaseProcessor.saveUsers({"username":username,"password":hashed,"job":job,'email':email})
    print(insertResult)
    context = {'userList':insertResult,'staticPath':STATIC_PATH, 'msg':'Add User %s Successfully!' % username}
    return JsonResponse({'msg':'Add User Successfully!'})

def deleteUser(request):
    user_id = request.GET.get('user_id')
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    print('deleteing id=',user_id)
    deleteResult = dataBaseProcessor.deleteUser(ObjectId(user_id))
    context = {'userList':deleteResult,'staticPath':STATIC_PATH}
    print('deleteResult',deleteResult)
    return JsonResponse({'msg':'Delete Successfully!'})

# #<<Users---------------------------------------------------------------------------------------------------------------

# #>>Console ---------------------------------------------------------------------------------------------------------------
## Console/console.html
# path('console',views.console),
# path('changedb/<str:db_name>',views.chooseDataBase),
# path('changeapkforest/<str:apkforest>',views.chooseRawApkForest),
# ## 用于检查有多少算法程序在本机执行
# path('checkRun',views.checkRun),
# ## Console/submitRun.html
# path('submitRun',views.submitRun),
# ## 进行数据集的预聚类，标注,去噪
# path('rawdatabase/<str:database>',views.tagRawDataBase),
# path('tagrawdatabase',views.submitRawDataBaseTag),
# path('apkforestlist',views.apkforestlist),
# path('apkforest/<str:apkforestName>',views.apkforest),
# path('apkForestSubmit',views.apkforestsubmit),
# ## 将app检查列表化简去重
# path('checkapp',views.checkAPPs),

def console(request):
    from pymongo import MongoClient
    default_cmd = '''
#尝试kpca降维到700,300,150的效果对比
A o kpcaExampleProject
######################### DP
# 已经提前处理过

A s spm_kpca700_optics
######################### DT
DT apktree csvsets

######################### IF
#IF extif spm
IF usedefault

######################### DE
DE vector

DE cutdim kpca,700
######################### VC
VC run
#VC eval
######################### OD
OD run
#OD eval

A s spm_kpca300_optics
DE cutdim kpca,300
######################### VC
VC run
#VC eval
######################### OD
OD run
#OD eval
    '''
    connection = MongoClient(DBIP, DBPORT)
    db_list = connection.database_names()
    db_list.remove('local')
    db_list.remove('admin')

    dataBaseList = []
    for db in db_list:
        dataBaseListItem = dict()
        dataBaseListItem['name'] = db
        save_path = RAW_ROOT + db + '/'
        try:
            remark =  '\n'.join(readTxt(save_path+'remark.txt'))
        except:
            remark = 'Click to Remark'
        dataBaseListItem['remark'] = remark
        dataBaseListItem['remarkLink'] = '/Console/remarkdatabase/%s' % db
        dataBaseListItem['tagLink'] = '/Console/tagrawdatabase/%s' % db
        dataBaseListItem['chooseLink'] = '/Console/changedb/%s' % db
        dataBaseList.append(dataBaseListItem)

    print(db_list)

    # apkforestlist
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    client = dataBaseProcessor.getConnection()
    collist = client.collection_names()
    apkForestList = []
    for line in collist:
        if '.' not in line and '_' not in line:
            # 作为列表之一
            apkForestListItem = dict()
            apkForestListItem['name'] = line
            apkForestListItem['tagLink'] = '/Console/apkforest/%s'  % line
            apkForestListItem['chooseLink'] = '/Console/changeapkforest/%s' % line
            apkForestList.append(apkForestListItem)

    context = {'default_cmd':default_cmd,'apkForestList':apkForestList,'staticPath':STATIC_PATH,'dataBaseList':dataBaseList,'current_db':DBNAME,'current_apkforest':RAWAPKFOREST}
    return render(request, 'Console/console.html', context)


# Console
def chooseDataBase(request,db_name=''):
    global DBNAME
    if db_name != '':
        DBNAME = db_name 
    return console(request)

def allDataBase(request):
    connection = MongoClient(DBIP, DBPORT)
    db_list = connection.database_names()
    res = {'db_list':db_list}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})

# Console
def chooseRawApkForest(request,apkforest=''):
    global RAWAPKFOREST
    if apkforest != '':
        RAWAPKFOREST = apkforest 
    return console(request)
    

# Console
@async
def callFun(cmd):
    import os
    from subprocess import PIPE
    import psutil
    writeTxt(cmd,CONFIG_PATHS+'Assistant/cmdline.txt')
    # 使用linux命令运行
    exectuePath = 'cd '+CONFIG_PATHS
    exectuor = '/home/crepuscule/anaconda3/envs/python3.6/bin/python3.6 '
    print(exectuePath + ' && '+exectuor + 'Assistant/Interpreter.py '+CONFIG_PATHS+'Assistant/cmdline.txt')
    os.system(exectuePath + ' && '+exectuor + 'Assistant/Interpreter.py '+CONFIG_PATHS+'Assistant/cmdline.txt')
    #interpreter = loadInterpreter(CONFIG_PATHS)
    #interpreter.sequenceCMD(cmd,'S')
    # 使用ps命令看一下有没有相关程序运行就行了，然后通过回调ajax返回就可以了

# Console
def checkRun(request):
    import os
    import psutil
    returnValue = os.popen('ps aux | grep "/home/crepuscule/anaconda3/envs/python3.6/bin/python3.6 Assistant/Interpreter.py" | wc -l')
    #returnValue = os.popen('ps aux | grep firefox | wc -l')
    returnValue = int(returnValue.read())
    if returnValue < 2:
        returnValue = 0
    else:
        returnValue -= 2
    res = {'running_num':returnValue,'cpu_percent':psutil.cpu_percent(),'mem_percent':psutil.virtual_memory().percent}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})

# Console
def print_object(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))

# Console
def submitRun(request):
    print("async submitRun start.")
    # 获取命令
    cmd = request.POST.get("cmd")
    callFun(cmd)
    # 返回主页//需要了解有几个脚本正在运行
    print("async submitRun done.")
    print('cmd:',cmd)
    res = {'msg':'success!'}
    #return JsonResponse(res,json_dumps_params={'ensure_ascii': False})
    return console(request)

# Console
# 给数据库进行评论
def remarkDataBase(request):
    global RAW_ROOT
    database = request.GET.get('database')
    remark = request.GET.get('remark')

    save_path = RAW_ROOT + database + '/'
    print(database,'=>',remark)
    if remark != '':
        writeTxt(remark,save_path+'remark.txt','w')
    #    updateMetaData({'$set':{'remark':remark}})
    res = {'msg':'success'}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})
        

# Console
# 读取预聚类的csv文件，构造成一个json然后显示
# 算法上应该直接可以执行，存储在db_pure_big的目录下
''' return apkforest.html
'''
def tagRawDataBase(request, database=DBNAME):
    # 读取csv文件
    global RAW_ROOT
    save_path = RAW_ROOT + database + '/'
    f = open(save_path+'info.csv','r') # 专门有用于构建的项目？
    lines = csv.reader(f)


    if os.path.exists(save_path+'abandon.txt'):
        abandon_list = readTxt(save_path+'abandon.txt') # 专门有用于构建的项目？
        print('raw abandon_list:',abandon_list)
    else:
        abandon_list = []


    #rawapkTree = collect_rawapkforest.find({},{'path':1,"app" : 1, "widget" : 1,'image_cluster_no':1}).sort("_id",1)
    rawapkTreeList = []
    max_cluster = 0
    for row in lines:
        #  如果path在抛弃清单里面，不加入
        if row[1] in abandon_list:
            print('abandon_list:',row[1])
            continue
        rawapkTreetemp = {'path':row[1],'app':row[0],"widget":'---','image_cluster_no':row[2]}
        # path为id，用path引导软删除
        rawapkTreeList.append(rawapkTreetemp)
        if int(rawapkTreetemp['image_cluster_no']) > max_cluster:
            max_cluster = int(rawapkTreetemp['image_cluster_no'])
    f.close()
    
    # 异常退出，没有进行聚类
    if len(rawapkTreeList) == 0:
        return HttpRespone('尚未进行聚类，无法人工审核该数据集.使用IC search搜索参数,IC run运行聚类')

    # 在线标注
    BaseDir= RAW_ROOT + '%s/input_data/' % database
    context = {'picturePath':PICTURE_PATH,'BaseDir':BaseDir,'rawapkTree':rawapkTreeList,'staticPath':STATIC_PATH,'current_db':database,'current_apkforest':'PRECLUSTER','new_max_cluster':max_cluster,'tagType':'rawdatabase'}
    return render(request,'Console/apkforest.html',context)
    
# Console
def submitRawDataBaseTag(request,database=DBNAME):
    '''
    tagResult = request.GET.get('tagResult')
    # 对删除的文件直接执行更名命令
    '''
    global RAW_ROOT
    BaseDir= RAW_ROOT + '%s/input_data/' % database
    save_path = RAW_ROOT + database + '/'

    widgets = request.POST.get('widgets')
    print(request.POST,'---------')
    widgets = widgets.rstrip(';')

    abandon_list = []
    for widget_path in widgets.split(';'):
        # 将传过来的文件进行改名
        abandon_list.append(widget_path)
        try:
            os.rename(BaseDir+widget_path,BaseDir+widget_path+'.abandon')
        except:
            print('not found '+BaseDir+widget_path)
    writeTxt(abandon_list,save_path+'abandon.txt','a')
    res = {'msg':'success'}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})


# Console
def apkforestlist(request):
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    client = dataBaseProcessor.getConnection()
    collist = client.collection_names()
    apkforestlist = []
    for line in collist:
        if '.' not in line and '_' not in line:
            # 作为列表之一
            apkforestlist.append((line,'/Console/apkforest/%s'  % line ))
    context = {'apkForestList':apkforestlist,'staticPath':STATIC_PATH}
    return render(request,'Console/apkforests.html',context)

# Console
def apkforest(request, apkforestName='MW_lle'):
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collect_rawapkforest = db[apkforestName]
    rawapkTree = collect_rawapkforest.find({},{'path':1,"app" : 1, "widget" : 1,'image_cluster_no':1}).sort("_id",1)
    rawapkTreeList = []
    max_cluster = 0
    for i in rawapkTree:
        rawapkTreetemp = dict(i)
        rawapkTreetemp['id'] = rawapkTreetemp['_id']
        rawapkTreeList.append(rawapkTreetemp)
        if int(rawapkTreetemp['image_cluster_no']) > max_cluster:
            max_cluster = int(rawapkTreetemp['image_cluster_no'])
    context = {'picturePath':PICTURE_PATH,'BaseDir':'/data/wangruifeng/datasets/DroidBot_Epoch/raw_data/%s/input_data/' % DBNAME,'rawapkTree':rawapkTreeList,'staticPath':STATIC_PATH,'current_db':DBNAME,'current_apkforest':apkforestName,'new_max_cluster':max_cluster,'tagType':'apkforest'}
    return render(request,'Console/apkforest.html',context)

# Console
def apkforestsubmit(request):
    global DBNAME
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    dataBaseProcessor.DBNAME = DBNAME
    dataBaseProcessor.rawApkForestName = request.POST.get('apkforestName')
    widgets = request.POST.get('widgets')
    print(request.POST,'---------')
    widgets = widgets.rstrip(';')
    idUpath = []
    for widget in widgets.split(';'):
        idUpath.append([ObjectId(widget),'-2'])
    dataBaseProcessor.updateRawAPKForest_Cluster(idUpath)
    print(idUpath)
    res = {'msg':'success'}
    return JsonResponse(res,json_dumps_params={'ensure_ascii': False})

# Console
def checkAPPs(request):
    global CURRENT_APP_SET_PATH
    applist = request.GET.get('applist')
    applist = applist.rstrip('\n')
    needapplist = []
    current_app_set = set(open(CURRENT_APP_SET_PATH,'r').read().rstrip('\n').split('\n'))
    for app in applist.split('\n'):
        print('=>',app)
        if app not in current_app_set:
            needapplist.append(app)
            current_app_set.add(app)
        else:
            print(app,'hased!')
    current_app_file = open(CURRENT_APP_SET_PATH,'w')
    current_app_file.write('\n'.join(list(current_app_set)))
    
    print('needapplist:',"\n".join(needapplist))
    return JsonResponse({'needapplist':"\n".join(needapplist)})

# #<<Console---------------------------------------------------------------------------------------------------------------

# #>>Projects---------------------------------------------------------------------------------------------------------------
## Console/projects.html
# path('projects',views.projects),
## Console/subtask.html
# path('subtask/<str:projectName>/<str:subtask_name>',views.subtask),
def projects(request):
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']
            subtaskDict['link'] = '/Console/subtask/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/projects.html', context)

def subtask(request, projectName='MW_pca', subtask_name='spm_pca300_optics3'):
    #根据需要选择HttpRespone或者HttpResponse
    #dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    #dataBaseProcessor.projectName = projectName
    #dataBaseProcessor.subtask_name = subtask_name
    #dataBaseProcessor.configTableName = dataBaseProcessor.projectName+'_config'
    #dataBaseProcessor.metaDataTableName = dataBaseProcessor.projectName + '_metadata'        
    #dataBaseProcessor.apkTreeTableName = dataBaseProcessor.subtask_name+'_apktree'         
    #config = dataBaseProcessor.getConfig({'INSTANCE_NAME':projectName})
    #metadata = dataBaseProcessor.getConfig({'subtask_name':subtask_name})
    #context = {'configLists': dataBaseProcessor.getConfig()}
    interpreter = loadInterpreter(CONFIG_PATHS, projectName, subtask_name)
    config = interpreter.config
    parsingConfig = interpreter.ParsingConfig()
    metadata = interpreter.DBP.queryMetaData({'projectName':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    metadata[0]['projectName'] = projectName
    print('metadata', metadata)
    print('config', config)

    canPreview = parsingConfig['CLUSTER_PICTURE_RESULT_DIR']['isExist']
    if canPreview == False: canPreview = ' disabled="disabled"'
    else: canPreview = ''
    context = {'metadata':metadata[0], 'configLists':parsingConfig, 'staticPath':STATIC_PATH, 'language':'zh', 'clusterPictureDir':config['CLUSTER_PICTURE_RESULT_DIR'], 'canPreview':canPreview}
    #return JsonResponse({'message':'Hello world'})
    return render(request, 'Console/subtask.html', context)
    #return HttpResponse("Hello world")
# #<<Projects---------------------------------------------------------------------------------------------------------------

# #>>Gallerys---------------------------------------------------------------------------------------------------------------
## Console/gallerys.html
# path('gallerys',views.gallerys),
def gallerys(request):
    # 获取所有 parsingConfig['CLUSTER_PICTURE_RESULT_DIR']['isExist'] 为True的项目子任务
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']
            subtaskDict['cluster_link'] = '/Console/album/%s/%s/cluster/none' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDict['outlier_link'] = '/Console/album/%s/%s/outlier/none' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/gallerys.html', context)

# #<<Gallerys---------------------------------------------------------------------------------------------------------------

# #>>Tags---------------------------------------------------------------------------------------------------------------
# path('tags',views.tags),
# Console/album_outlier.html
# path('album/<str:projectName>/<str:subtask_name>/<str:galleryId>/<str:hightlightClusterId>/<int:cluster_no>',views.album),
# path('tagging/<str:projectName>/<str:subtask_name>/<str:widget_id>',views.tagging),
# # Console/evaluate.html
# path('evaluateHome',views.evaluateHome),
# path('evaluate/<str:projectName>/<str:subtask_name>',views.evaluate),
# path('evaluateSubmit',views.evaluateSubmit),
# 实际上不需要，但是先这样
# path('submitSuspects',views.submitSuspects),

def resoluteAPI(apis,stanard_android_api,method='simple'):
    if method == 'custom':
        api_type_set = set()
        for api in apis:
            package,status = isAtPackageList(api,stanard_android_api)
            if status == False:
                api_type_set.add('other')
                continue
            print('----->',package.split('.'))
            print('----->',package.split('.')[1:2])
            api_type = '.'.join(package.split('.')[1:2])#'.'.join(api.split('.')[1:3])
            # 将来可以对包建立一个map库对应起来
            api_type_set.add(api_type[:10])
        return list(api_type_set)
    else:
        api_type_set = set()
        for api in apis:
            api_type = '.'.join(api.split('.')[1:3])
            # 将来可以对包建立一个map库对应起来
            api_type_set.add(api_type[:21])
        return list(api_type_set)

def isCanShow(apps_dict):
    #{'app1':2,'app2':3,'app3'1}
    # app数量大于3
    appnum = len(list(apps_dict.keys()))
    if appnum < 2:#3
        return False
    ## 总控件数量大于5
    c = list(apps_dict.values())
    sum_c = sum(c)
    if sum_c < 3:#5
        return False
    c = [i/sum_c for i in c]
    if len(c) < 0:
        return False
    result=0; 
    '''
    for x in c: 
        result+=(-x)*math.log(x,2)
    if result < 0.91:
        return False
    '''
    return True

def fetchAppWebsiteInfo(curdbname,app):
    # 首先尝试获取存储的json文件
    global RAW_ROOT
    app_json_path = RAW_ROOT + 'app_json.json'
    try:
        app_json = readDict(app_json_path,'noordered') # 专门有用于构建的项目？
    except:
        app_json = dict()
        global ZIP_ROOT
        # 如果没有，直接读取一个当前DBNAME对应的系统文件夹，生成这种json文件
        zip_json_path = RAW_ROOT + 'app_json.json'
        # 应当从zip中读取
        raw_zip_paths = ['views_info_f_droid_1538/','views_info_google_play_13k_12011736/','views_info_google_play_13k_12021120/','views_info_google_play_13k_12071659/','views_info_google_play_1435_apps_rerun/']
        for raw_folder_path in raw_zip_paths:
            for app_folder_name in os.listdir(ZIP_ROOT+raw_folder_path):
                if 'f_droid' in raw_folder_path:
                    website = 'https://f-droid.org/en/packages/'
                else:
                    website = 'https://play.google.com/store/apps/details?id='
                if app_folder_name not in app_json:
                    app_json[app_folder_name] = dict()
                app_json[app_folder_name]['website'] = website
        writeDict(app_json,app_json_path) # 专门有用于构建的项目？

    # 正常的流程
    app_search_name = app.replace('.apk','')
    app_search_name = re.sub(r"_\d+","",app_search_name)
    website = app_json[app]['website']+app_search_name
    print('fetchAppWebsiteInfo:',website)
    return website
                    

    # jon文件中，各个app对应的库均在其中，得知库后会发送web请求，如果请求无效则更换地址，实在不行在原地址上加上标识

def displayInfoInjetor(curdbname,apkInfoTree):
    # rawapkTree: {'image_cluster_no':{"$ne":'-2'}}, {"path" : 1, "app" : 1, "widget" : 1,"method_api":1, "suspect":1}
    # apkTree: {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1}
    # apkInfoTree.append((rawapkTree[i], apkTree[i])
    
    ##### 用于给异常排序，对于每一个簇号相同的一起排序
    # 首先将所有cluster_no相同的找出，然后逐步的给他们动态排序
    cluster_no_dict = dict()
    for tree_item in apkInfoTree:
        # 当前控件的cluster_no
        cur_cluster_no = tree_item[1]['cluster_no']
        icon_name = tree_item[0]['path'].split('/')[-1]
        if cur_cluster_no in cluster_no_dict:
            cluster_no_dict[cur_cluster_no].append((tree_item[0]['widget'],tree_item[1]['outlier_score'],icon_name))
        else:
            cluster_no_dict[cur_cluster_no] = [(tree_item[0]['widget'],tree_item[1]['outlier_score'],icon_name)]
        
    for cluster_key,cluster_value in cluster_no_dict.items():
        cluster_no_dict[cluster_key].sort(key=lambda x:float(x[1]))
        
    ##### 异常排序部署阶段；插入报表信息
    for i in range(len(apkInfoTree)):
        tree_item = apkInfoTree[i]
        # 当前控件的cluster_no
        cur_cluster_no = tree_item[1]['cluster_no']
        # cluster_no_dict[cur_cluster_no] => [('2021_034342','-0.45'),('2021_034342','-0.45')]
        cur_widget_index = cluster_no_dict[cur_cluster_no].index((tree_item[0]['widget'],tree_item[1]['outlier_score']))
        apkInfoTree[i][1]['outlier_sort'] = cur_widget_index
        # 一些用于报表的属性
        apkInfoTree[i][1]['appwebsite'] = fetchAppWebsiteInfo(DBNAME,tree_item[0]['app'])
    
    coverIndexStatistics(apkInfoTree,cluster_no_dict)

def getCheckoutIndex(cluster_list):
    # 给定一个簇列表，得出其Top1/3/5,Top20%,therhold>4.9,therhold_outlier>0.55的临界下标
    top_n_index = 0
    top_20percent_index = 0
    threshold = 0.49
    threshold_index = 0
    threshold_outlier_threshold = 0.55
    threshold_outlier_threshold_index = 0
    
    # 先按数学序数计算，最后统一减去1，注意本身就是0
    cluster_length = len(cluster_list)
    if cluster_length <= 5:
        top_n_index = 1
    elif cluster_length <= 10:
        top_n_index = 3
    else:
        top_n_index = 5
    top_20percent_index = int(cluster_length * 0.2)
    # 这是里面最后一个大于0.49的后一个项的下标，所以减1之后是最后一个大于0.49的
    # 如果没有大于0.49的，threshold_index=-1
    for index in range(cluster_length):
        if cluster_list[index][1] < therhold:
            threshold_index = index-1
            break

    return top_n_index-1,top_20percent_index-1,threshold_index

# 对当前控件cover的好坏
def coverIndexStatistics(apkInfoTree,cluster_no_dict):
    # 首先读出needcover的控件名，注意只需要最后.png即可
    need_cover_icon = readTxt(COVER_ICON_TXT_PATH)
    for i in range(len(need_cover_icon)):
        need_cover_icon[i] = need_cover_icon[i].split('/')[-1]
    cover_icon_csv = []
    # 对于每一个簇，检查是否具有列表中的icon
    # cluster_no_dict[cur_cluster_no].append((tree_item[0]['widget'],tree_item[1]['outlier_score'],tree_item[0]['path'].split('/')[-1]))
    for cluster_key,cluster_value in cluster_no_dict.items():
        # 每个cluster_value 均是一个簇，簇由列表构成，按顺序排列
        # 可以开发一个函数专门获取每个数组中top几的下标，比较need_cover_icon中出现的下标与这下下标即可
        for icon_item_index in range(len(cluster_no_dict[cluster_key])):
            cluster_list = cluster_no_dict[cluster_key]
            # 在need_cover_icon内则统计: 如有在其中，统计它是否在Top1/3/5,Top20%,therhold>4.9,therhold_outlier>0.55中，记录在csv中
            if cluster_list[icon_item_index][2] in need_cover_icon: 
                top_n_index, top_20percent_index,threshold_index = getCheckoutIndex(cluster_list)
                is_top_n_hit = icon_item_index <= top_n_index
                is_top_20percent_hit = icon_item_index <= top_20percent_index
                is_threshold_hit = icon_item_index <= threshold_index
                hit_statistics = is_top_n_hit or is_top_20percent_hit or is_threshold_hit
                cover_icon_csv.append([cluster_list[icon_item_index][2],cluster_key,is_hit,icon_item_index,len(cluster_no_dict[cluster_key]),is_top_n_hit,is_top_20percent_hit,is_threshold_hit])
            
    headers = ['控件icon名','包含簇号','是否命中','簇内排序','簇内控件总数','top-1,3,5命中','top-20%命中','Threshold0.49命中']
	with open(COVER_ICON_CSV_PATH,'w')as f:
		f_csv = csv.writer(f)
		f_csv.writerow(headers)
		f_csv.writerows(cover_icon_csv)

    

# 评测目前主要看的函数#$#$#$
# 1. 需要将控件的异常排名搞出来
def album(request, projectName='MW_lle', subtask_name='spm_lle150_optics3', galleryId='',hightlightClusterId='',cluster_no=0):
    global DBNAME
    if hightlightClusterId == 'none':
        hightlightCluster = hightlightId = ''
    else:
        hightlightCluster,hightlightId = hightlightClusterId.split('.')
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    dataBaseProcessor.projectName = projectName
    dataBaseProcessor.subtask_name = subtask_name
    dataBaseProcessor.configTableName = dataBaseProcessor.projectName+'_config'
    dataBaseProcessor.metaDataTableName = dataBaseProcessor.projectName + '_metadata'        
    dataBaseProcessor.apkTreeTableName = dataBaseProcessor.projectName+'__'+dataBaseProcessor.subtask_name+'_apktree'         
    #print('what??', dataBaseProcessor.configTableName , dataBaseProcessor.metaDataTableName, dataBaseProcessor.apkTreeTableName)
    config = dataBaseProcessor.getConfig()
    metadata = dataBaseProcessor.queryMetaData({'project_name':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1,"rawapkforestname":1,"remark":1}) 
    dataBaseProcessor.rawApkForestName = metadata[0]['rawapkforestname']
    rawapkTree = dataBaseProcessor.queryRawAPKTree({'image_cluster_no':{"$ne":'-2'}}, {"path" : 1, "app" : 1, "widget" : 1,"method_api":1, "suspect":1})
    apkTree = dataBaseProcessor.queryAPKTree({}, {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1})
    #print(rawapkTree)
    #print(apkTree)
    print('what?',metadata)
    #stanard_android_api = readTxt('/home/dl/users/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/MisleadingWidgetsDetective/type.txt')
    #stanard_android_api = readTxt('/core/kernel/01work/02project/system/AndroidUIUnderstanding/05MisleadingWidget/process/MisleadingWidgetsDetective/MisleadingWidgetsDetective/type.txt')

    apkInfoTree = []
    rawapkTree[0]['api_type'] = []
    # 将簇信息存入一个字典，这样可以统计出每个簇有多少个控件，分属于多少应用
    cluster_info_dict = dict()
    cluster_show_dict = dict()
    app_statisic_dict = dict()
    # 将rawAPITree中的信息补充到apkTree当中，最后存入到apkInfoTree中
    for i in range(len(rawapkTree)):
        # 用于统计各簇的数量>>>>
        # 会有各簇下各应用数量的统计,每次更新时都检查状态，如果一个簇内数量>5个，表为可以显示can_show
        # 同时统计每个簇内应用纯度(熵)，低于某个纯度则标为low_app_abundance.即熵越小，不确定性越小，丰度越低，越是不要显示
        if apkTree[i]['cluster_no'] not in cluster_info_dict:
            cluster_info_dict[apkTree[i]['cluster_no']] = dict()
            cluster_info_dict[apkTree[i]['cluster_no']][rawapkTree[i]['app']] = 1
        else:
            if rawapkTree[i]['app'] not in cluster_info_dict[apkTree[i]['cluster_no']]:
                cluster_info_dict[apkTree[i]['cluster_no']][rawapkTree[i]['app']] = 1
            else:
                cluster_info_dict[apkTree[i]['cluster_no']][rawapkTree[i]['app']] +=1
        cluster_show_dict[apkTree[i]['cluster_no']] = isCanShow(cluster_info_dict[apkTree[i]['cluster_no']])
        # 统计各簇中控件数量结束<<<<
        if rawapkTree[i]['_id'] != apkTree[i]['raw_id']:
            print('Wrong!!')
        apkTree[i]['isOutlier'] = ''
        apkTree[i]['outlier_score'] = apkTree[i]['outlier_score'][:5]
        #if float(apkTree[i]['outlier_score']) <= -0.55:
        if float(apkTree[i]['outlier_score']) <= 1:
        #if float(apkTree[i]['outlier_score']) > 3:
            apkTree[i]['isOutlier'] = 'outlier'
        rawapkTree[i]['widget'] = ''.join(rawapkTree[i]['widget'].split(', '))
        apkTree[i]['id'] = str(apkTree[i]['raw_id'])

        if apkTree[i]['id'] == hightlightId and apkTree[i]['cluster_no'] == hightlightCluster:
            apkTree[i]['hightlight'] = 'hightlight'
        if galleryId == 'evaluate':
            rawapkTree[i]['api_type'] = rawapkTree[i]['method_api']#resoluteAPI(rawapkTree[i]['api'],stanard_android_api,'simple')#
            rawapkTree[i]['api_string'] = '  '.join(rawapkTree[i]['method_api'])
            apkInfoTree.append((rawapkTree[i], apkTree[i]))

    if galleryId == 'evaluate':
        apkInfoTree_swap = []
        new_cluster_no_dict = dict()
        new_cluster_no_count = 0
        for i in range(len(rawapkTree)):
            if cluster_show_dict[apkTree[i]['cluster_no']] == True:
                if apkInfoTree[i][1]['cluster_no'] not in new_cluster_no_dict:
                    apkInfoTree[i][1]['new_cluster_no'] = new_cluster_no_count
                    new_cluster_no_dict[apkInfoTree[i][1]['cluster_no']] = new_cluster_no_count
                    new_cluster_no_count += 1
                else:
                    apkInfoTree[i][1]['new_cluster_no'] = new_cluster_no_dict[apkInfoTree[i][1]['cluster_no']]
                apkInfoTree_swap.append(apkInfoTree[i])
    else:
        apkInfoTree_swap = apkInfoTree
        new_cluster_no_count = 0

    # 给异常控件排序，使用函数,p给异常控件加入报表的信息
    displayInfoInjetor(DBNAME,apkInfoTree_swap)

    context = {'cluster_no':cluster_no,'BaseDir':config['INPUT_DATA_DIR'], 'metadata':metadata[0], 'apkInfoTree':apkInfoTree_swap, 'apkTree':apkTree, 'max_cluster':metadata[0]['clusters'], 'cluster_num':range(int(metadata[0]['clusters'])),'new_max_cluster':new_cluster_no_count, 'staticPath':STATIC_PATH,'picturePath':PICTURE_PATH, 'language':'zh','hightlightCluster':hightlightCluster,'averAPIs':len(rawapkTree[0]['api_type']),'current_db':DBNAME,'cluster_show_dict':cluster_show_dict}
    #print(context)

    if galleryId == 'outlier':
        return render(request, 'Console/album_outlier.html', context)
    elif galleryId == 'tagging':
        return render(request, 'Console/album_tagging.html', context)
    elif galleryId == 'evaluate':
        return render(request, 'Console/evaluateCluster.html', context)
    else:
        return render(request, 'Console/album_cluster.html', context)


def tags(request):
    # 获取所有 parsingConfig['CLUSTER_PICTURE_RESULT_DIR']['isExist'] 为True的项目子任务
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']

            try:
                dataBaseProcessor.project_name = subtaskDict['projectName']
                dataBaseProcessor.subtask_name = subtaskDict['subtaskName']
                dataBaseProcessor.metaDataTableName = dataBaseProcessor.project_name + '_metadata'        
                metadata = dataBaseProcessor.queryMetaData({'remark':1}) 
                metadata = metadata[0]['remark']
            except:
                metadata = 'Nothing'
            subtaskDict['remark'] = metadata
            # 由于evaluate加入，更改
            #subtaskDict['tagging_link'] = '/Console/tagging/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDict['tagging_link'] = '/Console/evaluate/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/tags.html', context)

def tagging(request, projectName='MW_lle', subtask_name='spm_lle150_optics3', widget_id=''):
    return album(request, projectName, subtask_name, 'tagging')

    # 首先要求登录
def evaluateHome(request):
    username_session = request.session.get('username',None)
    if username_session == None: 
        needLogin = True
    else:
        needLogin = False
    context = { 'staticPath':STATIC_PATH, 'needLogin': needLogin, 'username':username_session}
    return render(request,'Console/evaluateHome.html',context)

# 异常
def evaluate(request,projectName='MW_pca',subtask_name='spm_pca300_optics3'):
    # 获取所有outlier的控件
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    dataBaseProcessor.projectName = projectName
    dataBaseProcessor.subtask_name = subtask_name
    dataBaseProcessor.configTableName = dataBaseProcessor.projectName+'_config'
    dataBaseProcessor.metaDataTableName = dataBaseProcessor.projectName + '_metadata'        
    dataBaseProcessor.apkTreeTableName =dataBaseProcessor.projectName+'__'+dataBaseProcessor.subtask_name+'_apktree'         
    #print('what??', dataBaseProcessor.configTableName , dataBaseProcessor.metaDataTableName, dataBaseProcessor.apkTreeTableName)
    config = dataBaseProcessor.getConfig()
    rawapkTree = dataBaseProcessor.queryRawAPKTree({'image_cluster_no':{"$ne":'-2'}}, {"path" : 1, "app" : 1, "widget" : 1})
    apkTree = dataBaseProcessor.queryAPKTree({}, {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1})
    #metadata = dataBaseProcessor.queryMetaData({'projectName':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    metadata = dataBaseProcessor.queryMetaData({'project_name':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1,"rawapkforestname":1}) 
    dataBaseProcessor.rawApkForestName = metadata[0]['rawapkforestname']
    print('evaluate starting...')
    metadata[0]['projectName'] = projectName

    apkInfoTree = []
    if apkTree == []:
        return HttpResponse('该项目下没有已运行完成的项目.')
    if 'outlier_score' not in apkTree[0]:
        return HttpResponse('该项目还未进行异常检测.')

    #pageSize = 12
    #curPageSize = 12
    pageSize = 1
    curPageSize = 1
    page = 0
    maxPage = 0
    for i in range(len(rawapkTree)):
        if rawapkTree[i]['_id'] != apkTree[i]['raw_id']:
            print('Wrong!!')
        apkTree[i]['isOutlier'] = ''
        apkTree[i]['outlier_score'] = apkTree[i]['outlier_score'][:5]
        #if float(apkTree[i]['outlier_score']) <= -0.55:
        if float(apkTree[i]['outlier_score']) <= 1:
        #if float(apkTree[i]['outlier_score']) > :
            apkTree[i]['isOutlier'] = 'outlier'
            # 现在只有是outlier的才被加入
            rawapkTree[i]['widget'] = ''.join(rawapkTree[i]['widget'].split(', '))
            apkTree[i]['id'] = str(apkTree[i]['raw_id'])
            curPageSize -= 1
            if curPageSize == 0:
                curPageSize = 12
                page += 1
                maxPage = page
            apkTree[i]['page'] = str(page)
            apkInfoTree.append((rawapkTree[i], apkTree[i]))

    context = {'BaseDir':config['INPUT_DATA_DIR'], 'metadata':metadata[0], 'outlierapkInfoTree':apkInfoTree, 'apkTree':apkTree, 'max_cluster':metadata[0]['clusters'], 'cluster_num':range(int(metadata[0]['clusters'])), 'staticPath':STATIC_PATH,'picturePath':PICTURE_PATH ,'language':'zh','max_page':maxPage}
    #print(context)

    return render(request, 'Console/evaluate.html', context)

def evaluateSubmit(request):
    #username = request.POST.get('username')
    score = request.POST.get('score')
    #writeEvaluation({'username':username,'score':score})
    context = {'staticPath':STATIC_PATH}
    return render(request, 'Console/evaluateDone.html', context)

def getWebCachefromVPS(website,platform=''):
    print('getWebCachefromVPS>>>')
    global RAW_ROOT
    if 'f-droid' in website:
        cache_html_name = website.replace('https://f-droid.org/en/packages/','')+'-'+platform+'.html'
    else:
        cache_html_name = website.split('=')[-1]+'-'+platform+'.html'
    cache_path = RAW_ROOT+'cachehtmls'
    if not os.path.exists(cache_path+'/'+cache_html_name):
        HelpMeDownload.downloadExecuter(website,cache_html_name,cache_path,'wget')
    print('<<<getWebCachefromVPS')
    return cache_path+'/'+cache_html_name

def getInfofromGooglePlay(website):
    # logo: class="xSyT2c"
    # appname: h1 class="AHFaub"
    # contact: span "hrTbp euBY6b"
    from bs4 import BeautifulSoup

    cache_html_path = getWebCachefromVPS(website,'googleplay')
    if not os.path.exists(cache_html_path):
        print('visist error! Return None')
        return None,None,None,None

    #html = requests.get(website,headers=headers,proxies=proxies)
    #soup = BeautifulSoup(html.content,'lxml')
    soup = BeautifulSoup(open(cache_html_path),'html.parser')

    try:
        logo = soup.find('img', {'class', 'T75of sHb2Xb'}).get('src')
        appname = soup.find('h1', {'class', 'AHFaub'}).span.string
        contact = soup.find('a', {'class', 'hrTbp euBY6b'}).string
    except:
        print('this page might not exist.')
        return None,None,None,None

    return logo,appname,contact,''

    
def getInfofromFdroid(website):
    # logo: "article-area" > class "package-icon"
    # appname: "article-area" > class "package-name"
    # contact: "package-links" > Issue Tracker
    from bs4 import BeautifulSoup
    '''
    from fake_useragent import UserAgent
    import requests
    ua=UserAgent()
    headers={"User-Agent":ua.random}

    html = requests.get(website,headers=headers)
    if html.status_code != 200:
        print('status_code:',html.status_code,' error!')
        return None,None,None,None
    '''
    cache_html_path = getWebCachefromVPS(website,'fdroid')
    if not os.path.exists(cache_html_path):
        print('visist error! Return None')
        return None,None,None,None
    soup = BeautifulSoup(open(cache_html_path),'html.parser')

    try:
        main = soup.find('div', {'class', 'article-area'})
        logo = main.article.header.img.get('src')
        appname = main.article.header.div.h3.string
        # 去除空白字符
        appname = appname.strip()

        contacts = soup.select('.package-links > li >  a')
        contact = ''
        for item in contacts:
            if item.string == 'Issue Tracker':
                contact = item.get('href')
                break
        download = soup.find('p',{'class','package-version-download'}).b.a.get('href')
    except:
        print('this page might not exist.')
        return None,None,None,None

    return logo,appname,contact,download

def getInfofromApkfab(website):
    # https://apkfab.com/free-apk-download?q=
    # logo: "article-area" > class "package-icon"
    # appname: "article-area" > class "package-name"
    # contact: "package-links" > Issue Tracker
    from bs4 import BeautifulSoup

    # 首先进行网址转化:
    website = 'https://apkfab.com/free-apk-download?q='+website.split('=')[-1]
    cache_html_path = getWebCachefromVPS(website,'apkfab')
    if not os.path.exists(cache_html_path):
        print('visist error! Return None')
        return None,None,None,None

    #html = requests.get(website,headers=headers,proxies=proxies)
    #soup = BeautifulSoup(html.content,'lxml')
    soup = BeautifulSoup(open(cache_html_path),'html.parser')

    
    logos = soup.select('.packageInfo > a > img')
    if len(logos) == 0:
        logos = soup.select('.packageInfo > div > img')
    logo = logos[0].get('src')
    # = main.find('a[class="title"]')
    appnames = soup.select('.packageInfo > div > a')
    appnames.extend(soup.select('.packageInfo > div > div'))
    appname = download = ''
    for item in appnames:
        #print('=>',item)
        if 'title' in item.get('class'):
            appname = item.string
            if 'href' in item.attrs:
                download = item.get('href')
            break
            '''
    except:
        print('this page might not exist.')
        return None,None,None,None
        '''
    if download == '':
        download = website
    return logo,appname,'',download

def submitSuspects(request):
    suspects = request.GET.get('suspects')
    suspects = suspects.rstrip(';').split(';')
    print('---->submit suspects:',suspects)
    # 连接数据库，提交标为suspects的状态
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    print('prepare to submit suspects:')

    #对idUpath更改从而更新数据库记录是否suspect
    idUpath = dataBaseProcessor.queryAllPath() # 这里就是从原apktree获取的 
    for i in range(len(idUpath)):
        #idUpath[i][1] = {"$set":{"cluster":str(clusterLabels[i])}}
        # _id字段保留，对1字段进行修改改为image_cluster_no
        if str(idUpath[i][0]) in suspects:
            idUpath[i][1] = 'suspect btn-warning'
            print(str(idUpath[i][0]),idUpath[i][1])
        else:
            idUpath[i][1] = 'notsuspect btn-default'
    dataBaseProcessor.updateRawAPKForest_Suspect(idUpath)

    # 数据库完成，，，接下来获取更多信息
    suspects_app = request.GET.get('suspects_app')
    suspects_app = suspects_app.rstrip(';').split(';')
    print('---->suspects_app:',suspects_app)
    return_website = []
    for app in suspects_app:
        website = fetchAppWebsiteInfo(DBNAME,app)
        if 'f-droid' in website:
            return_website.append( getInfofromFdroid(website) )
        else:
            google_logo = google_appname = google_contact = google_download = ''
            result2 = getInfofromApkfab(website) 
            #print('#>result2',result2)
            if result2 != (None,None,None,None):
                google_logo = result2[0]
                google_appname = result2[1]
                google_download = result2[3]
            result1 = getInfofromGooglePlay(website)
            #print('#result1>',result1)
            if result1 != (None,None,None,None):
                if google_logo != '':google_logo = result1[0]
                if google_appname != '':google_appname = result1[1]
                google_contact = result1[2]
            result = (google_logo , google_appname , google_contact , google_download  )
            return_website.append(result)
    print('======>return_website:',return_website)
    return JsonResponse({'msg':'success!','data':return_website})
    need_cover_icon = []
    cover_icon_csv = []
    # 对于每一个簇，检查是否具有列表中的icon
    # cluster_no_dict[cur_cluster_no].append((tree_item[0]['widget'],tree_item[1]['outlier_score'],tree_item[0]['path'].split('/')[-1]))
    for cluster_key,cluster_value in cluster_no_dict.items():
        # 每个cluster_value 均是一个簇，簇由列表构成，按顺序排列
        # 可以开发一个函数专门获取每个数组中top几的下标，比较need_cover_icon中出现的下标与这下下标即可
        for icon_item_index in range(len(cluster_no_dict[cluster_key])):
            cluster_list = cluster_no_dict[cluster_key]
            # 在need_cover_icon内则统计: 如有在其中，统计它是否在Top1/3/5,Top20%,therhold>4.9,therhold_outlier>0.55中，记录在csv中
            if cluster_list[icon_item_index][2] in need_cover_icon: 
                top_n_index, top_20percent_index,threshold_index = getCheckoutIndex(cluster_list)
                is_top_n_hit = icon_item_index <= top_n_index
                is_top_20percent_hit = icon_item_index <= top_20percent_index
                is_threshold_hit = icon_item_index <= threshold_index
                hit_statistics = is_top_n_hit or is_top_20percent_hit or is_threshold_hit
                cover_icon_csv.append([cluster_list[icon_item_index][2],cluster_key,is_hit,icon_item_index,len(cluster_no_dict[cluster_key]),is_top_n_hit,is_top_20percent_hit,is_threshold_hit])
            
    headers = ['控件icon名','包含簇号','是否命中','簇内排序','簇内控件总数','top-1,3,5命中','top-20%命中','Threshold0.49命中']
	with open('','w')as f:
		f_csv = csv.writer(f)
		f_csv.writerow(headers)
		f_csv.writerows(cover_icon_csv)

# 评测目前主要看的函数#$#$#$
# 1. 需要将控件的异常排名搞出来
def album(request, projectName='MW_lle', subtask_name='spm_lle150_optics3', galleryId='',hightlightClusterId='',cluster_no=0):
    global DBNAME
    if hightlightClusterId == 'none':
        hightlightCluster = hightlightId = ''
    else:
        hightlightCluster,hightlightId = hightlightClusterId.split('.')
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    dataBaseProcessor.projectName = projectName
    dataBaseProcessor.subtask_name = subtask_name
    dataBaseProcessor.configTableName = dataBaseProcessor.projectName+'_config'
    dataBaseProcessor.metaDataTableName = dataBaseProcessor.projectName + '_metadata'        
    dataBaseProcessor.apkTreeTableName = dataBaseProcessor.projectName+'__'+dataBaseProcessor.subtask_name+'_apktree'         
    #print('what??', dataBaseProcessor.configTableName , dataBaseProcessor.metaDataTableName, dataBaseProcessor.apkTreeTableName)
    config = dataBaseProcessor.getConfig()
    metadata = dataBaseProcessor.queryMetaData({'project_name':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1,"rawapkforestname":1,"remark":1}) 
    dataBaseProcessor.rawApkForestName = metadata[0]['rawapkforestname']
    rawapkTree = dataBaseProcessor.queryRawAPKTree({'image_cluster_no':{"$ne":'-2'}}, {"path" : 1, "app" : 1, "widget" : 1,"method_api":1, "suspect":1})
    apkTree = dataBaseProcessor.queryAPKTree({}, {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1})
    #print(rawapkTree)
    #print(apkTree)
    print('what?',metadata)
    #stanard_android_api = readTxt('/home/dl/users/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/MisleadingWidgetsDetective/type.txt')
    #stanard_android_api = readTxt('/core/kernel/01work/02project/system/AndroidUIUnderstanding/05MisleadingWidget/process/MisleadingWidgetsDetective/MisleadingWidgetsDetective/type.txt')

    apkInfoTree = []
    rawapkTree[0]['api_type'] = []
    # 将簇信息存入一个字典，这样可以统计出每个簇有多少个控件，分属于多少应用
    cluster_info_dict = dict()
    cluster_show_dict = dict()
    app_statisic_dict = dict()
    # 将rawAPITree中的信息补充到apkTree当中，最后存入到apkInfoTree中
    for i in range(len(rawapkTree)):
        # 用于统计各簇的数量>>>>
        # 会有各簇下各应用数量的统计,每次更新时都检查状态，如果一个簇内数量>5个，表为可以显示can_show
        # 同时统计每个簇内应用纯度(熵)，低于某个纯度则标为low_app_abundance.即熵越小，不确定性越小，丰度越低，越是不要显示
        if apkTree[i]['cluster_no'] not in cluster_info_dict:
            cluster_info_dict[apkTree[i]['cluster_no']] = dict()
            cluster_info_dict[apkTree[i]['cluster_no']][rawapkTree[i]['app']] = 1
        else:
            if rawapkTree[i]['app'] not in cluster_info_dict[apkTree[i]['cluster_no']]:
                cluster_info_dict[apkTree[i]['cluster_no']][rawapkTree[i]['app']] = 1
            else:
                cluster_info_dict[apkTree[i]['cluster_no']][rawapkTree[i]['app']] +=1
        cluster_show_dict[apkTree[i]['cluster_no']] = isCanShow(cluster_info_dict[apkTree[i]['cluster_no']])
        # 统计各簇中控件数量结束<<<<
        if rawapkTree[i]['_id'] != apkTree[i]['raw_id']:
            print('Wrong!!')
        apkTree[i]['isOutlier'] = ''
        apkTree[i]['outlier_score'] = apkTree[i]['outlier_score'][:5]
        #if float(apkTree[i]['outlier_score']) <= -0.55:
        if float(apkTree[i]['outlier_score']) <= 1:
        #if float(apkTree[i]['outlier_score']) > 3:
            apkTree[i]['isOutlier'] = 'outlier'
        rawapkTree[i]['widget'] = ''.join(rawapkTree[i]['widget'].split(', '))
        apkTree[i]['id'] = str(apkTree[i]['raw_id'])

        if apkTree[i]['id'] == hightlightId and apkTree[i]['cluster_no'] == hightlightCluster:
            apkTree[i]['hightlight'] = 'hightlight'
        if galleryId == 'evaluate':
            rawapkTree[i]['api_type'] = rawapkTree[i]['method_api']#resoluteAPI(rawapkTree[i]['api'],stanard_android_api,'simple')#
            rawapkTree[i]['api_string'] = '  '.join(rawapkTree[i]['method_api'])
            apkInfoTree.append((rawapkTree[i], apkTree[i]))

    if galleryId == 'evaluate':
        apkInfoTree_swap = []
        new_cluster_no_dict = dict()
        new_cluster_no_count = 0
        for i in range(len(rawapkTree)):
            if cluster_show_dict[apkTree[i]['cluster_no']] == True:
                if apkInfoTree[i][1]['cluster_no'] not in new_cluster_no_dict:
                    apkInfoTree[i][1]['new_cluster_no'] = new_cluster_no_count
                    new_cluster_no_dict[apkInfoTree[i][1]['cluster_no']] = new_cluster_no_count
                    new_cluster_no_count += 1
                else:
                    apkInfoTree[i][1]['new_cluster_no'] = new_cluster_no_dict[apkInfoTree[i][1]['cluster_no']]
                apkInfoTree_swap.append(apkInfoTree[i])
    else:
        apkInfoTree_swap = apkInfoTree
        new_cluster_no_count = 0

    # 给异常控件排序，使用函数,p给异常控件加入报表的信息
    displayInfoInjetor(DBNAME,apkInfoTree_swap)

    context = {'cluster_no':cluster_no,'BaseDir':config['INPUT_DATA_DIR'], 'metadata':metadata[0], 'apkInfoTree':apkInfoTree_swap, 'apkTree':apkTree, 'max_cluster':metadata[0]['clusters'], 'cluster_num':range(int(metadata[0]['clusters'])),'new_max_cluster':new_cluster_no_count, 'staticPath':STATIC_PATH,'picturePath':PICTURE_PATH, 'language':'zh','hightlightCluster':hightlightCluster,'averAPIs':len(rawapkTree[0]['api_type']),'current_db':DBNAME,'cluster_show_dict':cluster_show_dict}
    #print(context)

    if galleryId == 'outlier':
        return render(request, 'Console/album_outlier.html', context)
    elif galleryId == 'tagging':
        return render(request, 'Console/album_tagging.html', context)
    elif galleryId == 'evaluate':
        return render(request, 'Console/evaluateCluster.html', context)
    else:
        return render(request, 'Console/album_cluster.html', context)


def tags(request):
    # 获取所有 parsingConfig['CLUSTER_PICTURE_RESULT_DIR']['isExist'] 为True的项目子任务
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    db = dataBaseProcessor.getConnection()
    collist = db.collection_names()

    no = 1
    subtaskDictList = list()
    # 遍历数据表
    for col in collist:
        # filter all _metadata
        if '_metadata' not in col :
            continue
        # 这条分支是能获取到信息的
        # 对于每个项目数据表遍历其内容
        for subtask in db[col].find():
            subtaskDict = dict()
            subtaskDict['no'] = no
            subtaskDict['projectName'] = col.replace('_metadata', '')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']

            try:
                dataBaseProcessor.project_name = subtaskDict['projectName']
                dataBaseProcessor.subtask_name = subtaskDict['subtaskName']
                dataBaseProcessor.metaDataTableName = dataBaseProcessor.project_name + '_metadata'        
                metadata = dataBaseProcessor.queryMetaData({'remark':1}) 
                metadata = metadata[0]['remark']
            except:
                metadata = 'Nothing'
            subtaskDict['remark'] = metadata
            # 由于evaluate加入，更改
            #subtaskDict['tagging_link'] = '/Console/tagging/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDict['tagging_link'] = '/Console/evaluate/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':STATIC_PATH}
    return render(request, 'Console/tags.html', context)

def tagging(request, projectName='MW_lle', subtask_name='spm_lle150_optics3', widget_id=''):
    return album(request, projectName, subtask_name, 'tagging')

    # 首先要求登录
def evaluateHome(request):
    username_session = request.session.get('username',None)
    if username_session == None: 
        needLogin = True
    else:
        needLogin = False
    context = { 'staticPath':STATIC_PATH, 'needLogin': needLogin, 'username':username_session}
    return render(request,'Console/evaluateHome.html',context)

# 异常
def evaluate(request,projectName='MW_pca',subtask_name='spm_pca300_optics3'):
    # 获取所有outlier的控件
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    dataBaseProcessor.projectName = projectName
    dataBaseProcessor.subtask_name = subtask_name
    dataBaseProcessor.configTableName = dataBaseProcessor.projectName+'_config'
    dataBaseProcessor.metaDataTableName = dataBaseProcessor.projectName + '_metadata'        
    dataBaseProcessor.apkTreeTableName =dataBaseProcessor.projectName+'__'+dataBaseProcessor.subtask_name+'_apktree'         
    #print('what??', dataBaseProcessor.configTableName , dataBaseProcessor.metaDataTableName, dataBaseProcessor.apkTreeTableName)
    config = dataBaseProcessor.getConfig()
    rawapkTree = dataBaseProcessor.queryRawAPKTree({'image_cluster_no':{"$ne":'-2'}}, {"path" : 1, "app" : 1, "widget" : 1})
    apkTree = dataBaseProcessor.queryAPKTree({}, {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1})
    #metadata = dataBaseProcessor.queryMetaData({'projectName':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    metadata = dataBaseProcessor.queryMetaData({'project_name':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1,"rawapkforestname":1}) 
    dataBaseProcessor.rawApkForestName = metadata[0]['rawapkforestname']
    print('evaluate starting...')
    metadata[0]['projectName'] = projectName

    apkInfoTree = []
    if apkTree == []:
        return HttpResponse('该项目下没有已运行完成的项目.')
    if 'outlier_score' not in apkTree[0]:
        return HttpResponse('该项目还未进行异常检测.')

    #pageSize = 12
    #curPageSize = 12
    pageSize = 1
    curPageSize = 1
    page = 0
    maxPage = 0
    for i in range(len(rawapkTree)):
        if rawapkTree[i]['_id'] != apkTree[i]['raw_id']:
            print('Wrong!!')
        apkTree[i]['isOutlier'] = ''
        apkTree[i]['outlier_score'] = apkTree[i]['outlier_score'][:5]
        #if float(apkTree[i]['outlier_score']) <= -0.55:
        if float(apkTree[i]['outlier_score']) <= 1:
        #if float(apkTree[i]['outlier_score']) > :
            apkTree[i]['isOutlier'] = 'outlier'
            # 现在只有是outlier的才被加入
            rawapkTree[i]['widget'] = ''.join(rawapkTree[i]['widget'].split(', '))
            apkTree[i]['id'] = str(apkTree[i]['raw_id'])
            curPageSize -= 1
            if curPageSize == 0:
                curPageSize = 12
                page += 1
                maxPage = page
            apkTree[i]['page'] = str(page)
            apkInfoTree.append((rawapkTree[i], apkTree[i]))

    context = {'BaseDir':config['INPUT_DATA_DIR'], 'metadata':metadata[0], 'outlierapkInfoTree':apkInfoTree, 'apkTree':apkTree, 'max_cluster':metadata[0]['clusters'], 'cluster_num':range(int(metadata[0]['clusters'])), 'staticPath':STATIC_PATH,'picturePath':PICTURE_PATH ,'language':'zh','max_page':maxPage}
    #print(context)

    return render(request, 'Console/evaluate.html', context)

def evaluateSubmit(request):
    #username = request.POST.get('username')
    score = request.POST.get('score')
    #writeEvaluation({'username':username,'score':score})
    context = {'staticPath':STATIC_PATH}
    return render(request, 'Console/evaluateDone.html', context)

def getWebCachefromVPS(website,platform=''):
    print('getWebCachefromVPS>>>')
    global RAW_ROOT
    if 'f-droid' in website:
        cache_html_name = website.replace('https://f-droid.org/en/packages/','')+'-'+platform+'.html'
    else:
        cache_html_name = website.split('=')[-1]+'-'+platform+'.html'
    cache_path = RAW_ROOT+'cachehtmls'
    if not os.path.exists(cache_path+'/'+cache_html_name):
        HelpMeDownload.downloadExecuter(website,cache_html_name,cache_path,'wget')
    print('<<<getWebCachefromVPS')
    return cache_path+'/'+cache_html_name

def getInfofromGooglePlay(website):
    # logo: class="xSyT2c"
    # appname: h1 class="AHFaub"
    # contact: span "hrTbp euBY6b"
    from bs4 import BeautifulSoup

    cache_html_path = getWebCachefromVPS(website,'googleplay')
    if not os.path.exists(cache_html_path):
        print('visist error! Return None')
        return None,None,None,None

    #html = requests.get(website,headers=headers,proxies=proxies)
    #soup = BeautifulSoup(html.content,'lxml')
    soup = BeautifulSoup(open(cache_html_path),'html.parser')

    try:
        logo = soup.find('img', {'class', 'T75of sHb2Xb'}).get('src')
        appname = soup.find('h1', {'class', 'AHFaub'}).span.string
        contact = soup.find('a', {'class', 'hrTbp euBY6b'}).string
    except:
        print('this page might not exist.')
        return None,None,None,None

    return logo,appname,contact,''

    
def getInfofromFdroid(website):
    # logo: "article-area" > class "package-icon"
    # appname: "article-area" > class "package-name"
    # contact: "package-links" > Issue Tracker
    from bs4 import BeautifulSoup
    '''
    from fake_useragent import UserAgent
    import requests
    ua=UserAgent()
    headers={"User-Agent":ua.random}

    html = requests.get(website,headers=headers)
    if html.status_code != 200:
        print('status_code:',html.status_code,' error!')
        return None,None,None,None
    '''
    cache_html_path = getWebCachefromVPS(website,'fdroid')
    if not os.path.exists(cache_html_path):
        print('visist error! Return None')
        return None,None,None,None
    soup = BeautifulSoup(open(cache_html_path),'html.parser')

    try:
        main = soup.find('div', {'class', 'article-area'})
        logo = main.article.header.img.get('src')
        appname = main.article.header.div.h3.string
        # 去除空白字符
        appname = appname.strip()

        contacts = soup.select('.package-links > li >  a')
        contact = ''
        for item in contacts:
            if item.string == 'Issue Tracker':
                contact = item.get('href')
                break
        download = soup.find('p',{'class','package-version-download'}).b.a.get('href')
    except:
        print('this page might not exist.')
        return None,None,None,None

    return logo,appname,contact,download

def getInfofromApkfab(website):
    # https://apkfab.com/free-apk-download?q=
    # logo: "article-area" > class "package-icon"
    # appname: "article-area" > class "package-name"
    # contact: "package-links" > Issue Tracker
    from bs4 import BeautifulSoup

    # 首先进行网址转化:
    website = 'https://apkfab.com/free-apk-download?q='+website.split('=')[-1]
    cache_html_path = getWebCachefromVPS(website,'apkfab')
    if not os.path.exists(cache_html_path):
        print('visist error! Return None')
        return None,None,None,None

    #html = requests.get(website,headers=headers,proxies=proxies)
    #soup = BeautifulSoup(html.content,'lxml')
    soup = BeautifulSoup(open(cache_html_path),'html.parser')

    
    logos = soup.select('.packageInfo > a > img')
    if len(logos) == 0:
        logos = soup.select('.packageInfo > div > img')
    logo = logos[0].get('src')
    # = main.find('a[class="title"]')
    appnames = soup.select('.packageInfo > div > a')
    appnames.extend(soup.select('.packageInfo > div > div'))
    appname = download = ''
    for item in appnames:
        #print('=>',item)
        if 'title' in item.get('class'):
            appname = item.string
            if 'href' in item.attrs:
                download = item.get('href')
            break
            '''
    except:
        print('this page might not exist.')
        return None,None,None,None
        '''
    if download == '':
        download = website
    return logo,appname,'',download

def submitSuspects(request):
    suspects = request.GET.get('suspects')
    suspects = suspects.rstrip(';').split(';')
    print('---->submit suspects:',suspects)
    # 连接数据库，提交标为suspects的状态
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    print('prepare to submit suspects:')

    #对idUpath更改从而更新数据库记录是否suspect
    idUpath = dataBaseProcessor.queryAllPath() # 这里就是从原apktree获取的 
    for i in range(len(idUpath)):
        #idUpath[i][1] = {"$set":{"cluster":str(clusterLabels[i])}}
        # _id字段保留，对1字段进行修改改为image_cluster_no
        if str(idUpath[i][0]) in suspects:
            idUpath[i][1] = 'suspect btn-warning'
            print(str(idUpath[i][0]),idUpath[i][1])
        else:
            idUpath[i][1] = 'notsuspect btn-default'
    dataBaseProcessor.updateRawAPKForest_Suspect(idUpath)

    # 数据库完成，，，接下来获取更多信息
    suspects_app = request.GET.get('suspects_app')
    suspects_app = suspects_app.rstrip(';').split(';')
    print('---->suspects_app:',suspects_app)
    return_website = []
    for app in suspects_app:
        website = fetchAppWebsiteInfo(DBNAME,app)
        if 'f-droid' in website:
            return_website.append( getInfofromFdroid(website) )
        else:
            google_logo = google_appname = google_contact = google_download = ''
            result2 = getInfofromApkfab(website) 
            #print('#>result2',result2)
            if result2 != (None,None,None,None):
                google_logo = result2[0]
                google_appname = result2[1]
                google_download = result2[3]
            result1 = getInfofromGooglePlay(website)
            #print('#result1>',result1)
            if result1 != (None,None,None,None):
                if google_logo != '':google_logo = result1[0]
                if google_appname != '':google_appname = result1[1]
                google_contact = result1[2]
            result = (google_logo , google_appname , google_contact , google_download  )
            return_website.append(result)
    print('======>return_website:',return_website)
    return JsonResponse({'msg':'success!','data':return_website})

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

#DBNAME = 'db_DroidBotMW'
DBNAME = 'db_Droidbot1128'
#DBNAME = 'db_DroidBotMW_tfidf'

# 重要业务逻辑处理文件
# Create your views here.
# 配置文件地址
# 9.7更新思路: 使用baseProcesser 获取json数据即可
#MG
CONFIG_PATHS = '/core/kernel/01work/02project/system/AndroidUIUnderstanding/03WidgetClustering/process/androidwidgetclustering/'
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

def writeTxt(content,path):                                                                            
    #path += '.txt'                                                                                         
    file_handle=open(path,mode='w')                                                                         
    file_handle.write(content)                                                                   
    file_handle.close()                                                                                     
    print(path,',',len(content),' records writen.') 

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
    context = {'userList':findResult,'staticPath':'http://172.17.9.13:8000/static'}
    print('in users',findResult)
    for i in range(len(findResult)):
        findResult[i]['no'] = findResult[i]['_id']
    return render(request, 'Console/users.html', context)

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
    context = {'userList':insertResult,'staticPath':'http://172.17.9.13:8000/static', 'msg':'Add User %s Successfully!' % username}
    return JsonResponse({'msg':'Add User Successfully!'})

def deleteUser(request):
    user_id = request.GET.get('user_id')
    dataBaseProcessor = loadDataBase(CONFIG_PATHS)
    print('deleteing id=',user_id)
    deleteResult = dataBaseProcessor.deleteUser(ObjectId(user_id))
    context = {'userList':deleteResult,'staticPath':'http://172.17.9.13:8000/static'}
    print('deleteResult',deleteResult)
    return JsonResponse({'msg':'Delete Successfully!'})

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
    context = {'subtaskDictList':subtaskDictList, 'staticPath':'http://172.17.9.13:8000/static'}
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
    return dataBaseProcessor

def console(request):
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
    context = {'default_cmd':default_cmd,'staticPath':'http://172.17.9.13:8000/static'}
    return render(request, 'Console/console.html', context)

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

def print_object(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))

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
    context = {'subtaskDictList':subtaskDictList, 'staticPath':'http://172.17.9.13:8000/static'}
    return render(request, 'Console/projects.html', context)

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
    context = {'subtaskDictList':subtaskDictList, 'staticPath':'http://172.17.9.13:8000/static'}
    return render(request, 'Console/gallerys.html', context)

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
    context = {'metadata':metadata[0], 'configLists':parsingConfig, 'staticPath':'http://172.17.9.13:8000/static', 'language':'zh', 'clusterPictureDir':config['CLUSTER_PICTURE_RESULT_DIR'], 'canPreview':canPreview}
    #return JsonResponse({'message':'Hello world'})
    return render(request, 'Console/subtask.html', context)
    #return HttpResponse("Hello world")

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

def album(request, projectName='MW_lle', subtask_name='spm_lle150_optics3', galleryId='',hightlightClusterId=''):
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
    rawapkTree = dataBaseProcessor.queryRawAPKTree({}, {"path" : 1, "app" : 1, "widget" : 1,"api":1})
    apkTree = dataBaseProcessor.queryAPKTree({}, {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1})
    metadata = dataBaseProcessor.queryMetaData({'projectName':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    #print(rawapkTree)
    #print(apkTree)
    print('what?',metadata)
    stanard_android_api = readTxt('/core/kernel/01work/02project/system/AndroidUIUnderstanding/05MisleadingWidget/process/MisleadingWidgetsDetective/MisleadingWidgetsDetective/type.txt')

    apkInfoTree = []
    rawapkTree[0]['api_type'] = []
    # 将rawAPITree中的信息补充到apkTree当中，最后存入到apkInfoTree中
    for i in range(len(rawapkTree)):
        if rawapkTree[i]['_id'] != apkTree[i]['raw_id']:
            print('Wrong!!')
        apkTree[i]['isOutlier'] = ''
        if float(apkTree[i]['outlier_score']) <= -0.55:
            apkTree[i]['isOutlier'] = 'outlier'
        rawapkTree[i]['widget'] = ''.join(rawapkTree[i]['widget'].split(', '))
        apkTree[i]['id'] = str(apkTree[i]['raw_id'])
        if apkTree[i]['id'] == hightlightId and apkTree[i]['cluster_no'] == hightlightCluster:
            apkTree[i]['hightlight'] = 'hightlight'
        if galleryId == 'evaluate':
            rawapkTree[i]['api_type'] = rawapkTree[i]['api']#resoluteAPI(rawapkTree[i]['api'],stanard_android_api,'simple')#
        apkInfoTree.append((rawapkTree[i], apkTree[i]))

    context = {'BaseDir':config['INPUT_DATA_DIR'], 'metadata':metadata[0], 'apkInfoTree':apkInfoTree, 'apkTree':apkTree, 'max_cluster':metadata[0]['clusters'], 'cluster_num':range(int(metadata[0]['clusters'])), 'staticPath':'http://172.17.9.13:8000/static','picturePath':'http://219.216.64.42', 'language':'zh','hightlightCluster':hightlightCluster,'averAPIs':len(rawapkTree[0]['api_type'])}
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
            # 由于evaluate加入，更改
            #subtaskDict['tagging_link'] = '/Console/tagging/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDict['tagging_link'] = '/Console/evaluate/%s/%s' % (subtaskDict['projectName'], subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList, 'staticPath':'http://172.17.9.13:8000/static'}
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
    context = { 'staticPath':'http://172.17.9.13:8000/static', 'needLogin': needLogin, 'username':username_session}
    return render(request,'Console/evaluateHome.html',context)

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
    rawapkTree = dataBaseProcessor.queryRawAPKTree({}, {"path" : 1, "app" : 1, "widget" : 1})
    apkTree = dataBaseProcessor.queryAPKTree({}, {"raw_id" : 1, "cluster_no" :1, "outlier_score" :1})
    metadata = dataBaseProcessor.queryMetaData({'projectName':1, 'subtask_name':1, 'updatetime':1, "ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    #print(rawapkTree)
    #print(apkTree)
    print('what?',metadata)
    metadata[0]['projectName'] = projectName

    apkInfoTree = []

    #pageSize = 12
    #curPageSize = 12
    pageSize = 1
    curPageSize = 1
    page = 0
    for i in range(len(rawapkTree)):
        if rawapkTree[i]['_id'] != apkTree[i]['raw_id']:
            print('Wrong!!')
        apkTree[i]['isOutlier'] = ''
        if float(apkTree[i]['outlier_score']) <= -0.55:
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

    context = {'BaseDir':config['INPUT_DATA_DIR'], 'metadata':metadata[0], 'outlierapkInfoTree':apkInfoTree, 'apkTree':apkTree, 'max_cluster':metadata[0]['clusters'], 'cluster_num':range(int(metadata[0]['clusters'])), 'staticPath':'http://172.17.9.13:8000/static','picturePath':'http://219.216.64.42' ,'language':'zh','max_page':maxPage}
    #print(context)

    return render(request, 'Console/evaluate.html', context)

def evaluateSubmit(request):
    #username = request.POST.get('username')
    score = request.POST.get('score')
    #writeEvaluation({'username':username,'score':score})
    context = {'staticPath':'http://172.17.9.13:8000/static'}
    return render(request, 'Console/evaluateDone.html', context)

def changeDB(request):
    global DBNAME
    '''
    if DBNAME == 'db_DroidBotMW_new':
        DBNAME = 'db_DroidBotMW'
    elif DBNAME == 'db_DroidBotMW':
        DBNAME = 'db_DroidBotMW_tfidf'
    elif DBNAME == 'db_DroidBotMW_tfidf':
        DBNAME = 'db_DroidBotMW_new'
    else:
        pass
    '''
    return JsonResponse({'msg':'Change Successfully'})

from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
import re
import time
import datetime

# 重要业务逻辑处理文件
# Create your views here.
# 配置文件地址
# 9.7更新思路: 使用baseProcesser 获取json数据即可
#MG
CONFIG_PATHS = '/core/kernel/01work/02project/system/AndroidUIUnderstanding/03WidgetClustering/process/androidwidgetclustering/'

def objectId2Time(objectid):
    timestamp = time.mktime(objectid.generation_time.timetuple())
    #dateArray = datetime.datetime.fromtimestamp(timestamp)
    #otherStyleTime = dateArray.strftime("%Y.%m.%d %H:%M")
    time_str = datetime.datetime.strftime(timestamp,'%Y-%m-%d %H:%M:%S')
    return time_str

def index(request):
    #根据需要选择HttpRespone或者HttpResponse
    return JsonResponse({'message':'Hello world'})
    #return HttpResponse("Hello world")

def homepage(request):
    #根据需要选择HttpRespone或者HttpResponse
    # 获取数据库信息
    baseProcessor = loadBase(CONFIG_PATHS)
    db = baseProcessor.getConnection()
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
            subtaskDict['projectName'] = col.replace('_metadata','')
            subtaskDict['subtaskName'] = subtask['subtask_name']
            subtaskDict['updateTime'] = subtask['updatetime']
            subtaskDict['link'] = '/Console/console/%s/%s' % (subtaskDict['projectName'],subtaskDict['subtaskName'])
            subtaskDictList.append(subtaskDict)
            no +=1
    context = {'subtaskDictList':subtaskDictList,'staticPath':'http://172.17.9.13:8000/static'}
    return render(request,'Console/homepage.html',context)

def loadInterpreter(configPaths,projectName,subtask_name):
    import sys,os
    sys.path.append(os.path.abspath(configPaths)) 
    sys.path.append(os.path.abspath(configPaths)+'/Assistant/') 
    import Interpreter
    from importlib import reload
    reload(Interpreter)
    # use 1,2 to use different config file
    #self.config = configuration.initConfig(2)
    #return configuration.initConfig(1)
    interpreter = Interpreter.Interpreter(projectName+'.'+subtask_name)
    return interpreter#.ParsingConfig()

def loadBase(configPaths):
    import sys,os
    sys.path.append(os.path.abspath(configPaths)+'/Base/') 
    import BaseProcessor
    from importlib import reload
    reload(BaseProcessor)
    # use 1,2 to use different config file
    #self.config = configuration.initConfig(2)
    #return configuration.initConfig(1)
    baseProcessor = BaseProcessor.BaseProcessor()
    return baseProcessor

def console(request,projectName='MW_pca',subtask_name='spm_pca300_optics3'):
    #根据需要选择HttpRespone或者HttpResponse
    #baseProcessor = loadBase(CONFIG_PATHS)
    #baseProcessor.projectName = projectName
    #baseProcessor.subtask_name = subtask_name
    #baseProcessor.configTableName = baseProcessor.projectName+'_config'
    #baseProcessor.metaDataTableName = baseProcessor.projectName + '_metadata'        
    #baseProcessor.apkTreeTableName = baseProcessor.subtask_name+'_apktree'         
    #config = baseProcessor.getConfig({'INSTANCE_NAME':projectName})
    #metadata = baseProcessor.getConfig({'subtask_name':subtask_name})
    #context = {'configLists': baseProcessor.getConfig()}
    interpreter = loadInterpreter(CONFIG_PATHS,projectName, subtask_name)
    config = interpreter.config
    parsingConfig = interpreter.ParsingConfig()
    metadata = interpreter.queryMetaData({'projectName':1,'subtask_name':1,'updatetime':1,"ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    metadata[0]['projectName'] = projectName
    print('metadata',metadata)
    print('config',config)

    context = {'metadata':metadata[0],'configLists':parsingConfig,'staticPath':'http://172.17.9.13:8000/static','language':'zh','clusterPictureDir':config['CLUSTER_PICTURE_RESULT_DIR']}
    #return JsonResponse({'message':'Hello world'})
    return render(request,'Console/console.html',context)
    #return HttpResponse("Hello world")

def gallery(request,projectName='MW_lle',subtask_name='spm_lle150_optics3',galleryId=''):
    baseProcessor = loadBase(CONFIG_PATHS)
    baseProcessor.projectName = projectName
    baseProcessor.subtask_name = subtask_name
    baseProcessor.configTableName = baseProcessor.projectName+'_config'
    baseProcessor.metaDataTableName = baseProcessor.projectName + '_metadata'        
    baseProcessor.apkTreeTableName = baseProcessor.subtask_name+'_apktree'         
    #print('what??',baseProcessor.configTableName , baseProcessor.metaDataTableName, baseProcessor.apkTreeTableName)
    config = baseProcessor.getConfig()
    rawapkTree = baseProcessor.queryRawAPKTree({},{"path" : 1, "app" : 1, "widget" : 1})
    apkTree = baseProcessor.queryAPKTree({},{"raw_id" : 1, "cluster_no" :1, "outlier_score" :1})
    metadata = baseProcessor.queryMetaData({'projectName':1,'subtask_name':1,'updatetime':1,"ifdim":1, "ifmethod":1, "imagesize":1, "rawdims":1, "cutdimway":1, "reducedims":1, "calinski" :1, "clustermethod":1, "clusters":1, "silhouette":1}) 
    #print(rawapkTree)
    #print(apkTree)
    #print(metadata)

    apkInfoTree = []
    for i in range(len(rawapkTree)):
        if rawapkTree[i]['_id'] != apkTree[i]['raw_id']:
            print('Wrong!!')
        apkTree[i]['isOutlier'] = ''
        if float(apkTree[i]['outlier_score']) <= -0.55:
            apkTree[i]['isOutlier'] = 'outlier'
        apkInfoTree.append((rawapkTree[i],apkTree[i]))

    context = {'BaseDir':config['PICTURES_DIR'],'apkInfoTree':apkInfoTree,'apkTree':apkTree,'cluster_num':range(int(metadata[0]['clusters'])),'staticPath':'http://172.17.9.13:8000/static','language':'zh'}

    if galleryId == 'outlier':
        return render(request,'Console/gallery_outlier.html',context)
    else:
        return render(request,'Console/gallery_cluster.html',context)

def console_old(request):
    #根据需要选择HttpRespone或者HttpResponse
    context = {'configLists': loadInterpreter(CONFIG_PATHS).ParsingConfig()}

    #return JsonResponse({'message':'Hello world'})
    return render(request,'Console/console.html',context)
    #return HttpResponse("Hello world")

def gallery_old(request,galleryId='outlier'):
    config = loadInterpreter(CONFIG_PATHS).config
    baseProcessor = loadBase(CONFIG_PATHS)
    if galleryId == 'outlier':
        rawAPKTree = baseProcessor.readDict(config['APK_TREE_PATH'])
        apkTree = dict()
        cluster_num = 0
        for app,widget in rawAPKTree.items():
            appName = app.replace('.','-')
            apkTree[appName] = dict()
            for name in widget.keys():
                widgetName = name.replace(',','_')
                apkTree[appName][widgetName] = dict()
                apkTree[appName][widgetName]['path'] = rawAPKTree[app][name]['path']
                apkTree[appName][widgetName]['cluster'] = rawAPKTree[app][name]['cluster']
                apkTree[appName][widgetName]['outlier'] = rawAPKTree[app][name]['outlier'][:5]
                if rawAPKTree[app][name]['outlier'][:5] == 'nan':
                    apkTree[appName][widgetName]['isoutlier'] = ''
                elif float(rawAPKTree[app][name]['outlier'][:5]) <= -0.55:
                    apkTree[appName][widgetName]['isoutlier'] = 'outlier'
                else:
                    apkTree[appName][widgetName]['isoutlier'] = ''
                if rawAPKTree[app][name]['cluster'] > cluster_num:
                    cluster_num = rawAPKTree[app][name]['cluster']
        import gc
        del rawAPKTree
        gc.collect()
        context = {'BaseDir':config['PICTURES_DIR'],'picutreLists':apkTree,'cluster_num':range(cluster_num)}
        return render(request,'Console/gallery_cluster.html',context)
    elif galleryId == 'cluster':
        # 读取聚类结果，这是一个数组,按顺序说明每个
        rawAPKTree = baseProcessor.readDict(config['APK_TREE_PATH'])
        apkTree = dict()
        cluster_num = 0
        for app,widget in rawAPKTree.items():
            appName = app.replace('.','-')
            apkTree[appName] = dict()
            for name in widget.keys():
                widgetName = name.replace(',','_')
                apkTree[appName][widgetName] = dict()
                apkTree[appName][widgetName]['path'] = rawAPKTree[app][name]['path']
                apkTree[appName][widgetName]['cluster'] = rawAPKTree[app][name]['cluster']
                if rawAPKTree[app][name]['cluster'] > cluster_num:
                    cluster_num = rawAPKTree[app][name]['cluster']
        import gc
        del rawAPKTree
        gc.collect()
        context = {'BaseDir':config['PICTURES_DIR'],'picutreLists':apkTree,'cluster_num':range(cluster_num)}
        return render(request,'Console/gallery_cluster.html',context)
    else:
        rawAPKTree = baseProcessor.readDict(config['APK_TREE_PATH'])
        '''
        #{'fdj.juig.xyz':{'id':'fdj-juig-xyz','path':'...'}}
        for app,widget in apkTree.items():
            for name in widget.keys():
                apkTree[app][name].pop('api')
            apkTree[app]['id'] = app.replace('.','-')
        '''
        apkTree = dict()
        for app,widget in rawAPKTree.items():
            appName = app.replace('.','-')
            apkTree[appName] = dict()
            for name in widget.keys():
                widgetName = name.replace(',','_')
                apkTree[appName][widgetName] = rawAPKTree[app][name]['path']
        import gc
        del rawAPKTree
        gc.collect()
        context = {'BaseDir':config['PICTURES_DIR'],'picutreLists':apkTree}
        return render(request,'Console/gallery.html',context)
def tagging(request):
    pass

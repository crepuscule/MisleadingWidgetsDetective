from django.http import HttpResponse,JsonResponse
from django.shortcuts import render

# 重要业务逻辑处理文件
# Create your views here.
# 配置文件地址
#MG
CONFIG_PATHS = '/core/kernel/01work/02project/system/AndroidUIUnderstanding/03WidgetClustering/process/androidwidgetclustering/'

def index(request):
    #根据需要选择HttpRespone或者HttpResponse
    return JsonResponse({'message':'Hello world'})
    #return HttpResponse("Hello world")

def loadInterpreter(configPaths):
    import sys,os
    sys.path.append(os.path.abspath(configPaths)+'/Assistant/') 
    import Interpreter
    from importlib import reload
    reload(Interpreter)
    # use 1,2 to use different config file
    #self.config = configuration.initConfig(2)
    #return configuration.initConfig(1)
    interpreter = Interpreter.Interpreter('/data/NewStaticWidgetData/generated_data/MisleadingWidget-kpca/')
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


def console(request):
    #根据需要选择HttpRespone或者HttpResponse
    context = {'configLists': loadInterpreter(CONFIG_PATHS).ParsingConfig()}

    #return JsonResponse({'message':'Hello world'})
    return render(request,'Console/console.html',context)
    #return HttpResponse("Hello world")

def gallery(request,galleryId='outlier'):
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

# -*- coding: UTF-8 -*-
# HelpMeDownload
import os
import sys
import paramiko

HOSTNAME = '45.129.2.50'
PORT = 22
USERNAME = 'wall'
PASSWORD = 'wall'
RSA_PATH = '/home/dl/.ssh/45129250_debian_vps_id_rsa.pri'
# in windows
#DOWNLOAD_PATH = '/mnt/f/BrowerDownloads'
DOWNLOAD_PATH = '/data2/user_codes/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/static/cachehtmls'
#DOWNLOAD_PATH = '/core/kernel/01work/02project/system/AndroidUIUnderstanding/05MisleadingWidget/report/BugReport/3.9/apks'
#DOWNLOAD_PATH = '/storage/BrowerDownloads'

def buildSSHLink(command,needReturn=True):
    # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接服务器
    private = paramiko.RSAKey.from_private_key_file(RSA_PATH)
    #ssh.connect(hostname=HOSTNAME, port=PORT, username=USERNAME, password=PASSWORD) # password
    ssh.connect(hostname=HOSTNAME, port=PORT, username=USERNAME, pkey=private) # pkey

    # 执行命令
    print('远程终端执行命令:\n',command)
    stdin, out, stderr = ssh.exec_command(command)
    stdout_result = ""
    stdout_result = out.read().decode()
    ssh.close()

    result = stdout_result.split('\r\n')[-1]
    print('远程终端输出:\n',result)
    if needReturn:
        #result = int(stdout_result[-7:-4])
        if "(null)" in result or "HTTP/1.1 403 Forbidden" in result:
            print('==>run ststus:',False)
            return False
        else:
            print('==>run ststus:',True)
            return True

# 使用远程服务器执行下载,下载完取回文件再删除远程文件
def downloadExecuter(file_url, save_name='', download_path=DOWNLOAD_PATH,download_tools='axel'):
    if file_url == 'space':
        command = "df -h | grep 'Filesystem' && df -h | grep vda" 
        print('远程服务器空间剩余:')
        try:
            space_status = buildSSHLink(command,needReturn=True)
        except:
            try:
                space_status = buildSSHLink(command,needReturn=True)
            except:
                return False
        return True

    if file_url == 'clear':
        command = 'rm -rf /data/trash/*' 
        print('远程服务器正在清理...')
        try:
            buildSSHLink(command,needReturn=False)
        except:
            try:
                buildSSHLink(command,needReturn=False)
            except:
                return False
        return True
    print('远程服务器正在下载...')
    # 调用远程服务器执行命令
    if save_name == '':
        download_file_name = file_url.split('/')[-1]
    else:
        download_file_name = save_name
    if download_tools == 'wget':
        command = 'wget "%s" --tries=2 --timeout=10 -O  /data/downloads/%s' % (file_url,download_file_name)
    else:
        command = 'axel -n 10 -a "%s" -o /data/downloads/%s' % (file_url,download_file_name)
    download_status = buildSSHLink(command,needReturn=True)
    # 如果结果正常，调用本地命令下载文件
    if download_status:
        #os.system('scp -i %s %s@%s:/data/downloads/%s .' % (RSA_PATH,USERNAME,HOSTNAME,download_file_name))
        if download_tools == 'wget':
            print('远程服务器下载完成，正在回传(use wget)...')
            os.system('wget "%s/%s" -O %s/%s' % (HOSTNAME+'/data/downloads',download_file_name,download_path,download_file_name))
        else:
            print('远程服务器下载完成，正在回传(use axel)...')
            os.system('axel -n 10 -a "%s/%s" -o %s/%s' % (HOSTNAME+'/data/downloads',download_file_name,download_path,download_file_name))
        '''
        command = 'mv /data/downloads/%s /data/trash/%s' % (download_file_name,download_file_name)
        try:
            buildSSHLink(command,needReturn=False)
        except:
            try:
                buildSSHLink(command,needReturn=False)
            except:
                return False
        if os.path.exists(download_file_name):
            return True
        else:
            return False
        '''
    else:
        return False

if __name__=='__main__':
    if len(sys.argv) <= 2:
        sys.argv.append('')
    if downloadExecuter(sys.argv[1],sys.argv[2],DOWNLOAD_PATH,'axel'):
        print('执行成功')
    else:
        print('执行失败')

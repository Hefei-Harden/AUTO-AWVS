# -*- coding:utf-8 -*-
#   author:合肥哈登
#   time:2020/8/24

import requests
import json
import requests.packages
import time
import urllib3
import argparse
import pandas as pd
from urllib3.exceptions import InsecureRequestWarning
from global_setting import config
import colorama
import signal
from colorama import init,Fore,Back,Style
init(autoreset=True)

urllib3.disable_warnings(InsecureRequestWarning)

#全局变量配置
global t_time
global all_count
global id_last_url
global time_start
time_start = id_last_url = all_count = t_time = 0

s = requests.Session()
apikey = str(config['apikey'])
cookies = {"ui_session":
    config['cookies']}
headers = {     "x-auth": apikey,
                 "Content-Type": "application/json"}
                 
time_start=time.time()


    #AWVS里添加URL
def addTask(url,target):
    try:
        url = ''.join((url, '/api/v1/targets/add'))
        data = {"targets":[{"address": target,"description":""}],"groups":[]}
        r = s.post(url, headers=headers, data=json.dumps(data),timeout=30,verify=False)
        time.sleep(1)
        result = json.loads(r.content.decode())
        return result['targets'][0]['target_id']
    except Exception as e:
        return e

    # 保存代理配置，代理生效
def save(url,target_id,user_agent,proxy_address,proxy_port):
    try:
        save_url = ''.join((url, '/api/v1/targets/',target_id,'/configuration'))
        save_headers = {"User-Agent": user_agent,
                         "x-auth": config['cookies'],
                         }
        save_json = {"authentication": {"enabled": False}, "case_sensitive": "auto", "client_certificate_password": "",
                      "custom_cookies": [], "custom_headers": [], "debug": False, "excluded_hours_id": "",
                      "excluded_paths": [], "issue_tracker_id": "", "limit_crawler_scope": True, "login": {"kind": "none"},
                      "proxy": {"address": proxy_address, "enabled": True, "port": proxy_port, "protocol": "http"},
                      "scan_speed": "fast", "sensor": False, "ssh_credentials": {"kind": "none"}, "technologies": [],
                      "user_agent": user_agent}
        r = requests.patch(save_url, headers=save_headers, cookies=cookies, json=save_json, verify=False)
        return r
    except Exception as e:
        print(e)

    #开始扫描
def scan(url,target,Crawl,user_agent,profile_id,proxy_address,proxy_port,proxy_bl):
    scanUrl = ''.join((url, '/api/v1/scans'))
    target_id = addTask(url,target)
    if proxy_bl:
        save(url,target_id,user_agent,proxy_address,proxy_port)
    if target_id:
        data = {"incremental": False, "profile_id": profile_id, "schedule": {"disable": False, "start_date": None, "time_sensitive": False}, "target_id": target_id,}
        try:
            time.sleep(1)
            if proxy_bl:
                configuration(url,target_id,proxy_address,proxy_port,Crawl,user_agent)
            response = s.post(scanUrl, data=json.dumps(data),headers=headers, timeout=30, verify=False)
            result = json.loads(response.content)
            return result['target_id']
        except Exception as e:
            print(e)

    #配置
def configuration(url,target_id,proxy_address,proxy_port,Crawl,user_agent):
    configuration_url = ''.join((url,'/api/v1/targets/{0}/configuration'.format(target_id)))
    #data = {"scan_speed":"fast","login":{"kind":"none"},"ssh_credentials":{"kind":"none"},"sensor": False,"user_agent": user_agent,"case_sensitive":"auto","limit_crawler_scope": True,"excluded_paths":[],"authentication":{"enabled": False},"proxy":{"enabled": True,"protocol":"http","address":proxy_address,"port":proxy_port},"technologies":[],"custom_headers":[],"custom_cookies":[],"debug":False,"client_certificate_password":"","issue_tracker_id":"","excluded_hours_id":""}
    save_json = {"authentication": {"enabled": False}, "case_sensitive": "auto", "client_certificate_password": "",
                 "custom_cookies": [], "custom_headers": [], "debug": False, "excluded_hours_id": "",
                 "excluded_paths": [], "issue_tracker_id": "", "limit_crawler_scope": True, "login": {"kind": "none"},
                 "proxy": {"address": proxy_address, "enabled": True, "port": proxy_port, "protocol": "http"},
                 "scan_speed": "fast", "sensor": False, "ssh_credentials": {"kind": "none"}, "technologies": [],
                 "user_agent": user_agent}
    s.patch(url=configuration_url,data=json.dumps(save_json), headers=headers,timeout=30, verify=False)

def main(r,id=0,num=4,delay=3600,proxy_bl=False,Crawl = False):
    try:
        proxy_address = config['proxy_address']
        proxy_port = config['proxy_port']
        awvs_url = config['awvs_url']
        count = 0
        all_count = 0
        error_count = 0
        dataframe = pd.read_csv(r, sep='\\s+',encoding='utf-8',error_bad_lines=False)
        IDs = dataframe['ID'].array
        #names = dataframe['name'].array
        index_nums = dataframe[(dataframe.ID==id)].index.tolist()
        targets = dataframe['url'].array
        targets = targets[index_nums[0]:]
        
        profile_id = "11111111-1111-1111-1111-111111111111"
        user_agent = config['user_agent'] #扫描默认UA头
        if Crawl:
            profile_id = "11111111-1111-1111-1111-111111111117"

        for target in targets:
            target = choose_url(target)
            if target == 0:
                continue
            if scan(awvs_url,target,Crawl,user_agent,profile_id,proxy_address,int(proxy_port),proxy_bl):
                print("{0} 添加成功".format(target))
                all_count += 1
            else:
                error_count += 1
            count += 1
            if count >= num:
                time.sleep(delay)
                count = 0
        id_last_url = IDs[id+all_count+error_count]
        
        return t_time,all_count,id_last_url
    except Exception as e:
        print(e)
    
def choose_url(url):
    if url[:4] == 'http':
        target = url
    else:
        h_url = 'http://' + url
        s_url = 'https://' + url
        try:
            s = requests.Session()
            s.post(h_url, headers=headers)
            s.close()
            return h_url
        except:
            try:
                time.sleep(1)
                s = requests.Session()
                s.post(s_url, headers=headers)
                s.close()
                return s_url
            except:
                return 0
    return target

def handler(signum,frame):
    time_end=time.time()
    t_time = time_end - time_start
    print('\033[1;31;40m本次扫描用时：'+str(t_time))
    print('\033[0;31;40m总共扫描URL个数：'+str(all_count))
    print('\033[0;31;40m最后一个URL任务ID为：'+str(id_last_url))
    print('\033[0;31;40m本次扫描结束！感谢您的使用！欢迎提供宝贵意见！')
    print('\033[0m')
    exit()

def print_banner():
    
    ss=r"""

  """
    print('\033[1;32;40m扫描任务开始......')
    print('\033[1;32;40m'"""
     __             ____        
    |  |          /   __|           
    |  |         /   /          
    |  |____     |   |__           
    |_______|     \ ____|      
                               @合肥哈登
                               @安徽赋能科技有限公司""")
    print('\033[1;33;40m'"""
[*] Very beautiful and niubee tool.
[*] you can use "python3 -r test.txt" to start this program
[*] try to use -h or --help show help message
[*] try to press 'CTRL+C' if you want to stop it
[*] author_Email:   xmblc@sina.cn
""")
    print('\033[0m')

if __name__ == '__main__':
    try:
        
        print_banner()
        signal.signal(signal.SIGINT,handler)
        #main('E:\FUCK_BUTIAN/BT_0-1200.txt', id=1000, num=4, delay=3600, proxy_bl=True,Crawl = False)
        parser = argparse.ArgumentParser(description='manual to this script')
        parser.add_argument("-r", type=str, default="0")
        parser.add_argument("-id", type=int, default=0)
        parser.add_argument("-n", type=int, default=4)
        parser.add_argument("-t", type=int, default=3600)
        parser.add_argument("-p", type=int, default=0)
        parser.add_argument("-c", type=int,default=0)
        args = parser.parse_args()
 
        print('\033[1;32;40m执行文件：{}'.format(args.r))
        print('\033[1;32;40m起始ID：{}'.format(args.id))
        print('\033[1;32;40m同时扫描数量：{}'.format(args.n))
        print('\033[1;32;40m添加任务间隔时间：{}'.format(args.t)+'s')
        
        if args.c == 1:
            print("\033[1;32;40m已启用爬虫不扫描模式！")
        if args.p == 1:
            print("\033[1;32;40m已启用代理模式！")
        t_time,all_count,id_last_url = main(args.r,id=args.id,num=args.n,delay=args.t,proxy_bl=args.p,Crawl=args.c)
        
    except Exception as e:
        print(e)
        
        
        
        
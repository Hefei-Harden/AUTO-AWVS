# -*- coding:utf-8 -*-
#   author:合肥哈登
#   time:2020/8/24

#配置文件
config = {
    'apikey':'1986ad8c0a5b3df4d7028d5f3c06e936c184e95b676cd4cb09b55a87d343396c6',    #去AWVS 配置文件里面 有个 API KEY 复制填进去就行
    'cookies':'2986ad8c0a5b3df4d7028d5f3c06e936c5f47e0687007d677f1414453a43a81b2cd601ff50915a7b654dc1aace9c449860c91b49e74a3432ec9fcace4db63ae5f',#用BP看自己AWVS的cookies
    'proxy_address':'127.0.0.1', 
    'proxy_port':'1234',        #如果想用AWVS+X_RAY联动，这里可以设置个代理，然后X_ray监听就行了
    'awvs_url':'https://127.0.0.1:3443',
    'user_agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.21'
}

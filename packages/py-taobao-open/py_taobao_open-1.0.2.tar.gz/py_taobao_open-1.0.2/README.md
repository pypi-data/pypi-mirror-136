# 淘宝开放平台Python 3 SDK

基于淘宝开放平台[服务端SDK](https://console.open.taobao.com/?spm=a219a.7386653.1.15.3b89286cAxkZ5O#/app/33328606/app_serversdk)修改，修复原版本无法在Python 
3环境下正常运行的问题，以及包名称top->taobao_open。


### 安装
```shell
pip install py-taobao-open
# 清华源
pip install py-taobao-open -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 使用说明
```python3

import taobao_open

app_key = ''
app_secret = ''

def dg_optimus_material():
    req = taobao_open.api.TraderatesGetRequest()
    req.set_app_info(taobao_open.appinfo(app_key, app_secret))
    req.adzone_id = 'xxx'
    req.material_id = 'xxx'
    try:
        resp = req.getResponse()
        print(resp)
    except Exception as e:
        print(e)
```

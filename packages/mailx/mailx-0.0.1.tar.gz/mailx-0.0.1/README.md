# fastmail

#### 介绍
快捷使用mail模块

#### 软件架构
软件架构说明


#### 安装教程

1.  pip安装
```shell script
pip install fastmail
```
2.  pip安装（使用阿里云镜像加速）
```shell script
pip install fastmail -i https://mirrors.aliyun.com/pypi/simple
```


#### 使用说明

1.  demo
```python
import fastmail
query_res = fastmail.quick_send_mail(sub='test sub', content='test content')
```
# arcgis-earth-python-api
ArcGIS Earth Automation API for Python

# 打包相关

## 添加打包文件

- 添加 setup.py文件标注要输出的包和依赖项 [ref](https://zhuanlan.zhihu.com/p/388989147), 
- 添加__init__.py表示包文件
- 添加MANIFEST.in来包含或者排除文件 详见 [ref](https://blog.csdn.net/weixin_43590796/article/details/121122850)

## 打包

[ref](https://www.cnblogs.com/yinzhengjie/p/14124623.html)

编译

```
python setup.py build
```

打包egg
```
python setup.py sdist
```

### 测试

例如：

```
pip install "C:\projects\arcgis-earth-test\Python\win\automation_api\dist\earth_api-0.0.1.tar.gz"
```

打包wheel

```
python setup.py sdist bdist_wheel
```

## 上传

[官方教程](https://packaging.python.org/en/latest/tutorials/packaging-projects/)


```
py -m pip install --upgrade twine
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

### 地址
https://pypi.org/project/earth-api/


### 测试

下载

```
pip install earth-api
```

```

from earth_api import EarthAPI
api = EarthAPI(type="swagger")
print(api.get_camera())

```
## TODO

* [ ] 包的结构的设置
* [ ] 如何写示例文档
* [ ] 函数文档和提示如何应用上
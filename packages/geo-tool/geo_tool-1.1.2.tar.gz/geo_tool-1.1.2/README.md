[![Supported Versions](https://img.shields.io/pypi/pyversions/geo-tool.svg)](https://pypi.org/project/geo-tool)
### 经纬度解析转换库
                  
#### pip安装
```shell
pip install geo_tool
```

#### 1.百度经纬度解析
```python
    from geo_tool import BaiduGeo
    baidu_map_key = 'xxxxxxxxxxxx'
    print(BaiduGeo(baidu_map_key).geo2address(22.52955, 113.93078))
    print(BaiduGeo(baidu_map_key).get_city_name_by_geo(22.52955, 113.93078))
    print(BaiduGeo(baidu_map_key).address2geo('北京市海淀区上地十街10号'))

```

#### 2.高德经纬度解析
```python
    from geo_tool import GaodeGeo

    gaode_map_key = 'xxxxxxxx'
    print(GaodeGeo(gaode_map_key).geo2address(22.52955, 113.93078))
    print(GaodeGeo(gaode_map_key).address2geo("广东省深圳市南山区"))
    print(GaodeGeo(gaode_map_key).get_city_name_by_geo(22.52955, 113.93078))

```

#### 3.谷歌经纬度解析
```python
    from geo_tool import GoogelGeo

    google_key = 'xxxxxx'
    print(GoogelGeo(google_key).address2geo('深圳市南山区'))

```

#### 4.经纬度互相转换
```python
    from geo_tool import GeoTransform
    baidu_lng = '114.126496'
    baidu_lat = '22.538926'
    print(GeoTransform(lng=baidu_lng, lat=baidu_lat).baidu2google())
    google_lng = 114.12008298963123
    google_lat = 22.53258746867191
    print(GeoTransform(lng=google_lng, lat=google_lat).google2baidu())

```

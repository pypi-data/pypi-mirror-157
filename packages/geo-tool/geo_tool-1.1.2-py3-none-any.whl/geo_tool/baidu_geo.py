# -*- coding: utf-8 -*-
# @Time    : 2020/6/16 10:26
# @Author  : CC
# @Desc    : baidu_geo.py
import json

import requests

from .base_geo import BaseGeo


class BaiduGeo(BaseGeo):
    def __init__(self, baidu_map_key):
        self.baidu_map_key = baidu_map_key

    def address2geo(self, address: str = ''):
        """
        将地址转换成经纬度
        :param address: 地址
        :return: 经纬度dict
        """
        url = "http://api.map.baidu.com/geocoding/v3/"
        querystring = {"address": address, "output": "json", "ak": self.baidu_map_key}
        response = requests.request("GET", url, params=querystring).json()
        return response

    def geo2address(self, lat: float = 0, lon: float = 0):
        """
            :param lat: 百度坐标 纬度
            :param lon: 百度坐标 经度
            :param latest_admin: 1 表示使用最新的行政区划，0 表示使用老的行政区划
            :return: 包含各种位置信息的j son 字符串

            attention： latest_admin＝1 时，部分城市的级别 是县级市， 不归属任何地级市， city为空， district 为城市名
                        latest_admin＝0 时，部分城市的级别 是县级市， 不归属任何地级市， city为城市名， district 为城市名， 两者一样，
                        台湾的不一样，district为乡镇级行政单位

            """
        url = "http://api.map.baidu.com/geocoder/v2/"
        querystring = {
            "location": "{},{}".format(float(lat), float(lon)),
            "output": "json",
            "pois": "1",
            "latest_admin": 1,
            "ak": self.baidu_map_key,
        }

        response = requests.request("GET", url, params=querystring)
        result = json.loads(response.text)
        return result

    def get_city_name_by_geo(self, lat: float = 0, lon: float = 0):
        return self.geo2address(lat, lon)['result']['addressComponent']['city']


if __name__ == '__main__':
    baidu_map_key = 'xxxxxxxxxxxx'
    print(BaiduGeo(baidu_map_key).geo2address(22.52955, 113.93078))
    print(BaiduGeo(baidu_map_key).get_city_name_by_geo(22.52955, 113.93078))
    print(BaiduGeo(baidu_map_key).address2geo('北京市海淀区上地十街10号'))

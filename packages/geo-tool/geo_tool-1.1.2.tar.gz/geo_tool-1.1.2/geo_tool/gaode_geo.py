# -*- coding: utf-8 -*-
# @Time    : 2020/6/16 10:45
# @Author  : CC
# @Desc    : gaode_geo.py
import json
from loguru import logger
import requests

from .base_geo import BaseGeo


class GaodeGeo(BaseGeo):
    def __init__(self, gaode_map_key):
        self.gaode_map_key = gaode_map_key

    def address2geo(self, address: str = ''):
        """
           利用高德geocoding服务解析地址获取位置坐标
           :param address:需要解析的地址
           :return:
        """
        geocoding = {'s': 'rsv3',
                     'key': self.gaode_map_key,
                     'city': '全国',
                     'address': address}
        ret = requests.get("%s?%s" % ("http://restapi.amap.com/v3/geocode/geo", geocoding))
        logger.info(ret.text)
        if ret.status_code == 200:
            json_obj = json.loads(ret.text)
            if json_obj['status'] == '1' and int(json_obj['count']) >= 1:
                geocodes = json_obj['geocodes'][0]
                lng = float(geocodes.get('location').split(',')[0])
                lat = float(geocodes.get('location').split(',')[1])
                return (lng, lat)
            else:
                return None
        else:
            return None

    def geo2address(self, lat: float = 0, lng: float = 0):
        url = f'https://restapi.amap.com/v3/geocode/regeo?output=json&location={lng},{lat}&key={self.gaode_map_key}&radius=1000'
        result = requests.request('get', url).json()
        return result

    def get_city_name_by_geo(self, lat: float = 0, lon: float = 0):
        return self.geo2address(lat, lon)['regeocode']['addressComponent']['city']


if __name__ == '__main__':
    gaode_map_key = 'xxxxxxxx'
    print(GaodeGeo(gaode_map_key).geo2address(22.52955, 113.93078))
    print(GaodeGeo(gaode_map_key).address2geo("广东省深圳市南山区"))
    print(GaodeGeo(gaode_map_key).get_city_name_by_geo(22.52955, 113.93078))

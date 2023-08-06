# -*- coding: utf-8 -*-
# @Time    : 2020/6/16 10:19
# @Author  : CC
# @Desc    : base_geo.py基础经纬度解析类
import abc


class BaseGeo(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def address2geo(self, address: str = ''):
        pass

    @abc.abstractmethod
    def geo2address(self, lat: float = 0, lon: float = 0):
        pass

    @abc.abstractmethod
    def get_city_name_by_geo(self, lat: float = 0, lon: float = 0):
        pass

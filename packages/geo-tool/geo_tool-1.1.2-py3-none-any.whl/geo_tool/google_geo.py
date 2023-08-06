# -*- coding: utf-8 -*-
# @Time    : 2020/6/16 11:47
# @Author  : CC
# @Desc    : google_geo.py
import googlemaps
from .base_geo import BaseGeo


class GoogelGeo(BaseGeo):
    def __init__(self, google_key=''):
        self.google_key = google_key
        self.gmaps = googlemaps.Client(key=self.google_key)

    def get_city_name_by_geo(self, lat: float = 0, lng: float = 0):
        pass

    def address2geo(self, address: str = ''):
        # return geocoder.google(address).latlng
        return self.gmaps.geocode(address)

    def geo2address(self, lat: float = 0, lng: float = 0):
        return self.gmaps.reverse_geocode((lat, lng))


if __name__ == '__main__':
    google_key = 'xxxxxx'
    print(GoogelGeo(google_key).address2geo('深圳市南山区'))

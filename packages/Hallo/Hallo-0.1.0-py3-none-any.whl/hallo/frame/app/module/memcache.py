# -*- coding: utf-8 -*-

from app.module.base import BaseController


class MemcacheController(BaseController):

    def mem_set(self):
        key = self.get('key')
        val = self.get('val')
        if self.memcache.set(key, val):
            return self.ok()
        else:
            return self.error('设置失败')

    def mem_get(self):
        key = self.get('key')
        val = self.memcache.get(key)
        if val:
            return self.ok(val)
        else:
            return self.error('获取失败')

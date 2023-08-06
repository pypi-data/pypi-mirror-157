# -*- coding: utf-8 -*-

from app.module.base import BaseController


class RedisController(BaseController):

    def mem_set(self):
        try:
            key = self.get('key')
            val = self.get('val')
            self.redis.set(key, val)
            return self.ok()
        except Exception as e:
            return self.error(str(e))

    def mem_get(self):
        try:
            key = self.get('key')
            val = self.redis.get(key)
            if isinstance(val, bytes):
                return self.ok(val.decode('UTF-8'))
            else:
                return self.error('获取失败')
        except Exception as e:
            return self.error(str(e))

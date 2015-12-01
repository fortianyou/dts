#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import tornado.web
import json
import urllib
import api.libs.define
import api.libs.config


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        # 输入参数
        self._logs = {
            'ip': self.request.remote_ip,
        }
        self._rets = {}
        self._errno = api.libs.define.ERR_SUCCESS
        self._conf = api.libs.config.get_config()
        self._domain = self._conf.get('server', 'domain')

    def _write(self):
        """传送到客户端, json 封装
        """
        ret = {
            'errno': self._errno,
            'data': self._rets,
        }
        ret_json = json.dumps(ret)
        super(BaseHandler, self).write(ret_json)
        self._logs['rt'] = '{:.03f}'.format(1000 * self.request.request_time())

    def _trace_url(self, tokens):
        """为链接包装一层跳转, 用来记录特殊事件.
        """
        token.update(self._params)
        url = '{0}/trace?{1}'.format(
            self._domain,
            urllib.urlencode(tokens),
        )
        return url

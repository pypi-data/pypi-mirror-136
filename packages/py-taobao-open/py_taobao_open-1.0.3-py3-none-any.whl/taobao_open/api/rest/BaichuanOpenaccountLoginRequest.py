from taobao_open.api.base import RestApi


class BaichuanOpenaccountLoginRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.name = None

    def getapiname(self):
        return 'taobao.baichuan.openaccount.login'

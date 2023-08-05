from taobao_open.api.base import RestApi


class TbkSpreadGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.requests = None

    def getapiname(self):
        return 'taobao.tbk.spread.get'

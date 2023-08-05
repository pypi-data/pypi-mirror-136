from taobao_open.api.base import RestApi


class TopAuthTokenCreateRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=443):
        RestApi.__init__(self, domain, port)
        self.code = None
        self.uuid = None

    def getapiname(self):
        return 'taobao.top.auth.token.create'

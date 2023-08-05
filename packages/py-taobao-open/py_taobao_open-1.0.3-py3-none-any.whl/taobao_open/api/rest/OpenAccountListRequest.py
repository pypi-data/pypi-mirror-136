from taobao_open.api.base import RestApi


class OpenAccountListRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.isv_account_ids = None
        self.open_account_ids = None

    def getapiname(self):
        return 'taobao.open.account.list'

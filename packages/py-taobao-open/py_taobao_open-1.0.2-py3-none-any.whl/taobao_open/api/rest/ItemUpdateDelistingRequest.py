from taobao_open.api.base import RestApi


class ItemUpdateDelistingRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.num_iid = None

    def getapiname(self):
        return 'taobao.item.update.delisting'

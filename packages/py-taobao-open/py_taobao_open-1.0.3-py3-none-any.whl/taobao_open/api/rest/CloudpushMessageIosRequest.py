from taobao_open.api.base import RestApi


class CloudpushMessageIosRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.body = None
        self.target = None
        self.target_value = None

    def getapiname(self):
        return 'taobao.cloudpush.message.ios'

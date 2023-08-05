from taobao_open.api.base import RestApi


class CloudpushNoticeIosRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.env = None
        self.ext = None
        self.summary = None
        self.target = None
        self.target_value = None

    def getapiname(self):
        return 'taobao.cloudpush.notice.ios'

class StandardStep:

    def __init__(self, service, scenario):
        self.service = service
        self.scenario = scenario

    # 请求的json数据
    def data(self): ...

    # 请求中的url参数
    def path_variable(self): ...

    # 请求返回后的回调处理
    def call_back(self, **kwargs): ...

    # 请求的前置操作
    def _pre_processor(self): ...

    # 请求的后置操作
    def _post_processor(self): ...

    # 调用请求
    # 因为需要注册请求，所以子类覆写的时候需要条用super
    def _execute(self): self.service.register_step(self)

    # 忽略请求的条件，默认是要执行
    def ignore(self): return False

    # 运行step
    def run(self):
        self._pre_processor()
        if not self.ignore():
            self._execute()
        self._post_processor()

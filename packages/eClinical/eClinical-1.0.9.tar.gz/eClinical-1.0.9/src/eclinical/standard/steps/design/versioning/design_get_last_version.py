import jsonpath
from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep

from eclinical.standard.design.design_api import Versioning


# 获取最后提交得版本信息
class DesignGetLastVersion(StandardStep):
    Name = "design_get_last_version"

    def __init__(self, service: Versioning, scenario: Scenario):
        super().__init__(service, scenario)


    def call_back(self, **kwargs):
        current = kwargs.get("version_info").current_version()
        if current.get("latest") is True and current.get("status") == 200:
            self.service.context["currentVersionId"] = current.get("id")
        else: raise Exception("The CRF has not Submit")

    def _execute(self):
        super()._execute()
        self.service.version_list()

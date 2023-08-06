import os

from cjen.sco.scenario import Scenario

from eclinical import Environment
from eclinical.standard.design.design_api import Versioning
from eclinical.standard.steps.design.versioning.design_download_publish_sql import DesignDownloadPublishSql
from eclinical.standard.steps.design.versioning.design_fileids import DesignFileIDS

from eclinical.standard.steps.design.versioning.design_get_last_version import DesignGetLastVersion


# 下载发布的SQL文件
class ScoDownLoadSql:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario = Scenario(scenario_dir)
        service = Versioning(environment)
        self.scenario.append_step(DesignDownloadPublishSql, service)
        # self.scenario.append_step(PortalStartupStudy, service)

    def run(self): self.scenario.run()


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    sco = ScoDownLoadSql(sco_dir, Environment.loader("DEV_03"))
    sco.run()

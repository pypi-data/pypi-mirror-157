import os

from eclinical.standard.steps.portal.hierarchies.portal_find_study import PortalFindStudy

from eclinical.standard.steps.portal.hierarchies.portal_find_sponsor import PortalFindSponsor

from eclinical import Environment

# 初始化整个公司账号的内容
from eclinical.standard.scenarios.sco_create_role import ScoCreateRole
from eclinical.standard.scenarios.sco_create_sponsor import ScoCreateSponsor
from eclinical.standard.scenarios.sco_create_study import ScoCreateStudy
from eclinical.standard.scenarios.sco_create_user import ScoCreateUser
from eclinical.standard.scenarios.sco_ctms_study import ScoCtmsStudy
from eclinical.standard.scenarios.sco_user_group import ScoUserGroup


class ScoInit:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario_dir = scenario_dir
        self.environment = environment
        self.sco_clazz = []

    def run(self):
        # 创建 Sponsor
        print("Portal 创建 Sponsor")
        sco = ScoCreateSponsor(self.scenario_dir, self.environment)
        sco.run()
        print(f'{sco.scenario.sponsor()} Sponsor ID: {sco.scenario.service.context[PortalFindSponsor.Id]}')
        # 创建 Study
        print("Portal 创建 Study")
        sco = ScoCreateStudy(self.scenario_dir, self.environment)
        sco.run()
        print(f'{sco.scenario.study()} Study ID: {sco.scenario.service.context[PortalFindStudy.Id]}')
        # 创建 Role
        print("Portal 创建 Role")
        ScoCreateRole(self.scenario_dir, self.environment).run()
        # 创建 UserGroup
        print("Portal 创建 User Group")
        ScoUserGroup(self.scenario_dir, self.environment).run()
        # 创建 User
        print("Portal 创建 User")
        ScoCreateUser(self.scenario_dir, self.environment).run()
        # 创建 CTMS SITE
        print("CTMS 创建Site")
        ScoCtmsStudy(self.scenario_dir, self.environment).run()
        # Portal 中分配Site
        print("Portal 为User Group 创建Site")
        ScoUserGroup(self.scenario_dir, self.environment).run()
        print("Finish")


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    envir = Environment.loader("DEV_03")
    sco = ScoInit(sco_dir, envir)
    sco.run()

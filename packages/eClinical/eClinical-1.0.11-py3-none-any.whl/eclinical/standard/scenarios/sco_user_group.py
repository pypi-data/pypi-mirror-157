import os.path

from eclinical import Environment
from eclinical.standard.portal.portal_api import PortalApi

from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.scenarios.sco_init import ScoInit
from eclinical.standard.steps.portal.user_groups.portal_create_usergroup import PortalCreateUserGroup
from eclinical.standard.steps.portal.user_groups.portal_get_lifecycle_hierarchies import PortalGetLifeCycleHierarchies
from eclinical.standard.steps.portal.user_groups.portal_get_user_group_info import PortalGetUserGroupInfo

#  创建UserGroup, 并且分配User, Sponsor, Study, Site.
from eclinical.standard.steps.portal.user_groups.portal_set_lifecycle_hierarchies import PortalSetLifeCycleHierarchies


class ScoUserGroup:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario = PortalScenario(scenario_dir)
        self.service = PortalApi(environment)

        # 创建用户组
        self.scenario.append_step(PortalCreateUserGroup, self.service)
        # 获取未添加到User Group中的 User
        self.scenario.append_step(PortalGetUserGroupInfo, self.service)
        # 选择lifecycle, 获取对应lifecycle的sponsor, study, site 信息
        self.scenario.append_step(PortalGetLifeCycleHierarchies, self.service)
        # 分配 Sponsor, Study, Site
        self.scenario.append_step(PortalSetLifeCycleHierarchies, self.service)

    def run(self): self.scenario.run()


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    sco = ScoUserGroup(sco_dir, Environment.loader("DEV_03"))
    sco.run()
    # a = "a"
    # print(f'{{a}}')

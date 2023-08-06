import os

from eclinical import Environment
from eclinical.standard.portal.portal_api import PortalApi
from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.role.portal_create_role import PortalCreateRole
from eclinical.standard.steps.portal.role.portal_find_role import PortalFindRole
from eclinical.standard.steps.portal.role.portal_get_permission_tree import PortalGetPermissionTree
from eclinical.standard.steps.portal.role.portal_set_permissions import PortalSetPermissions


class ScoCreateRole:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario = PortalScenario(scenario_dir)
        self.service = PortalApi(environment)
        # 查询角色
        self.scenario.append_step(PortalFindRole, self.service)
        # 查询创建角色
        self.scenario.append_step(PortalCreateRole, self.service)
        # 获取菜单树
        self.scenario.append_step(PortalGetPermissionTree, self.service)
        # 为角色设置所有的菜单权限
        self.scenario.append_step(PortalSetPermissions, self.service)

    def run(self): self.scenario.run()


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    envir = Environment.loader("DEV_03")
    sco = ScoCreateRole(sco_dir, envir)
    sco.run()
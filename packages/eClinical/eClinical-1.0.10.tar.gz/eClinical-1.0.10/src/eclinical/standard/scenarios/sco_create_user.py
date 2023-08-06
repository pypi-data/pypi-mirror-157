import os.path
from eclinical import Environment
from eclinical.standard.portal.portal_api import PortalApi

from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.user.portal_associated_usergroup import PortalAssociatedUserGroup
from eclinical.standard.steps.portal.user.portal_create_user import PortalCreateUser
from eclinical.standard.steps.portal.user.portal_find_user import PortalFindUser
from eclinical.standard.steps.portal.user.portal_find_user_role import PortalFindUserRole
from eclinical.standard.steps.portal.user.portal_study_title import PortalStudyTitle
from eclinical.standard.steps.portal.user.portal_user_access import PortalUserAccess
from eclinical.standard.steps.portal.user.portal_user_append_usergroup import PortalUserAppendUserGroup


class ScoCreateUser:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario = PortalScenario(scenario_dir)
        self.service = PortalApi(environment)
        self.scenario.append_step(PortalFindUser, self.service)
        self.scenario.append_step(PortalCreateUser, self.service)
        self.scenario.append_step(PortalFindUserRole, self.service)
        self.scenario.append_step(PortalAssociatedUserGroup, self.service)
        self.scenario.append_step(PortalUserAppendUserGroup, self.service)
        self.scenario.append_step(PortalUserAccess, self.service)
        self.scenario.append_step(PortalStudyTitle, self.service)

    def run(self): self.scenario.run()


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    envir = Environment.loader("DEV_01")
    sco = ScoCreateUser(sco_dir, envir)
    sco.run()

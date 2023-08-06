from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.user_groups.portal_find_usergroup import PortalFindUserGroup
from eclinical.standard.steps.portal.user_groups.portal_get_company_envs import PortalGetCompanyEnvs


class PortalCreateUserGroup(StandardStep):
    Name = "portal_create_user_group"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)


    def _pre_processor(self):
        PortalFindUserGroup(self.service, self.scenario).run()
        PortalGetCompanyEnvs(self.service, self.scenario).run()

    def ignore(self): return self.service.context[PortalFindUserGroup.Id] is not None

    def code(self): return self.scenario.user_group()

    def _execute(self):
        super()._execute()
        if self.service.context[PortalFindUserGroup.Id] is None:
            self.service.usergroups_create_user_group(data=self.data())

    def data(self):
        return {"code": self.code(), "active": True, "envIds": self.service.context[PortalGetCompanyEnvs.Id]}

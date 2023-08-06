from cjen import BigTangerine
from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.portal_scenario import PortalScenario


class PortalGetUserRole(StandardStep):
    Name = "portal_get_user_role.py"
    Id = "portal_user_role_id"

    def __init__(self, service: BigTangerine, scenario: PortalScenario):
        super().__init__(service, scenario)

    def path_variable(self):
        return dict(PageNo=1)

    def role(self):
        return self.scenario.role()

    def _execute(self):
        super()._execute()
        self.service.userrole_api_get_user_roles(path_variable=self.path_variable())

    def call_back(self, **kwargs):
        self.service.context[self.Id] = None
        for role in kwargs.get("user_role").list():
            if role.code() == self.role():
                self.service.context[self.Id] = role.id()

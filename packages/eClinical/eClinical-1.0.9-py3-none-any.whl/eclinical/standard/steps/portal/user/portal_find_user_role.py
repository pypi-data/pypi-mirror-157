
from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.portal_scenario import PortalScenario


class PortalFindUserRole(StandardStep):
    Name = "portal_role_list.py"
    Id = "user_role_id"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)


    def role(self):
        return self.scenario.role()

    def _execute(self):
        super()._execute()
        self.service.user_api_role_list()

    def call_back(self, **kwargs):
        for r in kwargs.get("role_list").payload():
            if r.code() == self.role():
                self.service.context[PortalFindUserRole.Id] = r.id()



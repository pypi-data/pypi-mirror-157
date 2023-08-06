from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.user_roles.portal_get_user_role import PortalGetUserRole


class PortalFindNoRelUser(StandardStep):
    Name = "portal_find_no_rel_user.py"
    Id = "No_REL_USER"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)

    def _pre_processor(self):
        PortalGetUserRole(self.service, self.scenario).run()

    def path_variable(self):
        return dict(role_id=self.service.context[PortalGetUserRole.Id], PageNo=1)

    def data(self):
        return dict(role_id=self.service.context[PortalGetUserRole.Id])

    def user_name(self):
        return self.scenario.user().upper()

    def _execute(self):
        super()._execute()
        self.service.userrole_get_no_relations_users(path_variable=self.path_variable(), data=self.data())

    def call_back(self, **kwargs):
        self.service.context[self.Id] = None
        for user in kwargs.get("users").list():
            if user.loginName() == self.user_name():
                self.service.context[self.Id] = user.id()

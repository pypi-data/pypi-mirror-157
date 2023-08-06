
from cjen.sco.standard_step import StandardStep


from eclinical.standard.scenarios.portal_scenario import PortalScenario


class PortalFindRole(StandardStep):
    Name = "portal_find_role.py"
    Id = "role_id"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)


    def path_variable(self): return dict(pageNo=1)

    def role_name(self):
        return self.scenario.role()

    def call_back(self, **kwargs):
        self.service.context[self.Id] = None
        for role in kwargs.get("role_list").all():
            if role.code() == self.role_name():
                self.service.context[self.Id] = role.id()

    def _execute(self):
        super()._execute()
        self.service.role_api_query(path_variable=self.path_variable())

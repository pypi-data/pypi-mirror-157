from cjen.sco.standard_step import StandardStep


from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.role.portal_find_role import PortalFindRole


class PortalCreateRole(StandardStep):
    Name = "portal_create_role.py"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)


    def _pre_processor(self):
        PortalFindRole(self.service, self.scenario).run()

    def ignore(self): return self.service.context[PortalFindRole.Id] is not None

    def category(self): return self.scenario.role().split("/")[0]

    def code(self): return self.scenario.role()

    def subCode(self): return self.scenario.role().split("/")[1]

    def data(self):
        return dict(category=self.category(), code=self.code(), subCode=self.subCode(), description="Test", active=True)

    def _execute(self):
        super()._execute()
        self.service.role_api_create_role(data=self.data())

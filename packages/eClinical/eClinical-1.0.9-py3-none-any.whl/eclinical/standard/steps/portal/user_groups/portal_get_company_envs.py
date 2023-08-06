from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep


from eclinical.standard.scenarios.portal_scenario import PortalScenario


class PortalGetCompanyEnvs(StandardStep):
    Name = "portal_get_company_envs"
    Id = "envIds"
    Object = "envObjects"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)

    def call_back(self, **kwargs):
        self.service.context["envIds"] = [company_env.id() for company_env in kwargs.get("company_envs").list()]
        self.service.context[self.Object] = [{f'{company_env.name()}': company_env.id()} for company_env in
                                              kwargs.get("company_envs").list()]

    def _execute(self):
        super()._execute()
        self.service.usergroups_api_company_envs()

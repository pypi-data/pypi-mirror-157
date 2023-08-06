from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.user_groups.portal_find_usergroup import PortalFindUserGroup


class PortalGetUserGroupInfo(StandardStep):
    Name = "portal_get_user_group_info"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)

    def _pre_processor(self):
        PortalFindUserGroup(self.service, self.scenario).run()

    def life_cycle(self):
        return self.scenario.life_cycle()

    def call_back(self, **kwargs):
        for company_multiple_env in kwargs.get("query").company_multiple_envs():
            if company_multiple_env.name() == self.life_cycle():
                self.service.context["company_multiple_env_id"] = company_multiple_env.id()

    def _execute(self):
        super()._execute()
        self.service.usergroups_user_group_info(path_variable=self.path_variable())

    def path_variable(self):
        return dict(userGroup_id=self.service.context["user_group_id"])

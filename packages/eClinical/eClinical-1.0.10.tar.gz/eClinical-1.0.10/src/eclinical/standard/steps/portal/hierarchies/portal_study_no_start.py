from cjen.exceptions import JsonPathNotFoundErr

from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.hierarchies.portal_find_study import PortalFindStudy


class PortalStudyNoStart(StandardStep):
    Name = "portal_study_no_start.py"
    System = "not_startup_study"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)


    def _pre_processor(self):
        if not self.service.context[PortalFindStudy.Id]:
            PortalFindStudy(self.service, self.scenario).run()

    def _execute(self):
        super()._execute()
        self.service.hierarchies_study_systems(path_variable=self.path_variable())

    def life_cycle(self):
        return self.scenario.life_cycle()

    def call_back(self, **kwargs):
        try:
            self.service.context[self.System] = [app.id() for app in kwargs.get("systems").no_rel_apps()]
        except JsonPathNotFoundErr as je:
            self.service.context[self.System] = None

    def path_variable(self):
        return dict(study_id=self.service.context[PortalFindStudy.Id], env_id=self.service.context[self.life_cycle()])

import os.path
from eclinical import Environment

from eclinical.standard.portal.portal_api import PortalApi
from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.hierarchies.portal_create_study import PortalCreateStudy
from eclinical.standard.steps.portal.hierarchies.portal_startup_study import PortalStartupStudy


class ScoCreateStudy:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario = PortalScenario(scenario_dir)
        self.service = PortalApi(environment)
        self.scenario.append_step(PortalCreateStudy, self.service)
        self.scenario.append_step(PortalStartupStudy, self.service)

    def run(self): self.scenario.run()


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    envir = Environment.loader("DEV_01")
    sco = ScoCreateStudy(sco_dir, envir)
    sco.run()

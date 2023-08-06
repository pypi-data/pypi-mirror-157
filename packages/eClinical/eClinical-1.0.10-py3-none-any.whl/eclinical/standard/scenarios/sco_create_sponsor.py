import os.path
from eclinical import Environment

from eclinical.standard.portal.portal_api import PortalApi
from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.hierarchies.portal_create_sponsor import PortalCreateSponsor
from eclinical.standard.steps.portal.hierarchies.portal_startup_sponsor import PortalStartSponsor


class ScoCreateSponsor:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario = PortalScenario(scenario_dir)
        # service = Hierarchies(environment)
        self.service = PortalApi(environment)
        self.scenario.append_step(PortalCreateSponsor, self.service)
        self.scenario.append_step(PortalStartSponsor, self.service)

    def run(self): self.scenario.run()


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    envir = Environment.loader("DEV_01")
    sco = ScoCreateSponsor(sco_dir, envir)
    sco.run()

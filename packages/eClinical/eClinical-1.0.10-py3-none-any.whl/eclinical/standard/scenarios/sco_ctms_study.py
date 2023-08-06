import os

from eclinical import Environment
from eclinical.standard.ctms.ctms_api import CtmsApi
from eclinical.standard.scenarios.ctms_scenario import CtmsScenario
from eclinical.standard.steps.ctms.ctms_common_country import CtmsCommonCountry
from eclinical.standard.steps.ctms.ctms_create_site_entity import CtmsCreateSiteEntity
from eclinical.standard.steps.ctms.ctms_find_site import CtmsFindSite
from eclinical.standard.steps.ctms.ctms_find_study import CtmsFindStudy
from eclinical.standard.steps.ctms.ctms_find_study_site import CtmsFindStudySite
from eclinical.standard.steps.ctms.ctms_study_set_site import CtmsStudySetSite
from eclinical.standard.steps.ctms.ctms_submit_study_basic_info import CtmsSubmitStudyBasicInfo


class ScoCtmsStudy:
    def __init__(self, scenario_dir, environment: Environment):
        self.scenario = CtmsScenario(scenario_dir, CtmsApi(environment))
        # service =
        self.scenario.add_step(CtmsCommonCountry)
        self.scenario.add_step(CtmsFindStudy)
        self.scenario.add_step(CtmsSubmitStudyBasicInfo)
        self.scenario.add_step(CtmsFindSite)
        self.scenario.add_step(CtmsCreateSiteEntity)
        self.scenario.add_step(CtmsFindStudySite)
        self.scenario.add_step(CtmsStudySetSite)

    def run(self): self.scenario.run()


if __name__ == '__main__':
    sco_dir = os.path.join("new_study")
    envir = Environment.loader("DEV_03")
    sco = ScoCtmsStudy(sco_dir, envir)
    sco.run()

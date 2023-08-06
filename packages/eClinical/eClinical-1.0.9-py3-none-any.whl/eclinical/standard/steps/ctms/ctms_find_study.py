from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.ctms_scenario import CtmsScenario


class CtmsFindStudy(StandardStep):
    Name = "ctms_find_study.py"
    Info = "ctms_study_dto"

    def __init__(self, service, scenario: CtmsScenario):
        super().__init__(service, scenario)
        self.service.context[self.Info] = None

    def call_back(self, **kwargs):
        for study in kwargs.get("studies").list():
            if study.name() == self.scenario.study():
                self.service.context[self.Info] = dict(id=study.id(), name=study.name())

    def _execute(self):
        super()._execute()
        self.service.study_management_get_study()

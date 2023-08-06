from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.ctms_scenario import CtmsScenario
from eclinical.standard.steps.ctms.ctms_find_site import CtmsFindSite
from eclinical.standard.steps.ctms.ctms_find_study import CtmsFindStudy
from eclinical.standard.steps.ctms.ctms_find_study_site import CtmsFindStudySite


class CtmsStudySetSite(StandardStep):
    Name = "ctms_set_site.py"

    def __init__(self, service, scenario: CtmsScenario):
        super().__init__(service, scenario)

    def sites(self):
        return self.scenario.sites()

    def _pre_processor(self):
        CtmsFindSite(self.service, self.scenario).run()
        CtmsFindStudySite(self.service, self.scenario).run()

    def data(self):
        site_codes = []
        for site_code in self.sites():
            for exist_site in self.service.context[CtmsFindStudySite.Info]:
                if exist_site.siteCode() == site_code: continue
            site_codes.append(site_code)
        return [{"siteId": f"{self.service.context[CtmsFindSite.Info].get(site_code)}",
                 "siteName": site_code,
                 "siteCode": site_code,
                 "timezoneId": '0',
                 "languageId": '2',
                 "expectedSubject": '100',
                 "studyId": f'{self.service.context[CtmsFindStudy.Info].get("id")}',
                 "menuId": '5080', } for site_code in site_codes]

    def _execute(self):
        super()._execute()
        for site_data in self.data():
            self.service.study_management_add_site(data=site_data)

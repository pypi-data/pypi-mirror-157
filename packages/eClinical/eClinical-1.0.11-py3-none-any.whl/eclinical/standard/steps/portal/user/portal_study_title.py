from cjen.sco.standard_step import StandardStep


from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.user.portal_find_user import PortalFindUser
from eclinical.standard.steps.portal.user.portal_user_access import PortalUserAccess


class PortalStudyTitle(StandardStep):
    Name = "portal_study_title.py"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)


    def _pre_processor(self): ...

    def path_variable(self):
        return dict(user_id=self.service.context[PortalFindUser.Id])

    def data(self):
        return [dict(studyId=study_id,
                     title=f'Title Of {study_id}',
                     userId=self.service.context[PortalFindUser.Id])
                for study_id in self.service.context[PortalUserAccess.StudiesId]]

    def _execute(self):
        super()._execute()
        self.service.user_api_study_title(path_variable=self.path_variable(), data=self.data())

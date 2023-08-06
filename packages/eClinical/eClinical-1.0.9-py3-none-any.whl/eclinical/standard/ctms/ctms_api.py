import cjen

from eclinical import CTMSLoginService, Environment
from eclinical.standard.base.ok_response import OkResponse
from eclinical.standard.ctms.dto.country import Countries
from eclinical.standard.ctms.dto.menus import Menus
from eclinical.standard.ctms.dto.site_entities import SiteEntities
from eclinical.standard.ctms.dto.sites_of_study import SitesOfStudy
from eclinical.standard.ctms.dto.studies import Studies
from eclinical.standard.steps.ctms.ctms_all_menu import CtmsAllMenu
from eclinical.standard.steps.ctms.ctms_common_country import CtmsCommonCountry
from eclinical.standard.steps.ctms.ctms_find_site import CtmsFindSite
from eclinical.standard.steps.ctms.ctms_find_study import CtmsFindStudy
from eclinical.standard.steps.ctms.ctms_find_study_site import CtmsFindStudySite


class CtmsApi(CTMSLoginService):
    def __init__(self, environment: Environment = None):
        super().__init__(environment)

    @cjen.http.get_mapping(uri="ctms/user/location/0/menu", json_clazz=Menus)
    @cjen.step.call(stepName=CtmsAllMenu.Name, argName="menus")
    def common_menu(self, menus: Menus, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="ctms/common/country", json_clazz=Countries)
    @cjen.step.call(stepName=CtmsCommonCountry.Name, argName="countries")
    def common_country(self, countries: Countries, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="ctms/site/information/list?pageNo={pageNo}&pageSize=25", json_clazz=SitesOfStudy)
    @cjen.step.call(stepName=CtmsFindStudySite.Name, argName="query")
    def study_management_site_list(self, path_variable, data, query: SitesOfStudy = None, resp=None, **kwargs):
        if not query.nextPage() == 0:
            self.study_management_site_list(path_variable=dict(pageNo=query.nextPage()), data=data)

    @cjen.http.post_mapping(uri="ctms/entity/site/list?pageNo={pageNo}&pageSize=25", json_clazz=SiteEntities)
    @cjen.step.call(stepName=CtmsFindSite.Name, argName="site_entities")
    def entity_management_site_list(self, path_variable, site_entities: SiteEntities, resp=None, **kwargs):
        if CtmsFindSite.NoFill in self.context[CtmsFindSite.Info].values():
            if not site_entities.nextPage() == 0:
                self.entity_management_site_list(path_variable=dict(pageNo=site_entities.nextPage()))

    @cjen.http.upload_mapping(uri="ctms/entity/site/info/save")
    def entity_management_add_site(self, data, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="ctms/study/basic/info", json_clazz=OkResponse)
    def study_management_submit_info(self, data, ok: OkResponse, resp=None, **kwargs):
        ...

    @cjen.http.upload_mapping(uri="ctms/site/basic/info", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def study_management_add_site(self, data, ok: OkResponse, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="ctms/study/query?pageNo=1&pageSize=25", json_clazz=Studies)
    @cjen.step.call(stepName=CtmsFindStudy.Name, argName="studies")
    def study_management_get_study(self, studies: Studies = None, resp=None, **kwargs):
        ...


if __name__ == "__main__":
    ctms = CtmsApi(Environment.loader("DEV_03"))
    for site in [[100990, "D007"],
                 [101000, "D008"],
                 [101010, "D009"],
                 [101020, "D010"],
                 [101030, "D011"],
                 [101040, "D012"],
                 [101050, "D013"],
                 [101060, "D014"],
                 [101070, "D015"],
                 [101080, "D016"],
                 [101090, "D017"],
                 [101100, "D018"],
                 [101110, "D019"],
                 [101120, "D020"],
                 [101130, "D021"],
                 [101140, "D022"],
                 [101150, "D023"],
                 [101160, "D024"],
                 [101170, "D025"],
                 [101180, "D026"],
                 [102370, "D030"],
                 [102380, "D027"],
                 [102390, "D028"],
                 [102400, "D029"]]:
        ctms.study_management_add_site(data={"siteId": f'{site[0]}',
                                             "siteName": site[1],
                                             "siteCode": site[1],
                                             "timezoneId": '0',
                                             "languageId": '2',
                                             "expectedSubject": '100',
                                             "studyId": '818',
                                             "menuId": '5080', })

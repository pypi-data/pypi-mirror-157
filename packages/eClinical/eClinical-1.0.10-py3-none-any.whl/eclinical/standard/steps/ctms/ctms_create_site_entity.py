from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.ctms_scenario import CtmsScenario
from eclinical.standard.steps.ctms.ctms_all_menu import CtmsAllMenu
from eclinical.standard.steps.ctms.ctms_common_country import CtmsCommonCountry
from eclinical.standard.steps.ctms.ctms_find_site import CtmsFindSite


class CtmsCreateSiteEntity(StandardStep):
    Name = "ctms_create_site_entity.py"

    def __init__(self, service, scenario: CtmsScenario):
        super().__init__(service, scenario)

    def _pre_processor(self):
        CtmsCommonCountry(self.service, self.scenario).run()
        CtmsAllMenu(self.service, self.scenario).run()

    def code_of_menus(self):
        return ["menu.ctms_entity_management", "menu.ctms_entity_management_site"]

    def find_country_id(self):
        return self.service.context[CtmsCommonCountry.Country].get("Afghanistan")

    def find_menu_id(self, menus_code, menu_tree, level=0):
        if menu_tree is not None:
            for menu in menu_tree:
                if menu.get("code") == menus_code[level]:
                    if level + 1 == len(self.code_of_menus()): return menu.get("id")
                    return self.find_menu_id(menus_code, menu.get("children"), level + 1)
        raise Exception(f'can not find {self.code_of_menus()}')

    def sites(self):
        return self.scenario.sites()

    def ignore(self):
        new_sites = list(filter(lambda dict_item: dict_item[1] == CtmsFindSite.NoFill, self.service.context[CtmsFindSite.Info].items()))
        return len(new_sites) == 0

    def data(self):
        menu_id = self.find_menu_id(self.code_of_menus(), self.service.context[CtmsAllMenu.Menu])
        country_id = self.find_country_id()
        new_sites = dict(filter(lambda dict_item: dict_item[1] == CtmsFindSite.NoFill, self.service.context[CtmsFindSite.Info].items()))

        return [
            {"siteId": "null",
             "siteName": site_name,
             "postalOrZoneCode": "0",
             "countryId": f'{country_id}',
             "provinceOrState": "China",
             "city": "China",
             "phone": "88888888",
             "fax": "",
             "email": "",
             "address": "China",
             "active": "true",
             "menuId": f'{menu_id}'} for site_name, site_id in new_sites.items()]

    def _execute(self):
        super()._execute()
        for d in self.data():
            self.service.entity_management_add_site(data=d)

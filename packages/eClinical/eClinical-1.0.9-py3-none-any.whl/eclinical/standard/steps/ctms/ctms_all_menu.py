from cjen.sco.standard_step import StandardStep

from eclinical.standard.scenarios.ctms_scenario import CtmsScenario


class CtmsAllMenu(StandardStep):
    Name = "ctms_all_menu.py"
    Menu = "ctms_all_menu"

    def __init__(self, service, scenario: CtmsScenario):
        super().__init__(service, scenario)



    def ignore(self):
        try:
            if self.service.context[self.Menu] is not None:
                return True
        except Exception as e:
            return False

    def call_back(self, **kwargs):
        self.service.context[self.Menu] = kwargs.get("menus").payload()

    def _execute(self):
        super()._execute()
        self.service.common_menu()

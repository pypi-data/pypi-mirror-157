from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep


class CtmsCommonCountry(StandardStep):
    Name = "ctms_common_country.py"
    Country = "CtmsCommonCountry"

    def __init__(self, service, scenario: Scenario):
        super().__init__(service, scenario)

    def ignore(self):
        try:
            if self.service.context[self.Country] is not None:
                return True
        except Exception as e:
            return False

    def call_back(self, **kwargs):
        # self.service.context[self.Country] = [{f'{country.name()}': country.id()} for country in kwargs.get("countries").list()]
        self.service.context[self.Country] = dict(zip([country.name() for country in kwargs.get("countries").list()],
                                                                                                 [country.id() for country in kwargs.get("countries").list()]))

    def _execute(self):
        super()._execute()
        self.service.common_country()

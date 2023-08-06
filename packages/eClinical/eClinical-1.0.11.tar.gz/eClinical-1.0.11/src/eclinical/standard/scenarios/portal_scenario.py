from cjen.sco.scenario import Scenario


class PortalScenario(Scenario):
    def __init__(self, scenario_dir):
        super().__init__(scenario_dir)

    def sponsor(self):
        return self.get("sponsor").get("name")

    def study(self):
        return self.get("study").get("name")

    def life_cycle(self):
        return self.get("life_cycle").get("env")

    def user_group(self):
        return self.get("user_groups").get("name")

    def user_group_sites(self):
        return self.get("user_groups").get("sites")

    def user(self):
        return self.get("user").get("name")

    def role(self):
        return self.get("user_role").get("name")
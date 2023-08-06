from cjen.sco.standard_step import StandardStep


from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.role.portal_find_role import PortalFindRole


class PortalGetPermissionTree(StandardStep):
    Name = "portal_get_permission_tree.py"
    IdOfAllPermission = "all_permissions_ids"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)

    def _pre_processor(self):
        PortalFindRole(self.service, self.scenario).run()

    def path_variable(self):
        return dict(role_id=self.service.context[PortalFindRole.Id])

    def _execute(self):
        super()._execute()
        self.service.role_api_all_permission_tree(path_variable=self.path_variable())

    def call_back(self, **kwargs):
        ids = set()
        for system in kwargs.get("pt").systems():
            self.get_permission_id(system, ids)
        self.service.context[self.IdOfAllPermission] = list(ids)

    def get_permission_id(self, node, cache):
        for menu in node.get("children"):
            cache.add(menu.get("id"))
            if menu.get("children"):
                self.get_permission_id(menu, cache)

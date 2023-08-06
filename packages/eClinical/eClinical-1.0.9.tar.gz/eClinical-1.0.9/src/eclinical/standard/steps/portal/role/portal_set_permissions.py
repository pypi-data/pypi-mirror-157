from cjen.sco.standard_step import StandardStep


from eclinical.standard.scenarios.portal_scenario import PortalScenario
from eclinical.standard.steps.portal.role.portal_find_role import PortalFindRole
from eclinical.standard.steps.portal.role.portal_get_permission_tree import PortalGetPermissionTree


class PortalSetPermissions(StandardStep):
    Name = "portal_set_permissions.py"

    def __init__(self, service, scenario: PortalScenario):
        super().__init__(service, scenario)


    def _pre_processor(self):
        PortalFindRole(self.service, self.scenario).run()
        PortalGetPermissionTree(self.service, self.scenario).run()

    def data(self):
        return [dict(permissionId=pid, roleId=self.service.context[PortalFindRole.Id])
                for pid in self.service.context[PortalGetPermissionTree.IdOfAllPermission]]

    def path_variable(self):
        return dict(role_id=self.service.context[PortalFindRole.Id])

    def _execute(self):
        super()._execute()
        self.service.role_api_set_permissions(path_variable=self.path_variable(), data=self.data())

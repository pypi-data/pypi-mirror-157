import cjen
from cjen.sco.step_definitions import StepDefinitions

from eclinical import PortalLoginService, Environment
from eclinical.standard.base.ok_response import OkResponse
from eclinical.standard.portal.dto.company_envs import CompanyEnvs
from eclinical.standard.portal.dto.envs import Envs
from eclinical.standard.portal.dto.group_user import GroupUsers
from eclinical.standard.portal.dto.hierarchy import Hierarchy
from eclinical.standard.portal.dto.permission_tree import PermissionTree
from eclinical.standard.portal.dto.query_studies import QueryStudies
from eclinical.standard.portal.dto.query_user_groups import QueryUserGroups
from eclinical.standard.portal.dto.querysponsors import QuerySponsors
from eclinical.standard.portal.dto.role_list import RoleList
from eclinical.standard.portal.dto.role_rel_user import RoleRelUsers
from eclinical.standard.portal.dto.systems import Systems
from eclinical.standard.portal.dto.user_access import UserAccess
from eclinical.standard.portal.dto.user_group_info import UserGroupInfo
from eclinical.standard.portal.dto.user_group_role_rel import UserGroupRoleRel
from eclinical.standard.portal.dto.user_roles import UserRoles
from eclinical.standard.portal.dto.users import Users
from eclinical.standard.steps.portal.hierarchies.portal_find_sponsor import PortalFindSponsor
from eclinical.standard.steps.portal.hierarchies.portal_find_study import PortalFindStudy
from eclinical.standard.steps.portal.hierarchies.portal_sponsor_no_start import PortalSponsorNoStart
from eclinical.standard.steps.portal.hierarchies.portal_study_no_start import PortalStudyNoStart
from eclinical.standard.steps.portal.role.portal_find_role import PortalFindRole
from eclinical.standard.steps.portal.role.portal_get_permission_tree import PortalGetPermissionTree
from eclinical.standard.steps.portal.user.portal_associated_usergroup import PortalAssociatedUserGroup
from eclinical.standard.steps.portal.user.portal_find_user import PortalFindUser
from eclinical.standard.steps.portal.user.portal_find_user_role import PortalFindUserRole
from eclinical.standard.steps.portal.user_groups.portal_find_un_added_user import PortalFindUnAddedUser
from eclinical.standard.steps.portal.user_groups.portal_find_usergroup import PortalFindUserGroup
from eclinical.standard.steps.portal.user_groups.portal_get_company_envs import PortalGetCompanyEnvs
from eclinical.standard.steps.portal.user_groups.portal_get_lifecycle_hierarchies import PortalGetLifeCycleHierarchies
from eclinical.standard.steps.portal.user_groups.portal_get_user_group_info import PortalGetUserGroupInfo
from eclinical.standard.steps.portal.user_groups.portal_life_cycle import PortalLifeCycle
from eclinical.standard.steps.portal.user_roles.portal_find_no_rel_user import PortalFindNoRelUser
from eclinical.standard.steps.portal.user_roles.portal_get_user_role import PortalGetUserRole


class PortalApi(PortalLoginService):
    def __init__(self, environment: Environment = None):
        super().__init__(environment)
        self.step_definitions = StepDefinitions()

    @cjen.http.get_mapping(uri="admin/company/envs", json_clazz=Envs)
    @cjen.operate.asserts.validation_meta(meta_name="envs")
    @cjen.step.call(stepName=PortalLifeCycle.Name, argName="envs")
    def hierarchies_get_env_list(self, envs: Envs = None, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/company/env/{env_id}/hierarchies", json_clazz=QuerySponsors)
    @cjen.operate.asserts.validation_meta(meta_name="query")
    @cjen.step.call(stepName=PortalFindSponsor.Name, argName="query")
    def hierarchies_get_sponsor(self, path_variable, query: QuerySponsors = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/study/query?pageNo={pageNo}&pageSize=25", json_clazz=QueryStudies)
    @cjen.step.call(stepName=PortalFindStudy.Name, argName="query")
    def hierarchies_get_study(self, path_variable, data, query: QueryStudies = None, resp=None, **kwargs):
        if not self.context[PortalFindStudy.Id]:
            if not query.nextPage() == 0:
                self.hierarchies_get_study(path_variable=dict(pageNo=query.nextPage()), data=data)

    @cjen.http.post_mapping(uri="admin/sponsor", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok")
    def hierarchies_new_sponsor(self, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/study", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok")
    def hierarchies_new_study(self, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/sponsor/{sponsor_id}/env/{env_id}/systems", json_clazz=Systems)
    @cjen.step.call(stepName=PortalSponsorNoStart.Name, argName="systems")
    def hierarchies_sponsor_systems(self, path_variable, systems: Systems = None, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/study/{study_id}/env/{env_id}/systems", json_clazz=Systems)
    @cjen.step.call(stepName=PortalStudyNoStart.Name, argName="systems")
    def hierarchies_study_systems(self, path_variable, systems: Systems = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/study/{study_id}/env/{env_id}/database", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok")
    def hierarchies_study_startup(self, path_variable, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/sponsor/{sponsor_id}/env/{env_id}/database", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok")
    def hierarchies_sponsor_startup(self, path_variable, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.put_mapping(uri="admin/role/{role_id}/permissions", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def role_api_set_permissions(self, path_variable, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/role/{role_id}/allPermissionTree", json_clazz=PermissionTree)
    @cjen.step.call(stepName=PortalGetPermissionTree.Name, argName="pt")
    def role_api_all_permission_tree(self, path_variable, pt: PermissionTree = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/role")
    def role_api_create_role(self, data, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/role/category/list", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def role_api_category_list(self, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/role/query?pageNo={pageNo}&pageSize=25", json_clazz=RoleList)
    @cjen.step.call(stepName=PortalFindRole.Name, argName="role_list")
    def role_api_query(self, path_variable, role_list: RoleList, resp=None, **kwargs):
        ...

    @cjen.http.put_mapping(uri="admin/user/{user_id}/study_title?sendEmail=false", json_clazz=OkResponse)
    def user_api_study_title(self, path_variable, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/user/{user_id}/access_list", json_clazz=UserAccess)
    def user_api_user_access(self, path_variable, user_access: UserAccess = None, resp=None, **kwargs):
        from eclinical.standard.steps.portal.user.portal_user_access import PortalUserAccess
        self.step_definitions.call_back(PortalUserAccess.Name, user_access=user_access)

    @cjen.http.get_mapping(uri="admin/role/list", json_clazz=RoleList)
    @cjen.operate.asserts.validation_meta(meta_name="role_list", fields="procCode")
    @cjen.step.call(stepName=PortalFindUserRole.Name, argName="role_list")
    def user_api_role_list(self, role_list: RoleList = None, resp=None, **kwargs):
        ...

    @cjen.http.put_mapping(uri="admin/role/{user_id}/user_group_role_rel", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def user_api_append_user_group_role_rel(self, path_variable, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/user/{user_id}/user_group_role_rel", json_clazz=UserGroupRoleRel)
    @cjen.operate.asserts.validation_meta(meta_name="rel", fields="procCode")
    @cjen.step.call(stepName=PortalAssociatedUserGroup.Name, argName="rel")
    def user_api_user_group_role_rel(self, path_variable, rel: UserGroupRoleRel, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/user/query?pageNo={pageNo}&pageSize=25", json_clazz=Users)
    @cjen.step.call(stepName=PortalFindUser.Name, argName="users")
    def user_api_user_query(self, path_variable, users: Users = None, resp=None, **kwargs):
        if not self.context[PortalFindUser.Id]:
            if not users.nextPage() == 0:
                self.user_api_user_query(path_variable=dict(pageNo=users.nextPage()))

    @cjen.http.post_mapping(uri="admin/user", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def user_api_create_user(self, data, ok: OkResponse, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/userGroup/query?pageNo={pageNo}&pageSize=25", json_clazz=QueryUserGroups)
    @cjen.step.call(stepName=PortalFindUserGroup.Name, argName="users")
    def user_get_user_group(self, path_variable, query: QueryUserGroups = None, resp=None, **kwargs):
        if not self.context[PortalFindUserGroup.Id]:
            if not query.nextPage() == 0:
                self.user_get_user_group(path_variable=dict(pageNo=query.nextPage()))

    @cjen.http.put_mapping(uri="admin/company/env/{life_cycle_id}/user-group/{userGroup_id}/hierarchies", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def usergroups_api_set_lifecycle_hierarchies(self, path_variable, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/company/env/{life_cycle_id}/user-group/{userGroup_id}/hierarchies",
                           json_clazz=Hierarchy)
    @cjen.step.call(stepName=PortalGetLifeCycleHierarchies.Name, argName="hierarchies")
    def usergroups_api_get_lifecycle_hierarchies(self, path_variable, hierarchies: Hierarchy, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/userGroup/query?pageNo={pageNo}&pageSize=25", json_clazz=QueryUserGroups)
    @cjen.step.call(stepName=PortalFindUserGroup.Name, argName="query")
    def usergroups_get_user_group(self, path_variable, query: QueryUserGroups = None, resp=None, **kwargs):
        if not self.context[PortalFindUserGroup.Id]:
            if not query.nextPage() == 0:
                self.usergroups_get_user_group(path_variable=dict(pageNo=query.nextPage()))

    @cjen.http.get_mapping(uri="admin/userGroup/{userGroup_id}", json_clazz=UserGroupInfo)
    @cjen.step.call(stepName=PortalGetUserGroupInfo.Name, argName="query")
    def usergroups_user_group_info(self, path_variable, query: UserGroupInfo = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/userGroup", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def usergroups_create_user_group(self, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/user")
    def usergroups_create_user(self, data, resp=None, **kwargs):
        ...

    @cjen.http.get_mapping(uri="admin/company/envs", json_clazz=CompanyEnvs)
    @cjen.step.call(stepName=PortalGetCompanyEnvs.Name, argName="company_envs")
    def usergroups_api_company_envs(self, company_envs: CompanyEnvs = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/userGroup/{userGroup_id}/unAddedUsers?pageNo=1&pageSize=25",
                            json_clazz=GroupUsers)
    @cjen.step.call(stepName=PortalFindUnAddedUser.Name, argName="group_users")
    def usergroups_api_get_un_added_user(self, path_variable, group_users: GroupUsers = None, resp=None, **kwargs):
        if not self.context["user_group_id"]:
            if not group_users.nextPage() == 0:
                self.usergroups_get_user_group(path_variable=dict(pageNo=group_users.nextPage()))

    @cjen.http.post_mapping(uri="admin/userGroup/{userGroup_id}/add/users", json_clazz=OkResponse)
    @cjen.operate.asserts.validation_meta(meta_name="ok", fields="procCode")
    def usergroups_api_add_group_user(self, path_variable, data, ok: OkResponse = None, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/role/{role_id}/user_group_user")
    def userrole_api_user_group_user(self, path_variable, data, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/role/{role_id}/relation/user_group_users?pageNo={pageNo}&pageSize=25")
    def userrole_get_relations_users(self, path_variable, data, resp=None, **kwargs):
        ...

    @cjen.http.post_mapping(uri="admin/role/{role_id}/no_relation/user_group_users?pageNo={pageNo}&pageSize=25", json_clazz=RoleRelUsers)
    @cjen.step.call(stepName=PortalFindNoRelUser.Name, argName="users")
    def userrole_get_no_relations_users(self, path_variable, data, users: RoleRelUsers, resp=None, **kwargs):
        if not self.context[PortalFindNoRelUser.Id]:
            if not users.nextPage() == 0:
                self.userrole_api_get_user_roles(path_variable=dict(pageNo=users.nextPage(), role_id=path_variable.get("role_id")))

    @cjen.http.get_mapping(uri="admin/role/user_roles?pageNo={pageNo}&pageSize=25", json_clazz=UserRoles)
    @cjen.step.call(stepName=PortalGetUserRole.Name, argName="user_role")
    def userrole_api_get_user_roles(self, path_variable, user_role: UserRoles = None, resp=None, **kwargs):
        if not self.context[PortalGetUserRole.Id]:
            if not user_role.nextPage() == 0:
                self.userrole_api_get_user_roles(path_variable=dict(pageNo=user_role.nextPage()))

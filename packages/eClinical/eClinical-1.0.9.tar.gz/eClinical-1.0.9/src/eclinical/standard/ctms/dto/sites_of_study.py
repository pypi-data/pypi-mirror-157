import cjen
from cjen import MetaJson


class StudySite(MetaJson):
    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.siteName")
    def siteName(self): ...

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.siteCode")
    def siteCode(self): ...

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.studyId")
    def studyId(self): ...

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.id")
    def id(self): ...


class SitesOfStudy(MetaJson):
    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.payload.nextPage")
    def nextPage(self): ...

    @cjen.operate.common.value
    @cjen.operate.json.listOf(clazz=StudySite)
    @cjen.operate.json.one(json_path="$.payload.list")
    def list(self) -> list[StudySite]: ...

    @cjen.operate.asserts.equal(value=200)
    @cjen.operate.json.one(json_path="$.procCode")
    def procCode(self): ...

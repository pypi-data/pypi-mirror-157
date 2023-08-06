import cjen
from cjen import MetaJson


class SiteEntity(MetaJson):

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.siteName")
    def siteName(self): ...

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.id")
    def id(self): ...


class SiteEntities(MetaJson):
    
    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.payload.nextPage")
    def nextPage(self): ...
    
    @cjen.operate.common.value
    @cjen.operate.json.listOf(clazz=SiteEntity)
    @cjen.operate.json.one(json_path="$.payload.list")
    def list(self) -> list[SiteEntity]: ...

    @cjen.operate.asserts.equal(value=200)
    @cjen.operate.json.one(json_path="$.procCode")
    def procCode(self): ...

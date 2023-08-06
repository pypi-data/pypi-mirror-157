import cjen
from cjen import MetaJson


class Country(MetaJson):
    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.name")
    def name(self): ...

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.id")
    def id(self): ...


class Countries(MetaJson):
    
    @cjen.operate.common.value
    @cjen.operate.json.listOf(clazz=Country)
    @cjen.operate.json.one(json_path="$.payload")
    def list(self) -> list[Country]: ...
    
    @cjen.operate.asserts.equal(value=200)
    @cjen.operate.json.one(json_path="$.procCode")
    def procCode(self): ...

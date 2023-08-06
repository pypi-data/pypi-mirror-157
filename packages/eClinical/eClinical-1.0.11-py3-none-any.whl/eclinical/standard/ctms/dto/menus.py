import cjen
from cjen import MetaJson


class Menus(MetaJson):

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.payload")
    def payload(self): ...

    @cjen.operate.asserts.equal(value=200)
    @cjen.operate.json.one(json_path="$.procCode")
    def procCode(self): ...
    
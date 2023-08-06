#-----------------------------
# -- kongodb --
# types
#-----------------------------

from typing import Any

TYPES_MAP = {
    "sqlite": {
        "Integer": "INT",
        "String": "VARCHAR(%s)",
        "Bool": "INT(1)",
        "Datetime": "TIMESTAMP",
        "Numeric": "FLOAT"
    },
    "mysql": {
        "Integer": "INTEGER",
        "String": "VARCHAR(%s)",
        "Bool": "TINYINT(1)",
        "Datetime": "DATETIME",
        "Numeric": "DOUBLE PRECISION"
    },
    "postgresql": {
        "Integer": "INT",
        "String": "VARCHAR(%s)",
        "Bool": "BOOLEAN",
        "Datetime": "TIMESTAMP",
        "Numeric": "DOUBLE PRECISION"
    }
}


class BaseType(object):
    field_type = None
    name = None
    length = None
    index = None
    unique = None
    default = None
    null = True

    def __init__(self, name, length: int = None, index: bool = True, unique: bool = False, default: Any = None, null=True):
        self.name = name
        self.length = length
        self.index = index
        self.unique = unique
        # 'unique' triggers 'index'
        if self.unique is True:
            self.index = True
        self.default = default

    def column_type(self, adapter_name:str=None):
        m = TYPES_MAP.get(adapter_name)
        if m and m.get(self.field_type):
            f = m.get(self.field_type)
            if "%" in f and self.length:
                f = f % self.length
            return f
        return self.field_type


class IntegerType(BaseType):
    field_type = "Integer"


class StringType(BaseType):
    field_type = "String"

    def __init__(self, *a, **kw):
        if not kw.get("length"):
            kw["length"] = 255
        super().__init__(*a, **kw)


class BoolType(BaseType):
    field_type = "Bool"

    def __init__(self, *a, **kw):
        if "default" not in kw or kw.get("default") is None:
            kw["default"] = False
        kw["default"] = bool(kw["default"])
        super().__init__(*a, **kw)


class DatetimeType(BaseType):
    field_type = "Datetime"


class NumericType(BaseType):
    field_type = "Numeric"


class CustomType(BaseType):
    def __init__(self, field_type, *a, **kw):
        super().__init__(*a, **kw)
        self.field_type = field_type


def stmt_to_custom_type(stmt):
    """
      "column", # column only. Type is in
      "column:type", # column and type
      "column:type@index", # column, type and index
      "column:type@unique" # column type and unique index
      "column@unique" # column and unique index. Type is inferred
    """
    _type = "VARCHAR(255)"
    _name = stmt
    _index = False
    _unique = False
    if "@" in _name:
        _name, _index = _name.split("@")
        _index = "UNIQUE" if _index.upper() == "UNIQUE" else True
    if _index == "UNIQUE":
        _index = True
        _unique = True
    if ":" in _name:
        _name, _type = _name.split(":")

    return CustomType(field_type=_type, name=_name, index=_index, unique=_unique)

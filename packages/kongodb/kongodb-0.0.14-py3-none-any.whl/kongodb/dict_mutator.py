# -----------------------------
# -- kongodb --
# dict_mutator
# -----------------------------

import re
import copy
import arrow
from . import lib
from typing import Any, List

# Operators that work with list
LISTTYPES_OPERATORS = ["xadd", "xadd_many", "xrem", "xrem_many", "xpush", "xpush_many", "xpushl", "xpushl_many"]

# _NMutDict: A dict thats aggregates data to be mutated in a nested context
class _NMutDict(dict): pass

# _NMutList: A list of data to be mutatated in a nested context
class _NMutList(list): pass

# FlattenDictType - Data Type flatten_dict
class FlattenDictType(dict): pass

# To unset a value from being updated
class UndefinedOperatorValue(object): pass


def mutate(mutations: dict, init_data: dict = {}):
    """
    mutate

    Args:
        mutations:dict - data contains operators to update
        init_data:dict - initial data 

    Returns:
        tuple(updated_data:dict, oplog)

    """
    _muts = lib.flatten_dict(mutations)
    _inits = lib.flatten_dict(init_data)
    muts = {}
    _restructed = {}

    for k, v in _muts.items():
        # since data is flat, let's restructe some data so they can be properly mutated
        xl = list(filter(lambda v: v, re.split("(\:\$\w+)(?:\.)?", k)))
        if len(xl) > 2:
            _op = xl[1].replace(":$", "")
            if _op in LISTTYPES_OPERATORS:
                _pathkey = "%s:$%s" % (xl[0], _op)
                if _pathkey not in _restructed:
                    _restructed[_pathkey] = _NMutDict()
                _jpath = ".".join(xl[2:]).replace(".:$", ":$")
                _restructed[_pathkey][_jpath] = v
            else:
                muts[k] = _NMutList([_NMutDict(vv) if isinstance(vv, dict) else vv for vv in v]) if isinstance(v, list) else v
        else:
            # by default, data will be a :$set. This will allow inner updat
            k = "%s:$set" % k if ":$" not in k else k
            muts[k] = _NMutList([_NMutDict(vv) if isinstance(vv, dict) else vv for vv in v]) if isinstance(v, list) else v

    muts.update(_restructed)
    d, _ = _mutate(muts, _inits)
    return lib.unflatten_dict(d), _


def _mutate(mutations:FlattenDictType, init_data:FlattenDictType={}):
    """
    Update Operations

    Args:
        data:dict - data to run $ops on 


    Returns:
        tuple(updated_data:dict, oplog)

    Operators:
        $incr
        $decr
        $unset
        $timestamp
        $xadd - $xadd_many
        $xrem - $xrem_many
        $xpush - $xpush_many
        $xpushl - $xpushl_many
        $xpop
        $xpopl
        
    Example
        {
           "key:$incr": True|1,
           "key:$decr": True|1,
           "some.key:$unset": True,
           "some.list:$xadd": Any,
           "some.list:$xadd_many": [Any, Any, Any, ...],
           "some.list:$xrem": Any,
           "some.list:$xrem_many": [Any, Any, Any, ...],     
           "some.list:$xpush": Any,
           "some.list:$xpush_many": [Any, Any, Any, ...],   
           "some.list:$xpushl": Any,
           "some.list:$xpushl_many": [Any, Any, Any, ...],    
           "some.list:$xpop": True,
           "some.list:$xpopl: False,
           "some.timestampfield:$timestamp": True,             
           "some.timestampfield:$timestamp": "+1Day +2Hours 5Minutes"             
        }
    """
    data = copy.deepcopy(init_data)
    oplog = {}
    for path, value in mutations.items():
        if ":" in path:
            if ":$" not in path:
                continue
            
            # _NMutDict
            if isinstance(value, _NMutDict):
                value = _mutate(value)[0]
            # _NMutList
            if isinstance(value, _NMutList):
                value = [ _mutate(vv)[0] if isinstance(vv, dict) else vv for vv in value]

            oplog_path = path
            path, op = path.split(":$")

            # $set. literal assigment, leave as is 
            if op == "set":
                pass

            # $incr
            elif op == "incr":
                value = _get_int_data(data, path) + \
                    (value if isinstance(value, int) else 1)
                oplog[oplog_path] = value

            # $decr
            elif op == "decr":
                _ = (value if isinstance(value, int) else 1) * -1
                value = _get_int_data(data, path) + _
                oplog[oplog_path] = value

            # $unset
            elif op == "unset":
                v = _pop(data, path)
                oplog[oplog_path] = v
                value = UndefinedOperatorValue()

            # $timestamp
            elif op == "timestamp":
                dt = lib.get_timestamp()
                if value is True:
                    value = dt
                else:
                    try:
                        if isinstance(value, str):
                            value = _arrow_date_shifter(dt=dt, stmt=value)
                        else:
                            value = UndefinedOperatorValue()
                    except:
                        value = UndefinedOperatorValue()

            # LIST operators

            elif op in (
                "xadd", "xadd_many",
                "xrem", "xrem_many",
                "xpush", "xpush_many",
                "xpushl", "xpushl_many"
            ):
                values = _values_to_mlist(value, many=op.endswith("_many"))
                v = _get_list_data(data, path)

                # $xadd|$xadd_many
                if op.startswith("xadd"):
                    for val in values:
                        if val not in v:
                            v.append(val)
                    value = v

                # $xrem|$xrem_many
                elif op.startswith("xrem"):
                    _removed = False
                    for val in values:
                        if val in v:
                            _removed = True
                            v.remove(val)
                    if not _removed:
                        value = UndefinedOperatorValue()

                # $xpush|$xpush_many
                elif op in ("xpush", "xpush_many"):
                    v.extend(values)
                    value = v

                # $xpushl|$xpushl_many
                elif op in ("xpushl", "xpushl_many"):
                    v2 = list(values)
                    v2.extend(v)
                    value = v2

            # $xpop
            elif op == "xpop":
                v = _get_list_data(data, path)
                if len(v):
                    value = v[:-1]
                    oplog[oplog_path] = v[-1]

            # $xpopl
            elif op == "xpopl":
                v = _get_list_data(data, path)
                if len(v):
                    value = v[1:]
                    oplog[oplog_path] = v[0]

            # UndefinedOperatorValue
            else:
                value = UndefinedOperatorValue()

        if not isinstance(value, UndefinedOperatorValue):
            data[path] = value

    return data, oplog


def _get(data:dict, path):
    """
    _get: Alias to get data from a path
    """
    return data.get(path)

def _set(data:dict, path, value):
    """
    _set: Alias to set value in data
    """
    data[path] = value
    return data

def _pop(data, path):
    """
    _pop: Alias to remove object from data
    """
    if path in data:
        return data.pop(path)
    return None 

def _get_int_data(data: dict, path: str) -> int:
    """
    _get_int_data: Returns INT for number type operations
    """
    v = _get(data, path)
    if v is None:
        v = 0
    if not isinstance(v, int):
        raise TypeError("Invalid data type for '%s'. Must be 'int' " % path)
    return v


def _get_list_data(data: dict, path: str) -> list:
    """
    _get_list_data: Returns a data LIST, for list types operations
    """
    v = _get(data, path)
    if v is None:
        return []
    if not isinstance(v, list):
        raise TypeError("Invalid data type for '%s'. Must be 'list' " % path)
    return v


def _values_to_mlist(value, many=False):
    """
    _values_to_mlist: Convert data multiple list items
    """
    return [value] if many is False else value if isinstance(value, (list, tuple)) else [value]


def _arrow_date_shifter(dt: arrow.Arrow, stmt: str) -> arrow.Arrow:
    """
    To shift the Arrow date to future or past

    Args:
        dt:arrow.Arrow - 
        stmt:str - 
    Returns:
        arrow.Arrow


    Valid shift:
        YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, WEEKS

    Format: [[+/-][$NUMBER][$SHIFT][SPACE]... ]
        +1Days
        -3Hours 6Minutes
        +1Days 2Hours 3Minutes
        1Year 2Month +3Days 5Hours -6Minutes 3Seconds 5weeks
    """
    shifts = ["years", "months", "days",
              "hours", "minutes", "seconds", "weeks"]

    t = [t for t in stmt.split(" ") if t.strip(" ")]
    t2 = [re.findall(r'((?:\+|\-)?(?:\d+))?(\w+)?', s)[0] for s in t if s]
    t2 = [(t[1].lower(), int(t[0])) for t in t2 if t[0] and t[1]]
    kw = {}
    for k, v in t2:
        if k in shifts or "%ss" % k in shifts:
            k = k if k.endswith("s") else "%ss" % k
            kw[k] = v
    if kw:
        dt = dt.shift(**kw)
        return dt

    return dt


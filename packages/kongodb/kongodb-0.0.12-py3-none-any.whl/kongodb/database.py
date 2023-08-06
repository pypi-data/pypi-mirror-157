# -----------------------------
# -- kongodb --
# database
# -----------------------------


import copy 
from urllib.parse import urlparse
from typing import Any, List, Union
from . import adapters, dict_mutator, dict_query, lib, types, exceptions


SQL_DATETIME_FORMAT = "YYYY-MM-DD HH:mm:ss"
ADD_MANY_CHUNK_SIZE = 1000

class __Item(dict):
    NAMESPACE = None

    def _make_path(self, path):
        # if self.NAMESPACE:
        #     return "%s.%s" % (self.NAMESPACE, path)
        return path

    def _update(self, data):
        raise NotImplementedError()

    def get(self, path: str, default: Any = None) -> Any:
        """
        GET: Return a property by key/DotNotation

        ie: 
            #get("key.deep1.deep2.deep3")

        Args:
            path:str - the dotnotation path
            default:Any - default value 

        Returns:
            Any
        """
        path = self._make_path(path)
        return lib.dict_get(obj=dict(self), path=path, default=default)

    def set(self, path: str, value: Any):
        """
        SET: Set a property by key/DotNotation

        Args:
            path:str - the dotnotation path
            value:Any - The value

        Returns:
            Void
        """

        path = self._make_path(path)
        self._update({path: value})

    def len(self, path: str):
        """
        Get the length of the items in a str/list/dict
        Args:
            path:str - the dotnotation path
        Returns:
            data that was removed
        """
        path = self._make_path(path)
        v = self.get(path)
        return len(v) if v else 0

    def incr(self, path: str, incr=1):
        """
        INCR: increment a value by 1
        Args
            path:str - path
            incr:1 - value to inc by
        Returns:    
            int - the value that was incremented
        """
        op = "%s:$incr" % self._make_path(path)        
        oplog = self._update({op: incr})
        return oplog.get(op)

    def decr(self, path: str, decr=1):
        """
        DECR: decrement a value by 1
        Args
            path:str - path
            decr:1 - value to dec by
        Returns:    
            int - the value that was decremented
        """
        op = "%s:$decr" % self._make_path(path)

        oplog = self._update({op: decr})
        return oplog.get(op)

    def unset(self, path: str):
        """ 
        UNSET: Remove a property by key/DotNotation and return the value

        Args:
            path:str

        Returns:
            Any: the value that was removed
        """
        path = self._make_path(path)
        self._update({"%s:$unset" % path: True})

    def xadd(self, path: str, values):
        """
        LADD: Add *values if they don't exist yet

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xadd" % self._make_path(path)
        self._update({op: values})

    def xadd_many(self, path: str, *values: List[Any]):
        """
        LADD: Add *values if they don't exist yet

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xadd_many" % self._make_path(path)
        self._update({op: values})

    def xrem(self, path: str, values):
        """
        LREM: Remove items from a list

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xrem" % self._make_path(path)
        oplog = self._update({op: values})
        return oplog.get(op)

    def xrem_many(self, path: str, *values: List[Any]):
        """
        LREM: Remove items from a list

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xrem_many" % self._make_path(path)
        oplog = self._update({op: values})
        return oplog.get(op)

    def xpush(self, path: str, values: Any):
        """
        LPUSH: push item to the right of list. 

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xpush" % self._make_path(path)
        self._update({op: values})

    def xpush_many(self, path: str, *values: List[Any]):
        """
        LPUSH: push item to the right of list. 

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xpush_many" % self._make_path(path)
        self._update({op: values})

    def xpushl(self, path: str, values: Any):
        """
        LPUSH: push item to the right of list. 

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xpushl" % self._make_path(path)
        self._update({op: values})

    def xpushl_many(self, path: str, *values: List[Any]):
        """
        LPUSH: push item to the right of list. 

        Args:
            path:str - the dotnotation path
            *values: set of items
        Returns:
            list: updated data
        """
        op = "%s:$xpush_many" % self._make_path(path)
        self._update({op: values})

    def xpop(self, path: str):
        """
        Remove value at the end an array/list
        Args:
            path:str - the dotnotation path
        Returns:
            data that was removed

        """
        op = "%s:$xpop" % self._make_path(path)
        oplog = self._update({op: True})
        return oplog.get(op)

    def xpopl(self, path: str):
        """
        Remove value at the beginning an array/list
        Args:
            path:str - the dotnotation path
        Returns:
            data that was removed        
        """
        op = "%s:$xpopl" % self._make_path(path)
        oplog = self._update({op: True})
        return oplog.get(op)


class Database(object):
    """
    :: Database

    Class to create a connection to an adapter and select a collection
    """

    def __init__(self, dsn_adapter: Union[str, adapters.BaseAdapter]):
        """
        Connect database 

        Return:
            dsn: str
                *`scheme://hostname` should be there at minimum
                - sqlite://
                - sqlite://./file.db
                - mysql://username:password@hostname:port/dbname
                - mariadb://username:password@hostname:port/dbname
        """
        if isinstance(dsn_adapter, adapters.BaseAdapter):
            self.db = dsn_adapter
        elif isinstance(dsn_adapter, str):
            # adapters.SQLiteAdapter(file=":memory:")
            _ = urlparse(dsn_adapter)
            # scheme, username, password, hostname, port, path.strip("/")
            if _.scheme == "sqlite":
                self.db = adapters.SQLiteAdapter(dsn_adapter)
            elif _.scheme in ["mysql", "mariadb"]:
                self.db = adapters.MySQLAdapter(dsn_adapter)


    def collection(self, name: str, columns: list = None):
        """
        Select a collection

        Args:
            name: str - collection name
            columns: list - list of columns and indexes to add

        Returns:
            Collection
        """
        collection = Collection(self.db, name)
        if columns:
            collection.add_columns(columns)
        return collection

    def drop_collection(self, name):
        """
        Drop/Delete a table/collection

        Returns:
            None
        """
        self.db.drop_collection(name)

    @property
    def collections(self) -> list:
        """
        List collections in the database

        Returns: 
          list
        """
        return self.db.get_collections()

    @staticmethod
    def utcnow():
        return lib.get_timestamp()


class CollectionItem(__Item):
    """
    CollectionItem/ActiveRecord

    Every row is a document in Kongodb
    """
    SUBCOLLECTION_NAMESPACE = "/subcollection/%s"

    def __init__(self, collection, row: dict):
        self._collection = collection
        self._load(row)

    def update(self, data: dict):
        """
        UPDATE: Update the active CollectionItem

        Returns:
            CollectionItem
        """
        self._update(data)

    def delete(self):
        """
        DELETE: Delete the Doument from the collection

        Returns:
            None
        """
        self._collection.delete_id(self._id)
        self._clear_self()

    def subcollection(self, name: str, constraints: list = None):
        collection_info = _CollectionInfo__(self._collection, name)
        _constraints = collection_info.get_subcollection_constraints(name) or []
        if constraints and set(constraints) != set(_constraints):
            collection_info.set_subcollection_constraints(name, constraints)
            _constraints = constraints
        return SubCollection(item=self, name=name, constraints=_constraints)

    @property
    def subcollections(self):
        return list(self.get("/collections").keys()) or []

    def drop_subcollection(self, name: str):
        try:
            self.unset("/collections.%s" % name)
        except KeyError as _:
            pass
        return True

    def save(self):
        """
        To commit the data when it's mutated outside.
            doc = CollectionItem()
            doc["xone"][1] = True
            doc.save()
        """
        data = dict(self)
        self._update(data)

    def _update(self, mutations: dict):
        """
        Return oplog
        """
        data = dict(self)
        doc, oplog = dict_mutator.mutate(mutations, data)
        row = self._collection.update_id(_id=self._id, doc=doc, replace=True, _as_document=False)
        self._load(row)
        return oplog

    def _load(self, row: dict):
        """
        load the content into the document

        Args:
            row: dict
        """
        self._clear_self()
        row = _parse_row(row)
        self._id = row.get("_id")
        super().__init__(row)

    def _clear_self(self):
        """ clearout all properties """
        for _ in list(self.keys()):
            if _ in self:
                del self[_]


class Collection(object):
    """
    Collection/Table

    """

    DEFAULT_COLUMNS = ["_id", "_json", "_created_at", "_modified_at"]
    _columns = []
    _indexes = []

    def __init__(self, conn: adapters.BaseAdapter, name):
        self.name = name
        self.db = conn
        self.db.create_collection(self.name)

    def __len__(self):
        return self.size

    # ---- properties ----

    @property
    def columns(self) -> list:
        """ 
        Get the list of all the columns name

        Returns:
            list
        """
        return self.db.get_columns(self.name)

    @property
    def indexes(self) -> list:
        """
        Get the list of all indexes

        Returns:
            list
        """
        return self.db.get_indexes(self.name)

    @property
    def size(self) -> int:
        """
        Get the total entries in the collection

        Returns:
            int
        """
        return self.db.get_size(self.name)

    # ---- methods ----

    def get(self, _id: str) -> CollectionItem:
        """
        Get a document by _id
        Alias to find_one(_id)

        Returns:
            CollectionItem
        """
        return self.find_one(_id=_id)

    def find_one(self, *a, **kw) -> CollectionItem:
        """
        Retrieve 1 document by _id, or other filters

        Args:
          _id:str - the document id
          _as_document:bool - when True return CollectionItem
          **kw other query

        Returns:
          CollectionItem

        Examples:
            #.find_one()
            #.find_one('IDfyeiquyteqtyqiuyt')
            #.find_one(_id="ID....")
            #.find_one(key1=value1, key2=value2, ...)
            #.find_one({key: val, key2: val2, ...})

        """

        _as_document = True
        if "_as_document" in kw:
            _as_document = kw.pop("_as_document")

        # expecting the first arg to be _id
        filters = kw or {} 
        if a and a[0]:
            if isinstance(a[0], dict):
                filters = a[0]
            else: 
                filters = {"_id": a[0]}
        r = self.find(filters=filters, limit=1, _as_document=_as_document)
        return r[0] if len(r) else None

    def find_all(self, *a, **kw) -> List[CollectionItem]:
        """
        Retrieve all docuemts based on criteria return in a list

        Returns:
            List[CollectionItem]
        """
        return list(self.find(*a, **kw))

    def find(self, filters: dict = {}, sorts: dict = {}, limit: int = 10, skip: int = 0, _as_document=True) -> dict_query.Cursor:
        """
        To fetch data from the collection

        Smart Query
          Allow to use primary indexes from sqlite 
          then do the xtra from parsing the documents

        Args:
          filters:dict - 
          sort:dict - {key: "DESC", key2: "ASC"}
          limit:int - 
          skit:int - 

        Returns:
          dictquery.Cursor
        """

        # SMART QUERY
        # Do the primary search in the columns
        # If there is more search properties, take it to the json
        xparams = []
        xquery = []

        smart_filters = _parse_smart_filtering(
            filters, indexed_columns=self.columns)

        # Build the SQL query
        query = "SELECT * FROM %s " % self.name

        # Indexed filtering
        if smart_filters["SQL_FILTERS"]:
            for f in smart_filters["SQL_FILTERS"]:
                xquery.append(" %s %s" % (f[0], f[1]))
                if isinstance(f[2], list):
                    for _ in f[2]:
                        xparams.append(_)
                else:
                    xparams.append(f[2])
        if xquery and xparams:
            query += " WHERE %s " % " AND ".join(xquery)

        # Perform JSON search, as we have JSON_FILTERS
        # Full table scan, relative to WHERE clause
        chunk = 100
        data = []
        if smart_filters["JSON_FILTERS"]:
            for chunked in self.db.fetchmany(query, xparams, chunk):
                if chunked:
                    rows = [_parse_row(row) for row in chunked]
                    for r in dict_query.query(rows, smart_filters["JSON_FILTERS"]):
                        data.append(r)
                else:
                    break
            if data:
                if _as_document:
                    data = [CollectionItem(self, d) for d in data]
            sorts = _parse_sort_dict(sorts, False)
            return dict_query.Cursor(data, sort=sorts, limit=limit, skip=skip)

        # Skip JSON SEARCH, use only SQL.
        # No need to look into the JSON. The DB is enough
        else:
            # order by
            sorts = _parse_sort_dict(sorts, True)
            if sorts:
                query += " ORDER BY "
                query += " ".join([" %s %s " % (_[0], _[1]) for _ in sorts])

            # limit/skip
            if limit or skip:
                query += " LIMIT ?, ?"
                xparams.append(skip or 0)
                xparams.append(limit or 10)

            res = self.db.fetchall(query, xparams)
            if _as_document:
                data = [CollectionItem(self, row) for row in res]
            else:
                data = list(res)
            return dict_query.Cursor(data)

    def add(self, data: dict, _as_document: bool = True) -> CollectionItem:
        """
        Add a new document in collection

        use Smart Insert, by checking if a value in the doc in is a column.

        Args:
          data:dict - Data to be inserted

        Returns:
            CollectionItem
        """
        if not isinstance(data, dict):
            raise TypeError('Invalid data type. Must be a dict')

        stmt, xparams = self._prepare_add(data=[data])
        self.db.execute(stmt, xparams[0])
        return self.find_one(_id=xparams[0][0], _as_document=_as_document)

    def add_many(self, data:List[dict]) -> bool:
        """
        Add many document at once.

        Args:
            data:list[dict]
        """

        if not isinstance(data, list):
            raise TypeError('Invalid data type. Must be a list')

        stmt, xparams = self._prepare_add(data=[data])
        for xdata in lib.chunk_list(xparams, ADD_MANY_CHUNK_SIZE):
            self.db.execute(stmt, xdata, many=True)
        return True

    def _prepare_add(self, data:list) -> tuple:
        """
        Prepare ADD/INSERT statement

        Returns 
            tuple(statement:str, data:List[list])
        """

        if not isinstance(data, list):
            raise TypeError('Invalid data type. Must be a list')

        data = copy.deepcopy(data)

        table_columns = self.columns
        _columns = None
        xparams = []
        for d in data:
            datax, _ = dict_mutator.mutate(d)
            _id = lib.gen_id()
            ts = lib.get_timestamp()
            f_ts = ts.format(SQL_DATETIME_FORMAT)
            datax.update({
                "_id": _id,
                "_created_at": ts,
                "_modified_at": ts,
            })

            _columns = ["_id", "_json", "_created_at", "_modified_at"]
            _params = [_id, lib.json_dumps(datax), f_ts, f_ts]
        
            # indexed data
            # some data can't be overwritten
            for col in table_columns:
                if col in datax and col not in _columns:
                    _columns.append(col)
                    _params.append(datax[col])

            xparams.append(_params)

        stmt = "INSERT INTO %s " % self.name
        stmt += " ( %s ) VALUES ( %s ) " % (",".join(_columns), ",".join(["?" for _ in xparams[0]]))
        return (stmt, xparams)

    def update(self, filters, data:dict): raise NotImplementedError()
    def delete(self, filters): raise NotImplementedError()

    def update_id(self, _id: str, doc: dict = {}, replace: bool = False, _as_document=True) -> CollectionItem:
        """
        To update a document

        Args:
          _id:str - document id
          doc:dict - the document to update
          replace:bool - By default document will be merged with existing data
                  When True, it will save it as is. 

        Returns:
            CollectionItem
        """
        ts = lib.get_timestamp()
        ts_f = ts.format(SQL_DATETIME_FORMAT)

        if replace:
            _doc = doc
        else:
            rdoc = self.find_one(_id=_id, _as_document=False)
            _doc = lib.dict_merge(lib.json_loads(rdoc["_json"]), doc)

        _doc["_modified_at"] = ts
        _restricted_columns = self.DEFAULT_COLUMNS[:]
        xcolumns = ["_json", "_modified_at"]
        xparams = [lib.json_dumps(_doc), ts_f]

        q = "UPDATE %s SET " % self.name

        # indexed data
        # some data can't be overriden
        for col in self.columns:
            if col in _doc and col not in _restricted_columns:
                xcolumns.append(col)
                xparams.append(_doc[col])
        q += ",".join(["%s = ?" % _ for _ in xcolumns])
        q += " WHERE _id=?"
        xparams.append(_id)
        self.db.execute(q, xparams)
        return self.find_one(_id=_id, _as_document=_as_document)

    def delete_id(self, _id: str) -> bool:
        """
        To delete an entry by _id

        Args:
            _id:str - entry id

        Returns:
            Bool
        """
        self.db.execute("DELETE FROM %s WHERE _id=?" % (self.name), (_id, ))
        return True

    def add_columns(self, columns: list, enforce_index=False):
        """
        To add columns. With options to add indexes

        Args:
            columns: List[str|types.BaseType]
        """
        cols_stmt = []
        for stmt in columns:
            if isinstance(stmt, types.BaseType):
                cols_stmt.append(stmt)
            elif isinstance(stmt, str):
                cols_stmt.append(types.stmt_to_custom_type(stmt))

        self.db.add_columns(table=self.name, cols_stmt=cols_stmt)

    def add_indexes(self, columns: List[str]):
        """
        To indexed columns

        Args: 
            columns:
                List[str]. Documentation-> #add_columns
        """
        self.add_columns(columns=columns, enforce_index=True)

    # TODO:
    # def update_many(self, data:dict, filters:dict)
    # def delete_many()


class SubCollection(object):
    _data = []
    _constraints = []

    def __init__(self, item: CollectionItem, name: str, constraints:list=None):
        self._item = item
        self._name = name
        self._collection_name = "/collections.%s" % name
        self._constraints = constraints
        self._load()

    def _load(self):
        self._data = self._item.get(self._collection_name) or []

    def _commit(self):
        self._item.set(self._collection_name, self._data)

    def _save(self, _id, data):
        _data = self._normalize_data()
        _data[_id] = data
        self._data = self._denormalize_data(_data)
        self._commit()        

    def _normalize_data(self) -> dict:
        return { d.get("_id"): d for d in self._data}

    def _denormalize_data(self, data:dict) -> list:
        return list(data.values())

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self.find())

    def add(self, data: dict):
        data, _ = dict_mutator.mutate(data.copy())

        if self._constraints:
            for c in  self._constraints:
                if c in data:
                    if self.find_one({c: data[c]}):
                        raise exceptions.ConstraintError("Key: %s" % c)

        _id = lib.gen_id()
        ts = lib.get_timestamp()
        doc = {
            **data,
            "_id": _id,
            "_created_at": ts,
            "_modified_at": ts
        }
        self._data.append(doc)
        self._commit()
        return SubCollectionItem(self, doc)

    def update(self, filters, mutations: dict):
        _data = self._normalize_data()
        for item in self.find(filters):
            ts = lib.get_timestamp()
            _id = item.get("_id")
            _default = {  # ensuring we do some data can't be overwritten
                "_id": _id,
                "_created_at": ts,
                "_modified_at": ts
            }
            upd, _ = dict_mutator.mutate(mutations, item)
            _data[_id] = {**upd, **_default}
        self._data = self._denormalize_data(_data)
        self._commit()

    def delete(self, filters: dict):
        _data = self._normalize_data()
        for item in self.find(filters):
            del _data[item.get("_id")]
        self._data = self._denormalize_data(_data)
        self._commit()

    def find(self, filters: dict = {}, sorts: dict = {}, limit: int = 10, skip: int = 0) -> dict_query.Cursor:
        """
        Args:
            filters:
            sorts:
            limit:
            skip:
        """
        data = dict_query.query(data=self._data, filters=filters)
        data = [SubCollectionItem(self, d) for d in data]
        sorts = _parse_sort_dict(sorts, False)
        return dict_query.Cursor(data, sort=sorts, limit=limit, skip=skip)

    def find_one(self, filters:dict={}):
        res = self.find(filters=filters, limit=1)
        if res:
            return list(res)[0]
        return None 

    def get(self, _id:str):
        return self.find_one({"_id": _id})

class SubCollectionItem(__Item):

    def __init__(self, subCollection: SubCollection, data):
        self.subCollection = subCollection
        self.NAMESPACE = self.subCollection._collection_name
        self._load(data)

    def _update(self, mutations):
        data = dict(self)
        mutations = copy.deepcopy(mutations)
        doc, oplog = dict_mutator.mutate(mutations, data)
        self.subCollection._save(self._id, doc)
        self._load(doc)
        return oplog

    def _load(self, data):
        self._id = data.get("_id")
        super().__init__(data)

class _CollectionInfo__(object):
    COLLECTION_NAME = "__collections_info__"

    def __init__(self, collection:Collection, collection_name:str):
        coll = Collection(collection.db, self.COLLECTION_NAME)
        coll.add_columns([types.StringType("collection_name", unique=True)])

        self.item = coll.find_one({"collection_name": collection_name})
        if not self.item:
            self.item = coll.add({"collection_name": collection_name})

    def get_subcollection_constraints(self, subcollection_name):
        path = "constraints.%s" % subcollection_name
        return self.item.get(path) or []

    def set_subcollection_constraints(self, subcollection_name, constraints:list):
        path = "constraints.%s" % subcollection_name
        if constraints and isinstance(constraints, list):
            return self.item.set(path, constraints)


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

def _parse_smart_filtering(filters: dict, indexed_columns: list = []) -> dict:
    """
    Smart Filter
    Breaks down the filters based on type. 
    - SQL_FILTERS: is more restrictive on what can be queried. 
                  Will be done at the SQL level
    - JSON_FILTERS: is more loose. 
                    It contains items that are not in the sql_filters. 
                    Will be done at the JSON level

    Args:
      filters: dict  - 
      indexed_columns: list - List of indexed sql columns/or other columns in the table 
                       this will allow with the smart filtering

    Returns: 
      dict:
        SQL_FILTERS
        JSON_FILTERS
    """

    # filter SQL_OPERATORS filters
    sql_filters = []
    json_filters = {}
    for k, v in filters.items():
        if dict_query.FILTER_OPERATOR in k:
            f, op = k.split(dict_query.FILTER_OPERATOR)
            if f in indexed_columns and op in dict_query.SQL_OPERATORS:
                sql_filters.append((f, dict_query.SQL_OPERATORS[op], v))
                continue
        else:
            if k in indexed_columns:
                sql_filters.append((k, dict_query.SQL_OPERATORS["eq"], v))
                continue
        json_filters[k] = v

    return {
        "SQL_FILTERS": sql_filters,
        "JSON_FILTERS": json_filters
    }


def _parse_row(row: dict) -> dict:
    """
    Convert a result row to dict, by merging _json with the rest of the columns

    Args:
        row: dict

    Returns
        dict
    """
    row = row.copy()
    _json = lib.json_loads(row.pop("_json")) if "_json" in row else {}
    return {
        **row,  # ensure columns exists
        **_json
    }


def _ascdesc(v, as_str=True):
    if as_str:
        if isinstance(v, int):
            return "DESC" if v == -1 else "ASC"
    else:
        if isinstance(v, str):
            return -1 if v.upper() == "DESC" else 1
    return v


def _parse_sort_dict(sorts: dict, as_str=True):
    return [(k, _ascdesc(v, as_str)) for k, v in sorts.items()]

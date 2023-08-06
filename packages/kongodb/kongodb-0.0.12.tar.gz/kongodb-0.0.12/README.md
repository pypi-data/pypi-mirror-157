# Kongodb

**Kongodb** is Hybrid Row-and-Document Oriented datastore leveraging SQL/RDBMS database: SQLite, MySQL, MariaDB, Postgresql 

Kongodb is both RDMBS + Document Oriented together.

It supports, regular SQL query along with Document Oriented and Key Value store.

Engine:
- SQLite
- Mariadb
- PostgreSQL
- MySQL



### Install

```python 
pip install kongodb
```

### Usage


```python
from kongodb import kongodb

# Open the db
db = kongodb("./my.db") 

# Select a collection 
# Collection will be created automatically
collection = db.collection("test")

# Get total items
print(len(collection))

# Add an item. It returns kongodb#Item
item = collection.add({
  "name": "Kongo",
  "type": "DB",
  "version": "1.0.0"
})

# Retrieve item by _id
_id = "9c5e5fbd05544700995c5fa3ca3ef214"
item = collection.get(_id)

# Access properties

item.get("name") # -> fun 
item.get("type") # -> DB
all_item_data = dict(item)

# Update a field
item.set("version", "1.0.1")

# or advance atomic update
item.update({
  "version": "1.0.1",
  "download:$inc": True,
  "ips:$xadd": "0.0.0.0"
})
#
item.get("version") # -> 1.0.1
item.get("download") # -> 1 or last value + 1
item.get("ips") # -> ["0.0.0.0"]

# Delete item
item.delete()

# Search
for item in collection.find():
  print(item.get("name"))


```

## ~ API ~

## Database

### kongodb

### #collection

To select a collection in the database

```python

from kongodb import kongodb 

db = kongodb()

users = fun.collection("users")

# all users

all_users = users.find_all()

```


### #Collection

List all the collections in the database 

```python

from kongodb import kongodb 

db = kongodb()

users = fun.collection("users")


```



## ColumnTypes For Index:

| Type | Column | SQlite | MariaDB | PostgreSQL|
| :--- | :---: | :---: | :---: | ---: |
| Integer | IntegerType | INT | INTEGER | INT |
| String | StringType | VARCHAR(n) | VARCHAR(n) | VARCHAR(n)|
| Bool | BoolType | INT(1) | TINYINT(1) | BOOLEAN |
| Datetime | DatetimeType | TIMESTAMP   | DATETIME | TIMESTAMP |
| Numeric | NumericType | FLOAT | DOUBLE PRECISION | DOUBLE PRECISION |

*n = the max number for the char

## ColumnType 

```
  types.[columtype](
      name:str,  # str: name of the field
      length:int, # int: length of the type if available 
      index:bool, # bool: to index the field
      unique:bool, # bool: to index and make field unique  
      default:Any # Any: any data to set as default
  )
ie: 



```

Example

```
types.StringType(
  name="myFieldName",
  length=125,
  index=True,
  unique=True,
  default="Hello"
)
```

Add Columns 

```
from kongodb import kongodb, types

COLUMNS = [
  types.IntegerType('count', index=True, default=0),
  types.BoolType('is_active', default=True),
  types.Datetime('created_at', default="NOW()"),
  types.String('full_name'),
  types.NumericType('amount', default=0.00)
]

db = kongodb("sqlite://")

collection = db.collection('test', columns=COLUMNS)

```
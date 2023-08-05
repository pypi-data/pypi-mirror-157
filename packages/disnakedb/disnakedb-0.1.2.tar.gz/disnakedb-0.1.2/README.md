# disnakedb

## Installation

```
pip3 install disnakedb
```

## Usage
```python
import disnakedb

db = disnakedb.Init()

print(db.get("foo"))  # None

db.set("foo", "bar")
print(db.get("foo"))  # bar

db.set("any", {"id": 1234, "top": 1, "str": "any string"})
print(db.get("any"))  # {"id": 1234, "top": 1, "str": "any string"}
print(db.get("any")["id"])  # 1234

db.remove("foo")
db.remove("any")
print(db.get("foo"))  # None

```
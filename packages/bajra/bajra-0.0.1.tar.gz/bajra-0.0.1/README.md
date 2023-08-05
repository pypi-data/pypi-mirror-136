# Bajra [![Bajra](https://img.shields.io/pypi/v/Bajra.svg?style=flat-square)](https://pypi.org/project/bajra/)

![bajra](https://i.ibb.co/r2DmPqb/bajra.png)

Bajra is a simple ORM API *(for MySQL and PostGreSQL)* that provide helpers to manage raw SQL in Python applications.

# What Bajra can do?

Bajra allows you to write raw SQL and forget about cursors, and it's related data structures like tuples or dicts. 
Also allows you to write your query by pieces, making the whole thing more readable.

Let's see a few examples!

## Fetching results made simple

```python
from bajra import Bajra
from bajra.engines.postgres import PostgreSQLEngine

cater = Bajra(PostgreSQLEngine(dsn="YOUR-DATABASE-DSN"))
rows = cater.fetchall("SELECT name, surname FROM test")  # That command returns a RowResult you can iterate
for row in rows:
    print(row.name)  # You can access to the data with dot notation.
    print(row['name'])  # Also as a dict-like object.
```

## Querying with arguments. No more pain.

```python
from bajra import Bajra
from bajra.engines.postgres import PostgreSQLEngine

cater = Bajra(PostgreSQLEngine(dsn="YOUR-DATABASE-DSN"))
row = cater.fetchone("SELECT name, surname FROM test WHERE name = %s", ("John", ))
print(row.name)  # John
print(row.surname)  # Costa

row = cater.fetchone("SELECT name, surname FROM test WHERE name = %(name)s", {'name': 'John'})
print(row.name)  # John
print(row.surname)  # Costa

row = cater.fetchone("SELECT name, surname FROM test WHERE name = %(name)s", name='John')
print(row.name)  # John
print(row.surname)  # Costa
```

## Querying piece by piece
```python
from bajra import Bajra
from bajra.engines.postgres import PostgreSQLEngine

cater = Bajra(PostgreSQLEngine(dsn="YOUR-DATABASE-DSN"))
query = cater.query("SELECT * FROM test")
query.append("WHERE name = %(name)s", name="John")
row = cater.fetchone(query)
row.name  # John
row.surname  # Costa
```

## Execute all the things.
```python
from bajra import Bajra
from bajra.engines.postgres import PostgreSQLEngine

cater = Bajra(PostgreSQLEngine(dsn="YOUR-DATABASE-DSN"))
query = cater.query("INSERT INTO test (name, surname) VALUES")
query.append("(%(name)s, %(surname)s)", name="Thomas", surname="Jefferson")

result = cater.execute(query)
print(result.lastrowid)  # Last Row ID of the last query. (If the engine supports it.)
print(result.rowcount)  # How many rows retrieve the last query. (If the engine supports it.)
print(result.rownumber)  # Number of rows affected by the last query. (If engine supports it.)
```

## Transactions
```python
from bajra import Bajra
from bajra.engines.postgres import PostgreSQLEngine

cater = Bajra(PostgreSQLEngine(dsn="YOUR-DATABASE-DSN"))
cater.begin()
query = cater.query("INSERT INTO test (name, surname) VALUES")
query.append("(%(name)s, %(surname)s)", name="Marie-Cole", surname="Ross")

result = cater.execute(query)
print(result.lastrowid)  # Last Row ID of the last query. (If the engine supports it.)
print(result.rowcount)  # How many rows retrieve the last query. (If the engine supports it.)
print(result.rownumber)  # Number of rows affected by the last query. (If engine supports it.)

cater.commit()
```

## Transactions within a context manager
```python
from bajra import Bajra
from bajra.engines.postgres import PostgreSQLEngine


def callback_on_exception(_cater, exc_type, exc_value, traceback):
    print(exc_type)  # <class 'psycopg2.ProgrammingError'>


cater = Bajra(PostgreSQLEngine(dsn="YOUR-DATABASE-DSN"))

with cater.transaction(rollback_on_exc=True, callback_exc=callback_on_exception):
    cater.execute("INSERT INTO test (name, surname) VALUES %s, %s", ("Augustus", "Zuma"))

row = cater.fetchone("SELECT * FROM test WHERE name=%s AND surname=%s", ("Augustus", "Zuma"))
print(row)  # None, Bajra has perfomed a rollback due to a exception.
```

# Collaborators Welcome!

If you have an idea you want to contribute in Bajra, clone the repo and raise a pull request with your feature!

![Made with love in India](https://madewithlove.now.sh/in?heart=true&template=flat-square)

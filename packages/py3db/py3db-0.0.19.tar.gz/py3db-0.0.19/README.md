# database操作(支持 mysql mongodb elasticSearch sqlite3)
## How to use
### mysql

#### connect

```python
mysql = MySql("localhost", "root", "123456", "test")
```

#### insert

```python
# insert into test values(1,'Mike','male')
mysql.insert_one("test", columns_list=[1, "Mike", "male"])

# insert into test(id,name,gender) values(1,'Mike','male')
mysql.insert_one("test", columns_dict={"id": 1, "name": "Mike", "gender": "male"})
```

#### update

```python
 #  update test set id=12 where id>12
 mysql.update('test', {'id': 12}, {"id": {
        "compare": ">",
        "value": 12
    }})

#  update test  set id=12 where name='mike'
 mysql.update('test', {'id': 12}, {"name": "mike"})   
```

#### select

```python
#  select * from test;
mysql.select("test")

#  select name,score,age from test;
mysql.select("test",["name","score","age"])

#  select name,score,age from test where name='XiaoMing';
 mysql.select("test",["name","score","age"],{'name':'XiaoMing'})
```

#### delete

````python
#  delete from test;
mysql.delete("test")

#  delete from test where name='LiBai'
mysql.delete("test",{"name":"LiBai"})
````



### mongodb

### elasticSearch
### sqlite3

#### connect

```python
sqlite = Sqlite("localhost", "root", "123456", "test")
```

#### insert

```python
# insert into test values(1,'Mike','male')
sqlite.insert_one("test", columns_list=[1, "Mike", "male"])

# insert into test(id,name,gender) values(1,'Mike','male')
sqlite.insert_one("test", columns_dict={"id": 1, "name": "Mike", "gender": "male"})
```

#### update

```python
 #  update test set id=12 where id>12
 sqlite.update('test', {'id': 12}, {"id": {
        "compare": ">",
        "value": 12
    }})

#  update test  set id=12 where name='mike'
 sqlite.update('test', {'id': 12}, {"name": "mike"})   
```

#### select

```python
#  select * from test;
sqlite.select("test")

#  select name,score,age from test;
sqlite.select("test",["name","score","age"])

#  select name,score,age from test where name='XiaoMing';
 sqlite.select("test",["name","score","age"],{'name':'XiaoMing'})
```

#### delete

````python
#  delete from test;
sqlite.delete("test")

#  delete from test where name='LiBai'
sqlite.delete("test",{"name":"LiBai"})
````


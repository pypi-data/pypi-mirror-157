DTOO: Data To Object in Python
==============================
>  Intro

Json Serializer and Deserializer

> Install
```
pip install dtoo==0.0.4
```

> Example
```
from dtoo import forModel, forJson
from typing import List

####################################
## 1. Input data example
####################################

data = {"A": 10,
        "B": 20,
        "C": 30,
        "D": [
                {"Value": 10},
                {"Value": 20}
             ],
        "E": {
                "age": 20,
                "name": "jdragon"
            }
        }


####################################
## 2. Class model using for data parsing
####################################
## must be decorated by dataclass_wrapper

@forModel.dataclass_wrapper
class Person:
    age: int = None
    name: str = None

@forModel.dataclass_wrapper
class V:
    Value: int = None

@forModel.dataclass_wrapper
class Response:
    A: int = None
    B: int = None
    C: int = None
    D: List[V] = None
    E: Person = None

####################################
## 3. Deserialize and Serialize object!
####################################

deserializeObj = forJson.Deserialization(data, Response)
serializeObj = forJson.Serialization(deserializeObj)

print(serializeObj)
```
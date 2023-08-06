from typing import get_type_hints
import inspect
import json

def IsHaveProperty(target, properties: dict):
    # properties : Dictionary
    flag = False
    for key in properties:
        if key == target: flag = True
    return flag

def GetProperties(target_object):
    properties = {}
    attributes = inspect.getmembers(target_object, lambda a: not (inspect.isroutine(a)))
    result = [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
    for item in result:
        properties[item[0]] = item[1]

    return properties

def Deserialization(inputData, RootType):
    if type(RootType) is type:
        RootType = RootType.Create()

    for key in inputData:
        if type(inputData[key]) is list:
            newObject = []
            rootProperties = GetProperties(RootType)

            for item in inputData[key]:
                if IsHaveProperty(key, rootProperties):
                    newRoot = get_type_hints(RootType)[key].__args__[0].Create()
                    Deserialization(item, newRoot)
                    newObject.append(newRoot)

                else:
                    # DO NOT ACCEPT UNEXPECTED PROPERTY!
                    # rootClass[key] = inputData[key]
                    # rootClass[key].update(key, inputData[key])
                    pass

            RootType.__dict__[key] = newObject

        elif type(inputData[key]) is not dict:
            RootType.__dict__[key] = inputData[key]

        else:
            RootType.__dict__[key] = get_type_hints(RootType)[key].Create()
            Deserialization(inputData[key], RootType.__dict__[key])

    return RootType

def Serialization(inputData, depth = 0):

    if type(inputData) is list:
        # 1. list
        list_obj = []
        depth += 1

        for item in inputData:
            list_obj.append(Serialization(item, depth))

        return list_obj

    elif type(inputData).__name__ == "myobject":
        depth += 1
        properties = GetProperties(inputData)
        dict_obj = {}

        for key in properties:
            dict_obj[key] = Serialization(properties[key], depth)

        return dict_obj

    else:
        return inputData

def loadJson(path: str, encoding="UTF-8"):
    with open(path, encoding=encoding) as json_file:
        json_data = json.load(json_file)

    return json_data
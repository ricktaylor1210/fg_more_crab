# -*- coding: utf-8 -*-

RegisterEntityBaseQuery = {
    # queryName:queryValue

    "all": {

    }
}


def GetAllRegisterDict():
    all_query_data = {}

    # 遍历字典
    for key, value in RegisterEntityBaseQuery.iteritems():
        for inner_key, inner_value in value.iteritems():
            if inner_key not in all_query_data:
                all_query_data[inner_key] = inner_value

    return all_query_data


def GetEntityNeedRegisterDict(entity_type_str):
    all_query_data = {}

    for key, value in RegisterEntityBaseQuery.get("all", {}).iteritems():
        if key not in all_query_data:
            all_query_data[key] = value
    for key, value in RegisterEntityBaseQuery.get(entity_type_str, {}).iteritems():
        if key not in all_query_data:
            all_query_data[key] = value

    return all_query_data

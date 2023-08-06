import json

segment_dict_list = []
def get_struct_elements(json_schema, col_names=[]):
    #Converting string into json for dynamodb
    #res = json.loads(json_schema)
    #print(res)
    res = json_schema


    #Listing the columns in a dataframe
    if len(col_names) == 0:
        #Listing the columns in a dataframe
        list_of_columns = list(res.keys())
        col_names = list_of_columns

    #print(col_names)
    #Transforming the raw json
    result = {}

    for key, val in res.items():
        name = key
        result[name] = [key]
        if type(val) == dict:
            for key, val in val.items():
                result[name].append(key)
                if type(val) == dict:
                    for key, val in val.items():
                        result[name].append(key)
                        if type(val) == dict:
                            for key, val in val.items():
                                result[name].append(key)
                                if (type(val)) == dict:
                                    for key, val in val.items():
                                        result[name].append(key)
                                        if type(val) == dict:
                                            for key, val in val.items():
                                                result[name].append(key)
                                                if type(val) == list:
                                                    val = val[0]
                                                    for key, val in val.items():
                                                        result[name].append(key)
                                                        if type(val) == dict:
                                                            for key, val in val.items():
                                                                result[name].append(key)
                                                                if type(val) == dict:
                                                                    for key, val in val.items():
                                                                        result[name].append(key)


    #print(result)

    #Preparing the struct type of dictionary
    temp_dict = {}
    for col_name in col_names:
        col_list = col_name.split('.')
        if len(col_list) > 1:
            parent_col = col_list[0]
            child_col = col_list[1]
        else:
            parent_col = col_list[0]
            child_col = None

        for key, val in result.items():
            temp = []
            index = 0
            if child_col is None and parent_col in result.keys():
                val = result[parent_col]
                for col in val:
                    if index == 0:
                        temp.append(val[index])
                        index = index + 1
                        if val[index] == 'L':
                            temp.append(val[index])
                            temp.append(0)
                            index = index + 1
                            temp.append(val[index])
                            temp_dict[parent_col] = temp
                        else:
                            temp.append(val[index])
                            temp_dict[parent_col] = temp
                        break
            elif child_col is None and parent_col in val:
                temp.append(val[index])
                index = index + 1
                temp.append(val[index])

                col_index = val.index(parent_col)
                temp.append(val[col_index])
                col_index = col_index + 1
                temp.append(val[col_index])
                temp_dict[parent_col] = temp
                break
            elif parent_col in val:
                for col in val:
                    if index == 0:
                        temp.append(val[index])
                        index = index + 1
                        temp.append(val[index])
                    elif parent_col == col:
                        temp.append(val[index])
                        index = index + 1
                        temp.append(val[index])
                    elif child_col == col:
                        temp.append(val[index])
                        index = index + 1
                        if val[index] == 'L':
                            temp.append(val[index])
                            temp.append(0)
                            index = index + 1
                            temp.append(val[index])
                            temp_dict[child_col] = temp
                        else:
                            temp.append(val[index])
                            temp_dict[child_col] = temp
                        break
                    else:
                        index = index + 1
            else:
                continue
    #print(temp_dict)


    child_fields = {}
    #Getting all the elements of that particular column
    for key, val in temp_dict.items():
        final_element = res
        for col in val:
            final_element = final_element[col]
        child_fields[key] = final_element

    #print(child_fields)



    #Cleaning up child columns/fields
    col_dict = {}
    for key, val in child_fields.items():
        field_list = []
        if type(val) == dict:
            for sub_key, sub_val in val.items():
                field_list.append(sub_key + '.' + list(sub_val.keys())[0])
            col_dict[key] = field_list
        else:
            col_dict[key] = ''



    #Getting String columns
    parent_col = 'Item'
    #Getting all the columns names
    string_columns = {}
    for key, val in temp_dict.items():
        final_list = [i for i in val if i!=0]
        main_str = parent_col + '.' + '.'.join(final_list)
        string_columns[key] = main_str


    #print(string_columns)
    #print('\n\n')


    #print(col_dict)
    final_dataframe_columns = {}

    for key, val in col_dict.items():
        if type(val) == list:
            for field in val:
                cols = field.split('.')
                if cols[1] == 'L' or cols[1] == 'M':
                    tt_dict = get_struct_elements(json_schema, [string_columns[key].split('.')[-2] + '.' + cols[0]])[0]
                    segment_dict_list.append(tt_dict)
                elif cols[0] == 'code' or cols[0] == 'description':
                    final_dataframe_columns[key+'_'+field.split('.')[0]] = string_columns[key] + '.' + field
                else:
                    final_dataframe_columns[field.split('.')[0]] = string_columns[key] + '.' + field
        else:
            final_dataframe_columns[key] = string_columns[key]

    filtered_final_df_columns = {}
    for key, val in final_dataframe_columns.items():
        if val.split('.')[-1] == 'L' or val.split('.')[-1] == 'M':
            continue
        else:
            filtered_final_df_columns[key] = val

    return (filtered_final_df_columns, segment_dict_list)

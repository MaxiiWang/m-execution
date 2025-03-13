from bson import ObjectId


def rec_convert_obj_id_to_str(data):
    """
    Recursively convert the ObjectId type to str
    :param data: data to convert
    :return: converted data
    """
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = rec_convert_obj_id_to_str(value)
    if isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = rec_convert_obj_id_to_str(item)
    return data

def get_enum_from_value(enum_class, value):
    """
    Get enum member from value
    :param 
    enum_class: enum class
    value: value
    :return: enum member
    """
    for member in enum_class.__members__.values():
        if member.value == value:
            return member
    raise ValueError(f"No enum member with value {value}")



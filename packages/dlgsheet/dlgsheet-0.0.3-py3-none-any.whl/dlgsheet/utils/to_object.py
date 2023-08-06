

def list_to_object(list_values, header):

    return dict(zip(header, list_values))

def nested_list_to_object(nested_list, header=None):

    if header is None:
        header = nested_list[0]
        nested_list = nested_list[1:]

    return [list_to_object(list_values, header) for list_values in nested_list]

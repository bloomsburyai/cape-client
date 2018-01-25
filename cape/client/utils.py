def check_list(list_to_check, description):
    if list_to_check is not None:
        if not isinstance(list_to_check, list):
            raise TypeError('Expecting %s to be of type list, instead got %s' % (description, type(list_to_check)))
        return list_to_check
    else:
        return []

import os

def read_config_entry(config=None, section=None, option=None, data_type=None, default_value=None, options=None):
    if config.has_option(section, option):
        if data_type == 'float':
            value = config.getfloat(section, option)
        if data_type == 'int':
            value = config.getint(section, option)
        if data_type == 'str':
            value = config.get(section, option)
        if data_type == 'folder_path':
            value = config.get(section, option)
            if not os.path.isdir(value):
                raise ValueError('VALUE ERROR: SimBA is looking for the folder {} but it does not exist.'.format(value))
        if options != None:
            if value not in options:
                raise ValueError('VALUE ERROR: {} is set to {} in SimBA, but this is not among the valid options ({})'.format(option, str(value), options))
            else:
                return value
        return value
    elif default_value != None:
        return default_value
    else:
        raise ValueError('VALUE ERROR: SimBA could not find an entry for option {} under section {} in the project_config.ini. Please specify the settings in the machine modells settings menu.'.format(section, option))
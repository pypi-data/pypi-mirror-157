import trafaret as t
import os
import pandas as pd


def check_int(name, value):
    try:
        t.Int().check(value)
    except t.DataError as e:
        print('{} {} {}'.format(name, str(value), e.as_dict()))
        raise ValueError('VALUE ERROR: {} should be an integer in SimBA, but is set to {}'.format(name, str(value)))

def check_str(name, value, options=()):
    try:
        t.String(allow_blank=False).check(value)
    except t.DataError as e:
        print('{} {} {}'.format(name, str(value), e.as_dict()))
        raise ValueError('VALUE ERROR: {} should be an string in SimBA, but is set to {}'.format(name, str(value)))
    if len(options) > 0:
        if value not in options:
            raise ValueError('VALUE ERROR: {} is set to {} in SimBA, but this is not a valid option {}'.format(name, str(value), options))
        else:
            pass
    else:
        pass

def check_float(name, value):
    try:
        t.Float().check(value)
    except t.DataError as e:
        print('{} {} {}'.format(name, str(value), e.as_dict()))
        raise ValueError('VALUE ERROR: {} should be a float in SimBA, but is set to {}'.format(name, str(value)))

def read_config_entry(config=None, section=None, option=None, data_type=None, default_value=None, options=None):
    try:
        if config.has_option(section, option):
            if data_type == 'float':
                value = config.getfloat(section, option)
            elif data_type == 'int':
                value = config.getint(section, option)
            elif data_type == 'str':
                value = config.get(section, option)
            elif data_type == 'folder_path':
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
            raise ValueError('VALUE ERROR: SimBA could not find an entry for option {} under section {} in the project_config.ini. Please specify the settings in the machine models settings menu.'.format(section, option))
    except ValueError:
        raise ValueError('VALUE ERROR: SimBA could not find an entry for option {} under section {} in the project_config.ini. Please specify the settings in the machine models settings menu.'.format(
                section, option))


def read_simba_meta_files(folder_path=None):
    meta_file_lst = []
    for i in os.listdir(folder_path):
        if i.__contains__("meta"):
            meta_file_lst.append(os.path.join(folder_path, i))
    if len(meta_file_lst) == 0:
        print('SIMBA WARNING: The training meta-files folder does not have any meta files inside it (no files in this folder has the "meta" substring in the filename')
    return meta_file_lst

def read_meta_file(meta_file_path):
    return pd.read_csv(meta_file_path, index_col=False).to_dict(orient='records')[0]

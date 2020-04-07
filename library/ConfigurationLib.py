import os.path
import yaml


def create_configuration_file(file_name, default_conf):
    if not os.path.isfile(file_name):  # Si no existe el archivo de conf
        stream = open(file_name, 'w')  # Crea el archivo
        yaml.dump(default_conf, stream)  # Write a YAML representation of data to file.


def read_configuration_file(file_name):
    if not os.path.isfile(file_name):
        return False  # Si no existe el archivo de conf
    else:
        with open(file_name, 'r', encoding="utf-8") as stream:
            data_loaded = yaml.full_load(stream)
        return data_loaded


def save_configuration_file(file_name, conf):
    stream = open(file_name, 'w')  # Crea el archivo
    yaml.dump(conf, stream)  # Write a YAML representation of data to file.

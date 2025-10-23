import configparser
from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd

from commons.utils.DateAndTimeUtils import parse_iso_datetime, parse_iso_date

class PythonParametrization(ABC):
    '''
        Generalization of a parametrization
    '''

    list_of_required_sections = []
    required_params_by_section = {}

    def __init__(self, config_ini_file: str = None,
                       config_parser : configparser = None,
                       config_df : pd.DataFrame = None
                        ):
        config_ini_file_valid =  (not config_ini_file is None)
        config_parser_valid = (not config_parser is None)
        config_df_valid = (not config_df is None)
        if config_ini_file_valid ^ config_parser_valid ^ config_df_valid :
            pass
        else:
            raise Exception('Can only pass either the file, the parser or a panda df!')

        self.add_required_sections_and_parameters_in_lists()
        if not config_ini_file is None:
            self.config_parser = configparser.ConfigParser(
                converters={
                    'datetime': parse_iso_datetime,
                    'date' : parse_iso_date
                }
            )
            self.parameters_parsed = False
            self.from_configuration_ini_file(config_ini_file)
        elif not config_parser is None:
            self.config_parser = config_parser
            self.parse_parameters(config_parser)
            self.parameters_parsed = True
        elif not config_df is None:
            self.parse_parameters_df(config_df)
            self.parameters_parsed = True
        else:
            raise Exception('Either config file OR configparser must be passed')


    def print_model_of_config(self):
        for section in self.list_of_required_sections:
            print('[' + section + ']')
            for param in self.required_params_by_section[section]:
                print(param + ' =')


    def add_required_section_parameter(self,
                                       section : str,
                                       param : str):
        if section not in self.list_of_required_sections:
            # New section
            self.list_of_required_sections.append(section)
            list_params = [param]
            self.required_params_by_section[section] = list_params
        else:
            # Already seen section
            self.required_params_by_section[section].append(param)


    def from_configuration_ini_file(self, configfile: str):
        if not configfile is None:
            with open(configfile) as f:
                self.config_parser.read(configfile)
            self.parse_parameters(self.config_parser)
            self.parameters_parsed = True

    
    def parse_parameters_df(self, dfp : pd.DataFrame):
        raise Exception('Not supported')
    
    
    @abstractmethod
    def parse_parameters(self, configparser : configparser):
        raise Exception('Override me parsing your data')


    @abstractmethod
    def add_required_sections_and_parameters_in_lists(self):
        raise Exception('Override me adding the specific sections and params')

    
    def get_config_parser(self):
        return self.config_parser

# ---------------------------------------------------------------
#
# ---------------------------------------------------------------
def find_keys_in_configparser(config_parser : configparser,
                              key_list : List[str]) -> Dict[str,List[str]]:
    '''
     This function takes a configparser object (config) and a list of keys (key_list).
     It then iterates over the sections of the configparser and checks if each key is present in each section.
     The function returns a dictionar where keys are the searched keys, and values are lists of sections where
     each key was found.
     
     Note:  if a key is not found in any section of the configparser, it won't be present in the output dictionary.
     
    '''
    key_info = {}

    for section in config_parser.sections():
        for key in key_list:
            if config_parser.has_option(section, key):
                if key in key_info:
                    key_info[key].append(section)
                else:
                    key_info[key] = [section]

    return key_info



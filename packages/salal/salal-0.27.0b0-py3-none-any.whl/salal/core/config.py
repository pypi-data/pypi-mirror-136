import sys
import os.path
import json
import argparse
from salal.core.logging import logging
from salal.core.utilities import utilities

# After initialization, the following attributes are available on
# the <config> object:
# - action: the action to be executed
# - profile: the build profile to use while executing it
# - system: a dict of system configuration variables
# - project: a dict of project configuration variables

class Config:

    #---------------------------------------------------------------------------

    @classmethod
    def initialize (cls):
        cls.config_data = dict()
        cls.parameters = dict()
        cls.globals = dict()
        cls.parse_arguments()
        cls.do_system_configuration()
        cls.do_user_configuration()
        cls.do_project_and_theme_configuration()
        cls.do_profile_configuration()
        cls.set_extension_directories()
        
    #---------------------------------------------------------------------------
 
    @classmethod
    def parse_arguments (cls):
        cls.parameters['paths'] = {}
        cls.parameters['paths']['salal_root'] = os.path.normpath(os.path.dirname(sys.modules['__main__'].__file__))
        parser = argparse.ArgumentParser()
        parser.add_argument('action', action = 'store')
        parser.add_argument('profile', action = 'store', nargs = '?', default = 'default')
        parser.add_argument('--config-file', action = 'store', default = os.path.join(cls.parameters['paths']['salal_root'], 'config', 'system_config.json'))
        parser.add_argument('--logging-level', action = 'store', default = 'INFO')
        cls._arguments = parser.parse_args()
        # we shouldn't do any logging until this point has been reached,
        # otherwise it won't be impacted by the logging level
        logging.set_logging_level(cls._arguments.logging_level)
        cls.parameters['action'] = cls._arguments.action
        logging.message('DEBUG', 'Using salal root directory of ' + cls.parameters['paths']['salal_root'])
        logging.message('DEBUG', 'Parsed command line arguments')

    #---------------------------------------------------------------------------

    @classmethod
    def load_configuration (cls, config_type, config_file):
        logging.message('DEBUG', 'Loading ' + config_type + ' configuration from ' + config_file)
        with open(config_file) as config_fh:
            cls.config_data[config_type] = json.load(config_fh)
        
    #---------------------------------------------------------------------------
    
    @classmethod
    def apply_configuration (cls, config_type):
        logging.message('DEBUG', 'Applying ' + config_type + ' configuration')
        if 'parameters' in cls.config_data[config_type]:
            utilities.deep_update(cls.parameters, cls.config_data[config_type]['parameters'])
        if 'globals' in cls.config_data[config_type]:
            utilities.deep_update(cls.globals, cls.config_data[config_type]['globals'])

    #---------------------------------------------------------------------------

    @classmethod
    def do_system_configuration (cls):
        # load and apply the system configuration
        if not os.path.isfile(cls._arguments.config_file):
            logging.message('ERROR', 'Fatal error: System config file missing')
        cls.load_configuration('system', cls._arguments.config_file)
        cls.apply_configuration('system')

    #---------------------------------------------------------------------------

    @classmethod
    def do_user_configuration (cls):
        # load and apply the user configuration, if present
        user_config_file = os.path.expanduser(cls.parameters['paths']['user_config_file'])
        if os.path.isfile(user_config_file):
            cls.load_configuration('user', user_config_file)
            
            cls.apply_configuration('user')

    #---------------------------------------------------------------------------

    @classmethod
    def do_project_and_theme_configuration (cls):
        # load the project configuration
        project_config_file = os.path.join(cls.parameters['paths']['config_root'], cls.parameters['paths']['project_config_file'])
        if os.path.isfile(project_config_file):
            cls.load_configuration('project', project_config_file)
            # check if there is a theme; if so, load and apply any theme
            # configuration
            if 'parameters' in cls.config_data['project'] and 'paths' in cls.config_data['project']['parameters'] and 'theme_root' in cls.config_data['project']['parameters']['paths']:
                theme_root = cls.config_data['project']['parameters']['paths']['theme_root']
                logging.message('INFO', 'Using theme ' + theme_root)
                theme_config_file = os.path.join(theme_root, cls.parameters['paths']['config_root'], cls.parameters['paths']['theme_config_file'])
                if os.path.isfile(theme_config_file):
                    cls.load_configuration('theme', theme_config_file)
                    cls.apply_configuration('theme')
            # apply the project configuration
            cls.apply_configuration('project')

    #---------------------------------------------------------------------------

    @classmethod
    def do_profile_configuration (cls):
        # set profile-related parameters
        cls.parameters['profile'] = cls._arguments.profile
        cls.parameters['paths']['profile_build_dir'] = os.path.join(cls.parameters['paths']['build_root'], cls.parameters['profile'])
        # for a non-default profile, load and apply the config file
        if cls.parameters['profile'] != 'default':
            profile_config_file = os.path.join(cls.parameters['paths']['config_root'], cls.parameters['paths']['profiles_dir'], cls.parameters['profile'] + '.json')
            if os.path.isfile(profile_config_file):
                cls.load_configuration('profile', profile_config_file)
                cls.apply_configuration('profile')
            else:
                logging.message('ERROR', 'Specified profile ' + cls._arguments.profile + ' does not exist')
        # log the profile name
        logging.message('INFO', 'Using profile ' + cls.parameters['profile'])
        
    #---------------------------------------------------------------------------

    @classmethod
    def set_extension_directories (cls):
        # Extensions can be located in three places: The base Salal
        # directory, the theme directory, or the <design> directory
        # for the project. In each case, any extensions need to be
        # placed in an <extensions> directory in that location. Here
        # we check for the existence of these <extensions> directories,
        # and set the system path <extension_dirs> to a list of those that
        # are found.
        extension_locations = [
            cls.parameters['paths']['salal_root'],
            cls.parameters['paths']['theme_root'] if 'theme_root' in config.parameters['paths'] else None,
            'design'
        ]
        config.parameters['paths']['extension_dirs'] = []
        for location in extension_locations:
            if location:
                extension_dir = os.path.join(location, cls.parameters['paths']['extensions_root'])
                if os.path.isdir(extension_dir):
                    config.parameters['paths']['extension_dirs'].append(extension_dir)
                    logging.message('DEBUG', 'Registered extensions directory ' + extension_dir)
        
    #---------------------------------------------------------------------------
    
config = Config

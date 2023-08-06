import os
import importlib
from salal.core.logging import logging
from salal.core.config import config
from salal.core.handlers import handlers
from salal.core.utilities import utilities

class Actions:

    #---------------------------------------------------------------------------

    @classmethod
    def initialize (cls):
        if 'action_commands' not in config.parameters:
            logging.message('ERROR', 'No actions are configured')
        logging.message('DEBUG', 'Loading command handlers')
        cls.handlers = handlers.load_handlers(config.parameters['paths']['command_handlers_dir'])

    #---------------------------------------------------------------------------

    @classmethod
    def execute_internal_command (cls, command):
        if command in cls.handlers:
            cls.handlers[command].execute(command)
        else:
            logging.message('ERROR', 'Command ' + command + ' is not configured.')
        
    #---------------------------------------------------------------------------

    @classmethod
    def execute (cls, action):
        # Make sure this action is defined
        if action not in config.parameters['action_commands']:
            logging.message('ERROR', 'The action ' + action + ' is not configured')
        else:
            logging.message('INFO', 'Executing ' + action + ' action')
            
        # Iterates through the list of commands associated with 'tag',
        # does substitution for system variables, and passes them to
        # the OS for execution
        for command_spec in config.parameters['action_commands'][action]:
            if command_spec['type'] == 'internal':
                cls.execute_internal_command(command_spec['command'])
            elif command_spec['type'] == 'external':
                command_string = utilities.substitute_variables(command_spec['command'], config.parameters)
                logging.message('INFO', command_string)
                os.system(command_string)
            else:
                logging.message('ERROR', 'Unrecognized command type ' + command_spec['type'])
 
    #---------------------------------------------------------------------------
    
actions = Actions

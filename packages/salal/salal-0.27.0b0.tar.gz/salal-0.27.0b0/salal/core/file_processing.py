import os
import re
import math
from salal.core.logging import logging
from salal.core.config import config
from salal.core.handlers import handlers
from salal.core.dependencies import dependencies

class FileProcessing:

    #---------------------------------------------------------------------------

    @classmethod
    def initialize (cls):
        logging.message('DEBUG', 'Loading file processing handlers')
        cls.handlers = handlers.load_handlers(config.parameters['paths']['file_processing_handlers_dir'])
        if len(cls.handlers) == 0:
            logging.message('ERROR', 'No file processing handlers are installed, exiting')
        
        if not 'file_handlers' in config.parameters or len(config.parameters['file_handlers']) == 0:
            logging.message('ERROR', 'No file processing handlers are configured in the configuration files, exiting')

        for handler in config.parameters['file_handlers']:
            if not handler in cls.handlers:
                logging.message('ERROR', 'There is a configuration for a file processing handler ' + handler + ', but no such handler is installed')
            if not 'include' in config.parameters['file_handlers'][handler]:
                logging.message('ERROR', 'Configuration for file processing handler ' + handler + ' must have an include pattern')
            if not 'priority' in config.parameters['file_handlers'][handler]:
                logging.message('ERROR', 'Configuration for file processing handler ' + handler + ' must have a priority')
        
    #---------------------------------------------------------------------------

    @classmethod
    def is_matching_handler (cls, file_path, handler):
        # check against include patterns
        matches = False
        for pattern in config.parameters['file_handlers'][handler]['include']:
            if re.search(pattern, file_path) != None:
                matches = True
                break
        # check against exclude patterns, if any
        if matches and 'exclude' in config.parameters['file_handlers'][handler]:
            for pattern in config.parameters['file_handlers'][handler]['exclude']:
                if re.search(pattern, file_path) != None:
                    matches = False
                    break
        return matches
    
    #---------------------------------------------------------------------------
    
    @classmethod
    def process (cls, source_file_path, target_file_path):
        if not dependencies.needs_build(target_file_path, source_file_path):
            logging.message('TRACE', target_file_path + ' is up to date, skipping')
            return
        
        # find the best matching handler
        best_handler = None
        best_priority = math.inf
        for key in config.parameters['file_handlers']:
            if cls.is_matching_handler(source_file_path, key) and config.parameters['file_handlers'][key]['priority'] < best_priority:
                best_handler = key
                best_priority = config.parameters['file_handlers'][key]['priority']
        if best_handler:
            logging.message('TRACE', 'Processing ' + source_file_path + ' using ' + best_handler + ' handler')
        else:
            logging.message('ERROR', 'Unable to find a matching handler for ' + source_file_path + ', exiting')
            
        # create the target directory if it doesn't exist
        os.makedirs(os.path.dirname(target_file_path), exist_ok = True)
        logging.message('INFO', target_file_path)
        dependencies.start_build_tracking(target_file_path, source_file_path)
        cls.handlers[best_handler].process(source_file_path, target_file_path)
        dependencies.stop_build_tracking()

    #---------------------------------------------------------------------------

file_processing = FileProcessing

import os
import re
from salal.core.logging import logging
from salal.core.config import config
from salal.core.utilities import utilities 
from salal.core.dependencies import dependencies
from salal.core.file_processing import file_processing

class Build:
    
    #---------------------------------------------------------------------------

    @classmethod
    def get_tag (cls):
        return 'build'
    
    #---------------------------------------------------------------------------

    @classmethod
    def configure_search_dirs (cls, dir_type):
        search_dirs = []
        # check for the appropriate type of directory within the project
        project_search_dir = os.path.join(config.parameters['paths']['design_root'], config.parameters['paths'][dir_type + '_dir'])
        if os.path.isdir(project_search_dir):
            search_dirs.insert(0, project_search_dir)
        # check for the appropriate type of directory within the theme
        # directory, if a theme is defined
        if 'theme_root' in config.parameters['paths']:
            theme_search_dir = os.path.join(config.parameters['paths']['theme_root'], config.parameters['paths']['design_root'], config.parameters['paths'][dir_type + '_dir'])
            if os.path.isdir(theme_search_dir):
                search_dirs.insert(0, theme_search_dir)
        return search_dirs
                
    #---------------------------------------------------------------------------

    @classmethod
    def select_files_to_process (cls, file_path_list, location):
        logging.message('DEBUG', 'Determining which ' + location + ' files pass include and exclude checks') 
        files_selected = []
        for file_path in file_path_list:
            passed_check = True
            if 'build' in config.parameters and 'locations' in config.parameters['build'] and location in config.parameters['build']['locations']:
                if 'include' in config.parameters['build']['locations'][location]:
                    passed_check = False
                    for pattern in config.parameters['build']['locations'][location]['include']:
                        if re.search(pattern, file_path) != None:
                            passed_check = True
                            break
                if passed_check and 'exclude' in config.parameters['build']['locations'][location]:
                    for pattern in config.parameters['build']['locations'][location]['exclude']:
                        if re.search(pattern, file_path) != None:
                            passed_check = False
                            break
            if passed_check:
                logging.message('TRACE', 'Passed: ' + file_path)
                files_selected.append(file_path)
            else:
                logging.message('TRACE', 'Failed: ' + file_path)
        return files_selected
    
    #---------------------------------------------------------------------------
    
    @classmethod
    def process_files (cls, source_relative_path_list, source_dir, target_dir, location):
        logging.message('DEBUG', 'Determining which files need to be rebuilt')
        if 'build' in config.parameters and 'locations' in config.parameters['build'] and location in config.parameters['build']['locations'] and 'mappings' in config.parameters['build']['locations'][location]:
            path_mappings = config.parameters['build']['locations'][location]['mappings']
        else:
            path_mappings = []
        for source_relative_path in source_relative_path_list:
            source_file_path = os.path.join(source_dir, source_relative_path)

            # By default, we use the location and name of the source
            # file within the source directory as the location and
            # name of the target file within the target
            # directory. However, alternative mappings can be
            # specified via system variables. Each mapping is a
            # three-element array: A 'selection' pattern which is used
            # to determine whether the mapping applies to this file, a
            # 'find' pattern which determines what text will be modified,
            # and a 'replacement' pattern which determines what it will
            # be replaced with.
            target_relative_path = source_relative_path
            for mapping in path_mappings:
                if re.search(mapping[0], source_relative_path):
                    target_relative_path = re.sub(mapping[1], mapping[2], source_relative_path)
                    break
            target_file_path = os.path.join(target_dir, target_relative_path)   

            file_processing.process(source_file_path, target_file_path)

    #---------------------------------------------------------------------------
    
    @classmethod
    def process_content (cls):
        content_dir = config.parameters['paths']['content_root']
        logging.message('DEBUG', 'Processing content files from ' + content_dir)
        content_files = utilities.find_files(config.parameters['paths']['content_root'])
        files_to_process = cls.select_files_to_process(content_files, 'content')
        cls.process_files(files_to_process, content_dir, config.parameters['paths']['profile_build_dir'], 'content')

    #---------------------------------------------------------------------------
    @classmethod
    def process_resources (cls):
        # Copy all the files in the resources directory to the build
        # directory, processing them according to the appropriate
        # file processing handler.
        #
        # We write files to the same relative path in the build
        # directory as they had in the resources directory. So, for
        # profile <test>, /resources/js/app.js will become
        # /build/test/js/app.js.
        #
        # Theme files get processed first, so they can be overridden
        # by local files. This is accomplished simply by overwriting
        # the theme version of the file.
        resource_dirs = cls.configure_search_dirs('resource')
        for resource_dir in resource_dirs:
            logging.message('DEBUG', 'Processing resources from ' + resource_dir)
            resource_files = utilities.find_files(resource_dir)
            files_to_process = cls.select_files_to_process(resource_files, 'resources')
            cls.process_files(files_to_process, resource_dir, config.parameters['paths']['profile_build_dir'], 'resources')

    #---------------------------------------------------------------------------

    @classmethod
    def process_modules (cls):
        # Copy module files to the build directory, processing them
        # according to the appropriate file processing handler.
        #
        # The destination directory is determined based on the file
        # type and module name. So, a file within the modules
        # directory called 'foo/foo.css' will end up as
        # 'css/foo/foo.css' in the build directory.
        #
        # Theme files get processed first, so they can be overridden
        # by local files. This is accomplished simply by overwriting
        # the theme version of the file.
        module_dirs = cls.configure_search_dirs('module')
        for module_dir in module_dirs:
            logging.message('DEBUG', 'Processing modules from ' + module_dir)
            module_files = utilities.find_files(module_dir)
            files_to_process = cls.select_files_to_process(module_files, 'modules')
            cls.process_files(files_to_process, module_dir, config.parameters['paths']['profile_build_dir'], 'modules')
        
    #---------------------------------------------------------------------------

    @classmethod
    def execute (cls, tag):

        file_processing.initialize()
        dependencies.initialize()
        cls.process_content()
        cls.process_resources()
        cls.process_modules()
        logging.message('INFO', str(dependencies.num_files_checked()) + ' file(s) processed, ' + str(dependencies.num_files_built()) + ' file(s) built')
        dependencies.write_log()

    #---------------------------------------------------------------------------

handler = Build

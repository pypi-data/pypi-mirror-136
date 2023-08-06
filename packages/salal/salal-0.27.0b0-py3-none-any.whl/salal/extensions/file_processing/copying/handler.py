# This handler just copies the file from the source directory to the target
# directory.
import os.path
import shutil
from salal.core.logging import logging

class Default:

    #---------------------------------------------------------------------------

    @classmethod
    def get_tag (cls):
        return 'copying'
    
    #---------------------------------------------------------------------------

    @classmethod
    def process (cls, source_file_path, target_file_path):
        logging.message('TRACE', 'Copying')
        shutil.copyfile(source_file_path, target_file_path)
    
    #---------------------------------------------------------------------------

handler = Default

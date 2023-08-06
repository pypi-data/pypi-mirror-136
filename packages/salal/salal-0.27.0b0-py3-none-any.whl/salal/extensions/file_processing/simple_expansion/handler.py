# This handler copies the file from the source to the target directory,
# substituting any references to project variables with their current values.
#
# For advanced users: Technically, the files get the full Jinja
# treatment, so you can put anything in the file that you can put in a
# Jinja template. But the only variables that will be available are
# project variables.
import os.path
import jinja2
from salal.core.logging import logging
from salal.core.config import config
from salal.core.dependencies import dependencies
from salal.core.variable_tracker import VariableTracker

class SimpleExpansion:

    #---------------------------------------------------------------------------

    @classmethod
    def get_tag (cls):
        return 'simple_expansion'

    #---------------------------------------------------------------------------

    @classmethod
    def process (cls, source_file_path, target_file_path):
        logging.message('TRACE', 'Doing simple expansion')
        source_dir, source_file = os.path.split(source_file_path)
        env = jinja2.Environment(loader = jinja2.FileSystemLoader(source_dir))
        # In Jinja, template paths aren't file system paths and always use
        # forward slashes regardless of the OS
        template = env.get_template(source_file)
        output = template.render({'globals': VariableTracker(config.globals, success_callback = dependencies.variable_used, failure_callback = dependencies.variable_not_found)})
        with open(target_file_path, mode = 'w', encoding = 'utf-8', newline = '\n') as output_fh:
            output_fh.write(output)

    #---------------------------------------------------------------------------

handler = SimpleExpansion

# This recursively expands the templates specified in the XML source file,
# and writes the result to an HTML file. During the expansion, templates
# have access to both the project variables and the attributes and content
# provided with the corresponding tag.
import os.path
import re
import jinja2
import xml.etree.ElementTree as ET
from salal.core.logging import logging
from salal.core.config import config
from salal.core.dependencies import dependencies
from salal.core.variable_tracker import VariableTracker
from . import custom_jinja_functions

class XMLHandler:

    #---------------------------------------------------------------------------

    @classmethod
    def get_tag (cls):
        return 'xml'

    #---------------------------------------------------------------------------
    
    @classmethod
    def configure_modules (cls, node, env):
        module_dirs = [os.path.join(config.parameters['paths']['design_root'], config.parameters['paths']['module_dir'])]
        if 'theme_root' in config.parameters['paths']:
            module_dirs.append(os.path.join(config.parameters['paths']['theme_root'], config.parameters['paths']['design_root'], config.parameters['paths']['module_dir']))
        for module in node.attrib['modules'].split():
            # try to locate the module directory
            module_location = None
            for module_dir in module_dirs:
                module_subdir = os.path.join(module_dir, module)
                if os.path.isdir(module_subdir):
                    logging.message('TRACE', 'Found module ' + module + ' in ' + module_dir)
                    module_location = module_dir
                    env.loader.searchpath.append(module_subdir)
                    break
            else:
                logging.message('ERROR', 'Cannot find module ' + module)

            # if it exists, add module style sheet to the styles list
            for extension, attribute in [('css', 'styles'), ('js', 'scripts')]:
                file_path =  os.path.join(module, module + '.' + extension)
                if os.path.exists(os.path.join(module_location, file_path)):
                    logging.message('TRACE', 'Configuring ' + attribute + ' for module ' + module)
                    if attribute not in node.attrib:
                        node.attrib[attribute] = ''
                    else:
                        node.attrib[attribute] += ' '
                    node.attrib[attribute] += os.path.join(os.sep, extension, file_path)

    #---------------------------------------------------------------------------

    @classmethod
    def render_node (cls, node, env, global_variables, parent_variables):
        # Store the attributes on the node (later passed to the render
        # function as 'this')
        this_variables = dict()
        if node.attrib:
            this_variables.update(node.attrib)
            
        # A tage name beginning with _ indicates a preprocessor directive, i.e.,
        # something needs to be done with the node before further processing
        if node.tag.startswith('_'):
            if node.tag == '_include':
                if 'file' in node.attrib:
                    include_tree = ET.parse(node.attrib['file'])
                    include_root = include_tree.getroot()
                    for child in include_root:
                        node.append(child)
                else:
                    raise ValueError('_include directive requires a file attribute')
            else:
                raise ValueError('Unrecognized preprocessor directive ' + node.tag)
        
        # If the node has text content, expand variables in that
        # content, and use the result as the node's text. Otherwise,
        # set the text content to the empty string.
        if node.text:
            content_template = env.from_string(node.text)
            node.text = content_template.render({'globals': global_variables, 'parent': parent_variables})
        else:
            node.text = ''
            
        # If the node has children, call this method recursively on
        # each child. Concatenate the results from those calls, and
        # append them to the node's text.
        if len(node) > 0:
            for child in node:
                node.text += cls.render_node(child, env, global_variables, this_variables)
                if child.tail:
                    content_template = env.from_string(child.tail)
                    node.text += content_template.render({'globals': global_variables, 'parent': this_variables})

        # Initialize the variables that will be passed to Jinja for rendering
        # the node. We start with whatever variables were passed in, and
        # add a 'this' variable that points to a dict of variables specific
        # to this node. Those include any attributes on the node, as well as
        # a special variable 'this.content' that contains the node text that
        # was set above.
        this_variables['content'] = node.text
        render_variables = {'globals': global_variables, 'parent': parent_variables, 'this': this_variables}
            
        # Load the template for this node
        if node.tag.startswith('_'):
            template = env.from_string('{{this.content}}')
        else:
            template = env.get_template(node.tag + '.html')
            dependencies.template_used(template.filename)

        # Render the node and return the result
        return template.render(render_variables)
    
    #---------------------------------------------------------------------------

    @classmethod
    def process (cls, source_file_path, target_file_path):

        logging.message('TRACE', 'Doing XML expansion')
        # Get the XML source file to be expanded
        xml_root = ET.parse(source_file_path).getroot()
        # We auto-generate a page ID, which is just the name of the directory
        # holding the index.xml file
        file_stem = os.path.relpath(source_file_path, config.parameters['paths']['content_root'])
        page_depth = file_stem.count('/')
        if page_depth == 0:
            page_id = 'home'
        elif page_depth == 1:
            page_id = re.sub(r'/index\.xml\Z', '', file_stem)
        else:
            page_id = re.sub(r'\A.+/([^/]+)/index\.xml\Z', r'\1', file_stem)
        xml_root.attrib['id'] = page_id
        # Configure the directories to be searched for templates. We
        # add the theme template dir after the local one, so a local
        # template will be found first if there is one
        template_dirs = [os.path.join(config.parameters['paths']['design_root'], config.parameters['paths']['template_dir'])] 
        if 'theme_root' in config.parameters['paths']:
            template_dirs.append(os.path.join(config.parameters['paths']['theme_root'], config.parameters['paths']['design_root'], config.parameters['paths']['template_dir']))
        # Initialize Jinja
        #env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dirs), trim_blocks = True, lstrip_blocks = True)
        env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dirs))
        # If there is a modules attribute on the root, configure modules
        if 'modules' in xml_root.attrib:
            logging.message('TRACE', 'Configuring modules for ' + file_stem)
            cls.configure_modules(xml_root, env)
        # Register Salal-specific Jinja functions
        custom_jinja_functions.register_functions(env)
        # Do template expansion on the source file
        xml_root.text = cls.render_node(xml_root, env, VariableTracker(config.globals, success_callback = dependencies.variable_used, failure_callback = dependencies.variable_not_found), None)
        # Write the expanded file to the target directory
        with open(target_file_path, mode = 'w', encoding = 'utf-8', newline = '\n') as output_fh:
            output_fh.write(xml_root.text)

    #---------------------------------------------------------------------------

handler = XMLHandler

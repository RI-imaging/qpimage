"""Include single scripts with doc string, code, and image

Use case
--------
There is an "examples" directory in the root of a repository,
e.g. 'include_doc_code_img_path = "../examples"' in conf.py 
(default). An example is a file ("an_example.py") that consists
of a doc string at the beginning of the file, the example code,
and, optionally, an image file (png, jpg) ("an_example.png").


Configuration
-------------
In conf.py, set the parameter

   include_doc_code_img_path = "../examples"

to wherever the included files reside.


Usage
-----
The directive 

   .. include_doc_code_img:: an_example.py

will display the doc string formatted with the first line as a
heading, a code block with line numbers, and the image file.
"""

import os.path as op

from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles
from docutils import nodes


class IncludeDirective(Directive):
    required_arguments = 1
    optional_arguments = 0

    def run(self):
        path = self.state.document.settings.env.config.include_doc_code_img_path
        full_path = op.join(path, self.arguments[0])
        
        with open(full_path, "r") as myfile:
            text = myfile.read()
        
        source = text.split('"""')
        doc = source[1].split("\n")
        doc.insert(1, "~"*len(doc[0])) # make title heading
        
        code = source[2].strip()
        
        # documentation
        rst = ViewList()
        for ii, line in enumerate(doc):
            rst.append(line, "fakefile.rst", ii)
        
        # image
        for ext in [".png", ".jpg"]:
            image_path = full_path[:-3] + ext
            if op.exists(image_path):
                break
        else:
            image_path = ""
        if image_path:
            rst.append(".. figure:: {}".format(image_path), "fakefile.rst", ii+1)
            #rst.append("   :height: 30%", "fakefile.rst", ii+2)
        
        # Create a node.
        node = nodes.section()
        node.document = self.state.document
        # Parse the rst.
        nested_parse_with_titles(self.state, rst, node)
        #self.add_name(node)

        lcode = nodes.literal_block(code, code)
        lcode['linenos'] = True
        self.add_name(lcode)

        return node.children + [lcode]

def setup(app):
    app.add_config_value('include_doc_code_img_path', "../examples", 'html')

    app.add_directive('include_doc_code_img', IncludeDirective)

    return {'version': '0.1'}   # identifies the version of our extension

"""qpimage definition extraction

Usage
-----
Directives:

Table output of qpimage.meta.DATA_DEF

   .. qpimage_meta_table:: data

Table output of qpimage.meta.OTHER_DEF

   .. qpimage_meta_table:: other
"""
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles
from docutils import nodes

from qpimage import meta


class Base(Directive):
    required_arguments = 0
    optional_arguments = 0

    def generate_rst(self):
        pass

    def run(self):
        rst = self.generate_rst()

        vl = ViewList(rst, "fakefile.rst")
        # Create a node.
        node = nodes.section()
        node.document = self.state.document
        # Parse the rst.
        nested_parse_with_titles(self.state, vl, node)
        return node.children


class MetaTable(Base):
    required_arguments = 1

    def generate_rst(self):
        which = self.arguments[0]
        if which == "data":
            ddict = meta.DATA_DEF
        elif which == "other":
            ddict = meta.OTHER_DEF
        else:
            raise ValueError("Expected argument 'data' or 'other', "
                             + "not '{}'.".format(which))
        rst = []

        keys = sorted(ddict.keys())

        rst.append(".. csv-table::")
        rst.append("    :header: key, description")
        rst.append("    :delim: tab")
        rst.append("")

        for kk in keys:
            rst.append("    {}\t {}".format(kk, ddict[kk]))

        rst.append("")

        return rst


def setup(app):
    app.add_directive('qpimage_meta_table', MetaTable)
    return {'version': '0.1'}   # identifies the version of our extension

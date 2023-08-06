import os

from pymdocx.common.comment import parse_p_comment

from pymdocx.common.utils import get_doc, print_xml_node
from pymdocx.doc.table import merge_table_comment_revision, merge_table_comment_revision_v2
from pymdocx.doc.paragraph import merge_paragraph_comment_revision

DIR_PATH = './../data/test_table'


def test_merge_table_comment_revision():
    doc_o_path = os.path.join(DIR_PATH, 't_base.docx')
    doc_a_path = os.path.join(DIR_PATH, 't_base_1.docx')
    doc_b_path = os.path.join(DIR_PATH, 't_base_2.docx')
    doc_o = get_doc(doc_o_path)
    doc_a = get_doc(doc_a_path)
    doc_b = get_doc(doc_b_path)
    # merge_table_comment_revision(doc_o, [doc_a, doc_b])
    merge_table_comment_revision_v2(doc_o, [doc_a, doc_b])
    doc_o.save('t_base_new.docx')


def test_table_xml():
    doc_a_path = os.path.join(DIR_PATH, 'a.docx')
    doc_a = get_doc(doc_a_path)
    table = doc_a.tables[0]
    print_xml_node(table._element)
import os
import string
import xml.etree.ElementTree as ET
import re


BASE_DIRS = '/var/tmp/dbramdisk/data'
PRINTABLE = set(string.printable)


def make_prefixed_name(name):
    return '{urn:cdbs:data}%s' % name


def resolve_path_from_filename(filename):
    return os.path.join(BASE_DIRS, filename)


def get_printable_name_from_xml_tag(xml_tag):
    return ''.join(filter(lambda _: _ in PRINTABLE, xml_tag.attrib[make_prefixed_name('Name')]))


def follow_navigation_link_in_child(xml_tag, child_tag_name):
    return xml_tag.find(make_prefixed_name(child_tag_name)).attrib[make_prefixed_name('Href')]


def get_document_root_for_file(filename):
    try:
        return ET.parse(resolve_path_from_filename(filename)).getroot()
    except IOError:
        return None


def get_top_level_elements_in_document_for_file(filename, element_type):
    try:
        return get_document_root_for_file(filename).findall(make_prefixed_name(element_type))
    except:
        return None


def build_page_model_from_file(filename):
    root = get_document_root_for_file(filename)

    if root is None:
        return None
    elif root.tag == make_prefixed_name('Root'):
        return parse_root_file(root)
    else:
        return parse_non_root_file(root)


def parse_root_file(document_root):
    items = []
    background = document_root.attrib[make_prefixed_name('Background')]

    for root_menu_item in document_root.findall(make_prefixed_name('RootMenu')):
        linked_image = root_menu_item.find(make_prefixed_name('Image'))
        
        info = {'href': linked_image.attrib[make_prefixed_name('Href')], 'icon': resolve_path_from_filename(linked_image.text)}
        items.append(info)

    imgs = document_root.findall(make_prefixed_name('Image'))

    tops = resolve_path_from_filename(imgs[0].text)
    hint = resolve_path_from_filename(imgs[-1].text)

    return {'items':items, 'dbc_hint':hint, 'dbc_top_header':tops, 'dbc_background':background, 'type':0}


def parse_non_root_file(document_root):
    menu_elements = document_root.findall(make_prefixed_name('Menu'))

    if menu_elements:
        return parse_second_level_page_file(document_root, menu_elements)
    else:
        return parse_third_level_page_file(document_root)


def sanitize_text(text):
    return re.sub(r'\n+', '', text)


def parse_second_level_page_file(document_root, menu_elements):
    tabs = []
    background = document_root.attrib[make_prefixed_name('Background')]

    for menu in menu_elements:
        info = {'title':menu.attrib[make_prefixed_name('Name')]}

        table_item = menu.find(make_prefixed_name('Table'))

        if table_item is not None:
            info['mode'] = 'table'

            headers = table_item.find(make_prefixed_name('Title'))
            info['widths'] = [int(_.attrib['Len']) for _ in headers.findall(make_prefixed_name('Head'))]
            info['headers'] = [_.text for _ in headers.findall(make_prefixed_name('Head'))]

            values = []
            for content_item in table_item.findall(make_prefixed_name('Content')):
                values.append([_.text for _ in content_item.findall(make_prefixed_name('Text'))])

            info['values'] = values
        else:
            info['mode'] = 'list'
            items = []

            for text_item in menu.findall(make_prefixed_name('Text')):
                items.append({'title':sanitize_text(text_item.text), 'href':text_item.attrib[make_prefixed_name('Href')]})

            info['values'] = items

        tabs.append(info)

    imgs = document_root.findall(make_prefixed_name('Image'))

    tops = resolve_path_from_filename(imgs[0].text)
    hint = resolve_path_from_filename(imgs[-1].text)

    return {'items':tabs, 'dbc_hint':hint, 'dbc_top_header':tops, 'dbc_background':background, 'type':1}


def parse_third_level_page_file(document_root):
    title = sanitize_text(document_root.find(make_prefixed_name('Text')).text)
    
    try:
        text = document_root.findall(make_prefixed_name('Text'))[1].text
    except:
        text = ''

    info = {'title':title, 'type':2, 'text':text}
    info['dbc_background'] = document_root.attrib[make_prefixed_name('Background')]

    images = document_root.findall(make_prefixed_name('Image'))

    try:
        image = images[1:-1][0]
    except:
        image = ''

    info['image'] = resolve_path_from_filename(image) if image else ''

    table_item = document_root.find(make_prefixed_name('Table'))
    if table_item is not None:
        table = {}
        
        headers = table_item.find(make_prefixed_name('Title'))
        table['widths'] = [int(_.attrib['Len']) for _ in headers.findall(make_prefixed_name('Head'))]
        table['headers'] = [_.text for _ in headers.findall(make_prefixed_name('Head'))]

        values = []
        for content_item in table_item.findall(make_prefixed_name('Content')):
            values.append([_.text for _ in content_item.findall(make_prefixed_name('Text'))])

        table['values'] = values
        info['table'] = table
    
    info['dbc_top_header'] = resolve_path_from_filename(images[0].text)
    info['dbc_hint'] = resolve_path_from_filename(images[-1].text)

    return info
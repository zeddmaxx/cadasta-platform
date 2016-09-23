import xml.etree.ElementTree as ET
from rest_framework.renderers import BaseRenderer

MEDIA_TYPES = {
    'PH': 'image/*',
    'AU': 'audio/*',
    'VI': 'video/*'
}


class XFormRenderer(BaseRenderer):
    format = 'xform'

    def create_option(self, option):
        item = ET.Element('item')
        label = ET.SubElement(item, 'label')
        label.text = option.get('label')
        value = ET.SubElement(item, 'value')
        value.text = option.get('name')

        return item

    def create_input(self, id, question):
        attrs = {'ref':  '/' + id + '/' + question.get('name')}
        tag = 'input'

        if question.get('type') in ['PH', 'AU', 'VI']:
            tag = 'upload'
            attrs['mediatype'] = MEDIA_TYPES[question.get('type')]
        elif question.get('type') == 'S1':
            tag = 'select1'

        field = ET.Element(tag, attrs)
        label = ET.SubElement(field, 'label')
        label.text = question.get('label')

        if question.get('type') == 'S1':
            for option in question.get('options'):
                field.append(self.create_option(option))
        return field

    def add_questions_to_body(self, id, element, questions):
        for field in questions:
            element.append(self.create_input(id, field))

    def add_questiongroups_to_body(self, id, element, question_groups):
        for group in question_groups:
            group_id = id + '/' + group.get('name')
            group_el = ET.SubElement(element,
                                     'group',
                                     {'ref':  '/' + group_id})
            label = ET.SubElement(group_el, 'label')
            label.text = group.get('label')
            self.add_questions_to_body(group_id,
                                       group_el,
                                       group.get('questions'))

    def add_questions_to_header(self, element, questions):
        for field in questions:
            ET.SubElement(element, field.get('name'))

    def add_questiongroups_to_header(self, element, question_groups):
        for group in question_groups:
            group_el = ET.SubElement(element, group.get('name'))
            self.add_questions_to_header(group_el, group.get('questions'))

    def render(self, data, **kwargs):
        root = ET.Element(
            'h:html',
            {'xmlns': 'http://www.w3.org/2002/xforms',
             'xmlns:ev': 'http://www.w3.org/2001/xml-events',
             'xmlns:h': 'http://www.w3.org/1999/xhtml',
             'xmlns:jr': 'http://openrosa.org/javarosa',
             'xmlns:orx': 'http://openrosa.org/xforms',
             'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema'}
        )

        title = ET.Element('h:title')
        title.text = data.get('id_string')

        model = ET.Element('model')
        instance = ET.SubElement(model, 'instance')
        thing = ET.SubElement(instance,
                              data.get('id_string'),
                              attrib={'id': data.get('id_string'),
                                      'version': data.get('version')})

        self.add_questions_to_header(thing, data.get('questions'))
        self.add_questiongroups_to_header(thing,
                                          data.get('question_groups', []))
        head = ET.Element('h:head')
        head.append(title)
        head.append(model)
        root.append(head)

        body = ET.Element('h:body')
        self.add_questions_to_body(data.get('id_string'),
                                   body,
                                   data.get('questions'))
        root.append(body)

        return ET.tostring(root)

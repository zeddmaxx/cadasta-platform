import xml.etree.ElementTree as ET
from django.test import TestCase
from ..renderer.xform import XFormRenderer


class XFormRendererTest(TestCase):
    def test_create_input(self):
        field = {
            "id": "v4ip2h6hzd96x3schjhh7tfh",
            "name": "party_name",
            "label": "Party Name",
            "type": "TX"
        }
        renderer = XFormRenderer()
        element = renderer.create_input('abc123', field)
        xml = ET.tostring(element).decode()
        assert ('<input ref="/abc123/party_name">'
                '<label>Party Name</label></input>') == xml

    def test_create_upload_input(self):
        field = {
            "id": "v4ip2h6hzd96x3schjhh7tfh",
            "name": "photo",
            "label": "A photo",
            "type": "PH"
        }
        renderer = XFormRenderer()
        element = renderer.create_input('abc123', field)
        xml = ET.tostring(element).decode()
        assert ('<upload mediatype="image/*" ref="/abc123/photo">'
                '<label>A photo</label></upload>') == xml

    def test_create_select1_input(self):
        field = {
            'id': "byv297rfgrtjcipj6eqirk5e",
            'name': "location_type",
            'label': "What is the land feature?",
            'type': "S1",
            'options': [
                {
                  'id': "uqu3heeejav74mrzgdw4w6wt",
                  'name': "MI",
                  'label': "Miscellaneous"
                },
                {
                  'id': "6azt8zkw45htpf6f9g8csm2j",
                  'name': "NP",
                  'label': "National Park Boundary"
                }
            ]
        }
        renderer = XFormRenderer()
        element = renderer.create_input('abc123', field)
        xml = ET.tostring(element).decode()
        assert ('<select1 ref="/abc123/location_type"><label>What is the land '
                'feature?</label><item><label>Miscellaneous</label><value>MI'
                '</value></item><item><label>National Park Boundary</label>'
                '<value>NP</value></item></select1>') == xml

    def test_add_questions_to_body(self):
        questions = [
            {
                "id": "xp8vjr6dsk46p47u22fft7bg",
                "name": "tenure_type",
                "label": "Tenure Type",
                "type": "TX"
            },
            {
                "id": "xp8vjr6dsk46p47u22fft7bg",
                "name": "party_type",
                "label": "Party Type",
                "type": "TX"
            }
        ]

        element = ET.Element('root')
        renderer = XFormRenderer()
        renderer.add_questions_to_body('abc123', element, questions)

        xml = ET.tostring(element).decode()

        assert '<label>Tenure Type</label>' in xml
        assert '<label>Party Type</label>' in xml

    def test_add_questiongroups_to_body(self):
        question_groups = [
            {
                'id': "grswcid3t2tyrzq4gsemrhf2",
                'name': "location_attributes",
                'label': "Location Attributes",
                'questions': [{
                    "id": "xp8vjr6dsk46p47u22fft7bg",
                    "name": "tenure_type",
                    "label": "Tenure Type",
                    "type": "TX"
                }, {
                    "id": "xp8vjr6dsk46p47u22fft7bg",
                    "name": "party_type",
                    "label": "Party Type",
                    "type": "TX"
                }]
            }
        ]

        element = ET.Element('root')
        renderer = XFormRenderer()
        renderer.add_questiongroups_to_body('abc123', element, question_groups)

        xml = ET.tostring(element).decode()

        assert '<group ref="/abc123/location_attributes">' in xml
        assert '<label>Tenure Type</label>' in xml
        assert 'ref="/abc123/location_attributes/tenure_type"' in xml
        assert '<label>Party Type</label>' in xml
        assert 'ref="/abc123/location_attributes/party_type"' in xml

    def test_add_questions_to_header(self):
        questions = [
            {
                'id': "xp8vjr6dsk46p47u22fft7bg",
                'name': "tenure_type",
            },
            {
                'id': "bzs2984c3gxgwcjhvambdt3w",
                'name': "start",
            }
        ]

        element = ET.Element('root')
        renderer = XFormRenderer()
        renderer.add_questions_to_header(element, questions)

        xml = ET.tostring(element).decode()

        assert '<tenure_type />' in xml
        assert '<start />' in xml

    def test_add_questiongroups_to_header(self):
        question_groups = [
            {
                'id': "grswcid3t2tyrzq4gsemrhf2",
                'name': "location_attributes",
                'label': "Location Attributes",
                'questions': [{
                    'id': "xp8vjr6dsk46p47u22fft7bg",
                    'name': "tenure_type",
                }, {
                    'id': "bzs2984c3gxgwcjhvambdt3w",
                    'name': "start",
                }]
            }
        ]

        element = ET.Element('root')
        renderer = XFormRenderer()
        renderer.add_questiongroups_to_header(element, question_groups)

        xml = ET.tostring(element).decode()

        assert ('<location_attributes><tenure_type /><start />'
                '</location_attributes>') in xml

    def test_render(self):
        data = {
            'id_string': 'abc123',
            'version': '1234567890',
            'questions': [
                {
                  'id': "xp8vjr6dsk46p47u22fft7bg",
                  'name': "tenure_type",
                  'label': "What is the social tenure type?",
                  'type': "S1",
                  'required': False,
                  'constraint': None,
                  'options': [
                    {
                      'id': "d9pkepyjg4sgaepdytgwkgfv",
                      'name': "WR",
                      'label': "Water Rights"
                    },
                    {
                      'id': "vz9533y64f2rns6v8frssc5v",
                      'name': "UC",
                      'label': "Undivided Co-ownership"
                    },
                  ]
                },
                {
                  'id': "bzs2984c3gxgwcjhvambdt3w",
                  'name': "start",
                  'label': None,
                  'type': "ST",
                  'required': False,
                  'constraint': None
                }
            ]
        }
        renderer = XFormRenderer()
        xml = renderer.render(data).decode()
        print(xml)
        assert '<h:title>abc123</h:title>' in xml
        assert '<abc123 id="abc123" version="1234567890">' in xml

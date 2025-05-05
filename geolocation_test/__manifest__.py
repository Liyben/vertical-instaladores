# -*- coding: utf-8 -*-
{
    'name': 'Geolocation_test',
    'version': '17.0.1.0.0',
    'summary': """ Geolocation_test Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['project'],
    "data": [
        "views/project_task_views.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'geolocation_test/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

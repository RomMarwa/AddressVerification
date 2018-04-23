# -*- coding: utf-8 -*-

{
    'name': 'Address Verification',
    'version': '10.0.1.0.1',
    'depends': [
        'base',
        'website_sale',
    ],
    'author': "Marwa ROMDHAN",

    'license': "AGPL-3",
    'summary': '''It uses Geonames to verify the validity of zip code/city on the checkout process
                ''',
    'data': [
            'data/data.xml',
            'views/res_config_views.xml',
            'views/templates.xml',
             ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}

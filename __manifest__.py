{
    'name': 'Addis Industrial Core',
    'version': '1.0',
    'category': 'Manufacturing',
    'depends': ['mrp','stock','account'],
    'data':[
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
    ],
    'installable': True,
    'application': True,
}
# -*- coding: utf-8 -*-
{
    'name': "Bill with Stock Receipts",
    'summary': "To link bill with stock receipts",
    'description': """
        Bridges the gap between bills and stock receipts, making financial tracking smoother. It helps users link their receipts directly 
        to the associated bills for better transparency and ease of reconciliation
        """,
    'author': "Ayesha Siddika Suchi",
    'website': "",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base', 'purchase_stock'],
    'license': 'LGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
}

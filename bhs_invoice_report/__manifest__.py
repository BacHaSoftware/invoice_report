# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom for invoice report',
    'author': 'Bac Ha Software',
    'website': 'https://bachasoftware.com',
    'maintainer': 'Bac Ha Software',
    'version': '1.0',
    'category': 'Invoice',
    'sequence': 75,
    'summary': 'Manage your invoice report',
    'description': "Create and manage your invoice report",
    'depends': ['account', 'bhs_invoice_partner', 'bhs_customer_sequence'],
    'assets': {
        'web.assets_backend': [
            'bhs_invoice_report/static/src/scss/invoice.scss',
        ],
        'web.report_assets_pdf': [
            'bhs_invoice_report/static/src/scss/invoice.scss',
        ],
        'web.report_assets_common': [
           'bhs_invoice_report/static/src/scss/invoice.scss',
        ],
    },

    'data': ['views/report_invoice.xml','views/account_move_view.xml'],
    'demo': [],
    "external_dependencies": {},
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}

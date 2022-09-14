# -*- coding: utf-8 -*-
{
    'name': "SME WO Split",
    'summary': "SME WO Split",
    'description': """
        Work order Split option
    """,

    'author': "Silverdale",
    'website': "https://www.silverdaletech.com",
    'license': 'OPL-1',
    'version': '2208',
    'category': 'mrp',

    "depends": [
        "base", "mrp", "mrp_workorder", "hr", "sd_widgets"
    ],
    "data": [
        "security/ir.model.access.csv",
        # "views/workorder_split_view.xml",
        "views/mrp_workorder_views.xml",
        "views/workcenter_productivity.xml",
        # Silverdale remove it
        # "views/mrp.xml",
        "views/mrp_workcenter.xml",
        "wizard/wo_produced_qty_wizard.xml",
        "data/data.xml",
    ],

}

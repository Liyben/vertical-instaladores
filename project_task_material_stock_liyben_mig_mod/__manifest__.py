# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# Copyright 2018 Praxya - Juan Carlos Montoya
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project Task Material Stock",
    "summary": "Create stock and analytic moves from "
    "record products spent in a Task",
    "version": "14.0.1.0.0",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["stock_account", "stock_analytic", "project_task_material", "sale_purchase", "product_task_material_work", "stock_picking_analytic"],
    "data": ["data/data.xml", "views/project_view.xml", "views/project_task_view.xml", "views/stock_picking_view.xml","views/stock_views.xml"],
}

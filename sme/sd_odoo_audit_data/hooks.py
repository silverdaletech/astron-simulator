# coding: utf-8
from os.path import join, dirname, realpath
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    models = env['ir.model'].search([])
    master_domain = env['master.data.domain']
    master = env['audit.master.data']
    duplicate = env['duplicate.data.count']
    model_fields = env['ir.model.fields']
    for model in models:
        domains = []
        if model.model == 'product.product':
            fields = model_fields.search([('model_id', '=', model.id), ('name', 'in', ['barcode', 'default_code'])])

            domain_list = ['barcode', 'active', 'default_code', 'sale_ok', 'list_price', 'purchase_ok', 'seller_ids', 'description_sale',
                           'weight', 'volume', 'activity_user_id', 'sale_delay', 'invoice_policy', 'purchase_method', ]

            domain_line_list = ['Missing Barcode', 'Missing SKU', 'Bad Pricing', 'Purchase Products without Vendors', 'Missing Sales Description',
                                'Missing Weight or Volume', 'Missing Responsible', 'Missing Customer Lead Time', 'Invoicing based on Ordered Quantities',
                                'Billing based on Ordered Quantities', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Barcode':
                    if 'barcode' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["barcode", "=", False], ["active", "=", True]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing SKU':
                    if 'default_code' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["default_code", "=", False], ["active", "=", True]]
                        })
                        domains.append(domain_record)
                        continue
                elif rec == 'Bad Pricing':
                    if 'sale_ok' in domain_fields and 'list_price' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", "&", ["sale_ok", "=", True], ["list_price", "<=", 1], ["active", "=", True]]
                        })
                        domains.append(domain_record)

                elif rec == 'Purchase Products without Vendors':
                    if 'purchase_ok' in domain_fields and 'seller_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", "&", ["purchase_ok", "=", True], ["seller_ids", "=", False], ["active", "=", True]]
                        })
                        domains.append(domain_record)

                elif rec == 'Missing Sales Description':
                    if 'description_sale' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["description_sale", "=", False], ["active", "=", True]]
                        })
                        domains.append(domain_record)

                elif rec == 'Missing Weight or Volume':
                    if 'weight' in domain_fields and 'volume' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["active", "=", True], "|", ["weight", "=", 0], ["volume", "=", 0]]
                        })
                        domains.append(domain_record)

                elif rec == 'Missing Responsible':
                    if 'activity_user_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["activity_user_id", "=", False], ["active", "=", True]]
                        })
                        domains.append(domain_record)

                elif rec == 'Missing Customer Lead Time':
                    if 'sale_delay' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["sale_delay", "=", ""], ["active", "=", True]]
                        })
                        domains.append(domain_record)

                elif rec == 'Invoicing based on Ordered Quantities':
                    if 'invoice_policy' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["invoice_policy", "=", "order"], ["active", "=", True]]
                        })
                        domains.append(domain_record)

                elif rec == 'Billing based on Ordered Quantities':
                    if 'purchase_method' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["purchase_method", "=", "purchase"], ["active", "=", True]]
                        })
                        domains.append(domain_record)

            existing = master.search([('name', '=', model.name)], limit=1)
            existing_duplicate = duplicate.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

            if existing_duplicate:
                existing_duplicate.write({
                    'duplicate_data_line': [(6, 0, fields.ids)]
                })
            else:
                duplicate.create({
                    'name': model.id,
                    'duplicate_data_line': [(6, 0, fields.ids)]
                })

        elif model.model == 'product.category':

            domain_list = ['property_valuation', 'property_cost_method', ]
            domain_line_list = ['Bad Valuation Method', 'Bad Costing Method', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Bad Valuation Method':
                    if 'property_valuation' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["property_valuation", "=", "manual_periodic"]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Bad Costing Method':
                    if 'property_cost_method' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["property_cost_method", "=", "standard"]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'delivery.carrier':

            domain_list = ['country_ids', 'delivery_type', ]
            domain_line_list = ['Missing Destination Country', 'Fixed Price or Rule based Methods', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Destination Country':
                    if ')' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["country_ids", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Fixed Price or Rule based Methods':
                    if 'delivery_type' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", ["delivery_type", "=", "fixed"], ["delivery_type", "=", "base_on_rule"]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'res.users':
            domain_lines = env['master.data.domain'].search([('name', 'in', ['Notifications by Email', ])])

            domain_list = ['notification_type', 'groups_id', ]
            domain_line_list = ['Notifications by Email', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Notifications by Email':
                    if 'notification_type' in domain_fields and 'groups_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["notification_type", "=", "email"], ["groups_id", "ilike", "internal"]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'mrp.workcenter':

            domain_list = ['alternative_workcenter_ids', 'time_stop', 'time_start', 'costs_hour', 'code', ]
            domain_line_list = ['No Alternative Workcenter', 'Missing Cleaning or Set up Time', 'Missing Cost', 'Missing Code', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'No Alternative Workcenter':
                    if 'alternative_workcenter_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["alternative_workcenter_ids", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Cleaning or Set up Time':
                    if 'time_stop' in domain_fields and 'time_start' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["time_stop", "=", 0], ["time_start", "=", 0]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Cost':
                    if 'costs_hour' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["costs_hour", "=", 0]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Code':
                    if 'code' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["code", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'crm.team':

            domain_list = ['alias_id', 'member_ids', 'user_id', 'invoiced_target', ]
            domain_line_list = ['Missing Alias', 'Missing Leader', 'Missing Target', 'Missing Members', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Alias':
                    if 'alias_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["alias_id.alias_name", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Leader':
                    if 'user_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["user_id", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Target':
                    if 'invoiced_target' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["invoiced_target", "=", 0]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Members':
                    if 'member_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["member_ids", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'helpdesk.team':

            domain_list = ['use_sla', 'use_credit_notes', 'use_product_returns', 'alias_id', 'use_helpdesk_timesheet', ]
            domain_line_list = ['No SLA Policies', 'Does not take Refund or Return Requests',
                                'Alias is not set', 'Timesheets not activated', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'No SLA Policies':
                    if 'use_sla' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["use_sla", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Does not take Refund or Return Requests':
                    if 'use_credit_notes' in domain_fields and 'use_product_returns' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["use_credit_notes", "!=", True], ["use_product_returns", "!=", True]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Alias is not set':
                    if 'alias_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["alias_id.alias_name", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Timesheets not activated':
                    if 'use_helpdesk_timesheet' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["use_helpdesk_timesheet", "!=", True]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'planning.role':

            domain_list = ['employee_ids', ]
            domain_line_list = ['Roles without Employees', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Roles without Employees':
                    if 'employee_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["employee_ids", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'res.bank':

            domain_list = ['bic', 'city', 'country', 'email', 'phone']
            domain_line_list = ['Without details', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Without details':
                    if 'bic' in domain_fields and 'city' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", "|", "|", "|", ["bic", "=", False], ["city", "=", False], ["country", "=", False], ["email", "=", False], ["phone", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'res.partner.bank':

            domain_list = ['bank_id', 'acc_holder_name', ]
            domain_line_list = ['Accounts without Banks', 'Accounts without Holder Name', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Accounts without Banks':
                    if 'bank_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["bank_id", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Accounts without Holder Name':
                    if 'acc_holder_name' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["acc_holder_name", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'documents.folder':

            domain_list = ['group_ids', 'read_group_ids', ]
            domain_line_list = ['Without Rights Configured', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Without Rights Configured':
                    if 'read_group_ids' in domain_fields and 'group_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", ["read_group_ids", "=", False], ["group_ids", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'mrp.bom':

            domain_list = ['code', 'operation_ids', ]
            domain_line_list = ['Missing Reference', 'Missing Operations', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Reference':
                    if 'code' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["code", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Operations':
                    if 'operation_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["operation_ids", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'stock.location':

            domain_list = ['barcode', 'valuation_in_account_id', 'usage']
            domain_line_list = ['Barcode is not set', 'Missing Accounting Configuration for Scrap, Adjustment or Production Locations', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Barcode is not set':
                    if 'barcode' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["barcode", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Accounting Configuration for Scrap, Adjustment or Production Locations':
                    if 'valuation_in_account_id' in domain_fields and 'usage' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["valuation_in_account_id", "=", False], "|", ["usage", "=", "production"], ["usage", "=", "inventory"]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'account.bank.statement':

            domain_list = ['state']
            domain_line_list = ['Statements in Processing', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Statements in Processing':
                    if 'state' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", ["state", "=", "open"], ["state", "=", "posted"]]
                        })
                        domains.append(domain_record)
                        continue
            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'account.tax':

            domain_list = ['invoice_repartition_line_ids', 'refund_repartition_line_ids']
            domain_line_list = ['Taxes without Accounts', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Taxes without Accounts':
                    if 'invoice_repartition_line_ids' in domain_fields and 'invoice_repartition_line_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", ["invoice_repartition_line_ids.account_id", "=", False], ["refund_repartition_line_ids.account_id", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'payment.acquirer':

            domain_list = ['state', 'module_state']
            domain_line_list = ['Payments Acquirers Installed but Disabled', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Payments Acquirers Installed but Disabled':
                    if 'module_state' in domain_fields and 'state' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", ["module_state", "=", "installed"], ["state", "=", "disabled"]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'stock.warehouse.orderpoint':

            domain_list = ['trigger', ]
            domain_line_list = ['Auto Rules', 'Manual Rules', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Auto Rules':
                    if 'trigger' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["trigger", "=", "auto"]]
                        })
                        domains.append(domain_record)
                        continue
                elif rec == 'Manual Rules':
                    domain_record = master_domain.create({
                        'name': rec,
                        'domain': [["trigger", "=", "manual"]]
                    })
                    domains.append(domain_record)
                    continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'product.attribute':
            domain_lines = env['master.data.domain'].search([('name', 'in', ['Attributes without values', 'Variant Creating Attributes', ])])

            domain_list = ['value_ids', 'create_variant']
            domain_line_list = ['Attributes without values', 'Variant Creating Attributes', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Attributes without values':
                    if 'value_ids' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["value_ids", "=", False]]
                        })
                        domains.append(domain_record)
                        continue
                elif rec == 'Variant Creating Attributes':
                    if 'create_variant' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", ["create_variant", "=", "always"], ["create_variant", "=", "dynamic"]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'product.packaging':

            domain_list = ['max_weight', 'height', 'width', 'packaging_length', 'barcode', 'shipper_package_code', 'package_carrier_type']
            domain_line_list = ['Without Dimensions or Max Weight', 'Without Barcodes', 'Without Code', 'Without Carrier', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Without Dimensions or Max Weight':
                    if 'height' in domain_fields and 'width' in domain_fields and 'packaging_length' in domain_fields and 'max_weight' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&", "&", "&", ["height", "=", 0], ["width", "=", 0], ["packaging_length", "=", 0], ["max_weight", "=", 0]]
                        })
                        domains.append(domain_record)
                        continue
                elif rec == 'Without Barcodes':
                    if 'barcode' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["barcode", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Without Code':
                    if 'shipper_package_code' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["shipper_package_code", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Without Carrier':
                    if 'package_carrier_type' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["package_carrier_type", "=", "none"]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'hr.employee':

            domain_list = ['work_email', 'work_phone', 'department_id', 'address_home_id', 'private_email', 'phone', 'timesheet_manager_id', 'expense_manager_id', 'parent_id', 'timesheet_cost']
            domain_line_list = ['Without Phone', 'Without Email', 'Without Department',
                                'Missing Private Details', 'Missing Managers or Approvers', 'Missing Timesheet Cost', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Without Phone':
                    if 'work_phone' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["work_phone", "=", False]]
                        })
                        domains.append(domain_record)
                        continue
                elif rec == 'Without Email':
                    if 'work_email' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["work_email", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Without Department':
                    if 'department_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["department_id", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Private Details':
                    if 'address_home_id' in domain_fields and 'private_email' in domain_fields and 'phone' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", "|", ["address_home_id", "=", False], ["private_email", "=", False], ["phone", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Managers or Approvers':
                    if 'parent_id' in domain_fields and 'expense_manager_id' in domain_fields and 'timesheet_manager_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", "|", ["parent_id", "=", False], ["expense_manager_id", "=", False], ["timesheet_manager_id", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Timesheet Cost':
                    if 'timesheet_cost' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["timesheet_cost", "=", 0]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'hr.department':

            domain_list = ['manager_id']
            domain_line_list = ['Missing Manager', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Manager':
                    if 'manager_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["manager_id", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'hr.job':

            domain_list = ['department_id', 'description']
            domain_line_list = ['Missing Department', 'Missing Job Description', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Department':
                    if 'department_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["department_id", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Job Description':
                    if 'description' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["description", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })

        elif model.model == 'res.partner':
            fields = model_fields.search([('model_id', '=', model.id), ('name', 'in', ['email', 'name'])])

            domain_list = ['email', 'phone', 'type', 'function', 'parent_id', 'customer_rank', 'user_id', 'property_payment_term_id', 'property_supplier_payment_term_id',
                           'supplier_rank', 'bank_ids', 'website', 'vat']
            domain_line_list = ['Missing Email Address', 'Missing Phone', 'Missing Address (one or more pieces)',
                                'Contact Persons without Job Positions', 'Companies without Contacts', 'Customer without Salesperson',
                                'Customers without Payment Terms', 'Vendors without Payment Terms', 'Vendors without Bank Details',
                                'Companies without websites', 'Companies without Tax IDs', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Email Address':
                    if 'email' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["email","=",False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Phone':
                    if 'phone' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["phone","=",False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing Address (one or more pieces)':
                    domain_record = master_domain.create({
                        'name': rec,
                        'domain': ["|","|","|","|",["street","=",False],["city","=",False],["country_id","=",False],["zip","=",False],["state_id","=",False]]
                    })
                    domains.append(domain_record)
                    continue

                elif rec == 'Contact Persons without Job Positions':
                    if 'type' in domain_fields and 'function' in domain_fields and 'parent_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&","&",["type","=","contact"],["function","=",False],["parent_id","!=",False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Companies without Contacts':
                    domain_record = master_domain.create({
                        'name': rec,
                        'domain': ["&",["is_company","=",True],["child_ids","=",False]]
                    })
                    domains.append(domain_record)
                    continue

                elif rec == 'Customer without Salesperson':
                    if 'customer_rank' in domain_fields and 'user_id' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&",["customer_rank","=",1],["user_id","=",False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Customers without Payment Terms':
                    if 'property_payment_term_id' in domain_fields and 'customer_rank' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&",["property_payment_term_id","=",False],["customer_rank","=",1]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Vendors without Payment Terms':
                    if 'property_supplier_payment_term_id' in domain_fields and 'supplier_rank' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&",["property_supplier_payment_term_id","=",False],["supplier_rank","=",1]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Vendors without Bank Details':
                    if 'bank_ids' in domain_fields and 'supplier_rank' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&",["bank_ids","=",False],["supplier_rank","=",1]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Companies without websites':
                    if 'website' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&",["is_company","=",True],["website","=",False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Companies without Tax IDs':
                    if 'vat' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["&",["vat","=",False],["is_company","=",True]]
                        })
                        domains.append(domain_record)
                        continue

            existing = master.search([('name', '=', model.name)], limit=1)
            existing_duplicate = duplicate.search([('name', '=', model.name)], limit=1)
            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            if not existing_duplicate:
                duplicate.create({
                    'name': model.id,
                    'duplicate_data_line': [(6, 0, fields.ids)]
                })

        elif model.model == 'res.company':
            fields = model_fields.search([('model_id', '=', model.id), ('name', '=', 'email')])
            existing = master.search([('name', '=', model.name)], limit=1)
            existing_duplicate = duplicate.search([('name', '=', model.name)], limit=1)

            domain_list = ['social_facebook', 'social_twitter', 'social_instagram', 'social_youtube', 'vat', 'phone', 'email', 'website', ]
            domain_line_list = ['Missing Phone, Website or Email', 'Missing VAT Numbers', 'Social Media Links Missing', ]
            domain_fields = model.field_id.filtered(lambda x: x.name in domain_list).mapped('name')
            for rec in domain_line_list:
                existing_domain = master_domain.search([('name', '=', rec)])
                if rec == 'Missing Phone, Website or Email':
                    if 'phone' in domain_fields and 'email' in domain_fields and 'website' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", "|", ["phone", "=", False], ["email", "=", False], ["website", "=", False]]
                        })
                        domains.append(domain_record)
                        continue

                elif rec == 'Missing VAT Numbers':
                    if 'vat' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': [["vat", "=", False]]
                        })
                        domains.append(domain_record)
                        continue
                elif rec == 'Social Media Links Missing':
                    if 'social_facebook' in domain_fields and 'social_twitter' in domain_fields and 'social_instagram' in domain_fields and 'social_youtube' in domain_fields:
                        domain_record = master_domain.create({
                            'name': rec,
                            'domain': ["|", "|", "|", ["social_facebook", "=", False], ["social_twitter", "=", False], ["social_instagram", "=", False], ["social_youtube", "=", False]]
                        })
                        domains.append(domain_record)

            if existing:
                existing.write({
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            else:
                master.create({
                    'name': model.id,
                    'domain_line': [(6, 0, [x.id for x in domains])]
                })
            if not existing_duplicate:
                duplicate.create({
                    'name': model.id,
                    'duplicate_data_line': [(6, 0, fields.ids)]
                })

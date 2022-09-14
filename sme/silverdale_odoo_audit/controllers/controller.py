# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal

import os

class OdooAuthController(CustomerPortal):
    """
        This controller saves pylint data
    """
    def convert_report_to_json(self, path):
        """
            Convert pylint report into json
            return {
                'Key':[[...],[.....]],
                'Key2':[[...],[.....]],
                }
        """
        dic = {}
        key = ''
        values = []
        can_as = False
        with open(path, 'r') as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if line[0] not in ['+', '-', '\n', '|', ':']:
                    if len(lines) > (index + 1):
                        if lines[index + 1][0] == '-':
                            key = line[:-1]
                            can_as = True
                    if 'Your code has been' in line:
                        values.append(line)
                        dic['Rate'] = values
                        break
                elif line[0] == '|':
                    values.append(line[1:-2:].split('|'))
                    can_as = True
                elif line[0] == '\n':
                    if can_as and values:
                        dic[key] = values
                    else:
                        values = []
                    can_as = False
        return dic


    @http.route(['/audit/report/<int:report_id>'], type='http', csrf=False, auth="public")
    def update_report_model(self, report_id, access_token=None, **kw):
        """Get file path from curl save save into model"""

        data = {'data':False}

        try:
            report_sudo = self._document_check_access('odoo.audit', report_id, access_token)
            data = {'data':True}
        except (AccessError, MissingError):
            data = json.dumps(data)
            return data

        file_loc = kw.get('data', False)
        if not os.path.isfile(file_loc):
        # if not file_loc:
            report_sudo.write({'state': 'failed'})
            return data
        json_file = self.convert_report_to_json(file_loc)

        report_sudo.write({
            'tech_data': json_file,
            'state': 'ready',
            })
        report_sudo.print_report()
        # os.remove(file_loc)
        data = json.dumps(data)
        return data

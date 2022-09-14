
from odoo import models, fields, _


class PartnerCreditLimit(models.TransientModel):
    _name = 'partner.credit.limit.warning'
    _description = 'Credit Warnings'

    message = fields.Text(readonly=True)

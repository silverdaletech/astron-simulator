# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def _check_auto_confirmation(self):
        """
        This function will hold attendee status 'un-confirm' until payment status is not paid if auto confirmation is
        enable in event and ticket is paid .
        """
        if any(not registration.event_id.auto_confirm or
               (not registration.event_id.seats_available and registration.event_id.seats_limited) for registration in
               self):
            return False
        else:
            # else condition is added to handel attendees status on payment bases
            if any(registration.payment_status == 'to_pay' and registration.event_id.is_confirm_on_payment for registration in self):
                return False
            return True


class Event(models.Model):
    _inherit = 'event.event'

    is_confirm_on_payment = fields.Boolean(
        string='Confirm on Payment',
        help='This will conform attendees after payment',
        required=False)
    is_disallow_registration = fields.Boolean(
        string='Disallow Registration?',)

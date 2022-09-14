from odoo.addons.delivery_fedex.models.fedex_request import FedexRequest

class FedexRequest(FedexRequest):

    def shipping_charges_payment_option(self, shipping_charges_payment_account, payment_type):
        self.RequestedShipment.ShippingChargesPayment = self.factory.Payment()
        self.RequestedShipment.ShippingChargesPayment.PaymentType = payment_type
        Payor = self.factory.Payor()
        Payor.ResponsibleParty = self.factory.Party()
        Payor.ResponsibleParty.AccountNumber = shipping_charges_payment_account
        self.RequestedShipment.ShippingChargesPayment.Payor = Payor

    def duties_payment_option(self, sender_party, responsible_account_number, payment_type):
        self.RequestedShipment.CustomsClearanceDetail.DutiesPayment = self.factory.Payment()
        self.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = payment_type
        if payment_type == 'SENDER':
            Payor = self.factory.Payor()
            Payor.ResponsibleParty = self.factory.Party()
            Payor.ResponsibleParty.Address = self.factory.Address()
            Payor.ResponsibleParty.Address.CountryCode = sender_party.country_id.code
            Payor.ResponsibleParty.AccountNumber = responsible_account_number
            self.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor = Payor
        elif payment_type == 'RECIPIENT':
            Payor = self.factory.Payor()
            Payor.ResponsibleParty = self.factory.Party()
            Payor.ResponsibleParty.Address = self.factory.Address()
            Payor.ResponsibleParty.Address.CountryCode = sender_party.country_id.code
            Payor.ResponsibleParty.AccountNumber = responsible_account_number
            self.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor = Payor

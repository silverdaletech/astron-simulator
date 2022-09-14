import ldap
import logging

from odoo import models, tools

_logger = logging.getLogger(__name__)

class CompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    def _connect(self, conf):
        """
        Connect to an LDAPS server specified by an ldap
        configuration dictionary.

        :param dict conf: LDAP configuration
        :return: an LDAP object
        """

        uri = 'ldaps://%s:%d' % (conf['ldap_server'], conf['ldap_server_port'])
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        connection = ldap.initialize(uri)
        connection.set_option(ldap.OPT_REFERRALS, 0)
        connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        connection.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
        connection.set_option(ldap.OPT_X_TLS_DEMAND, True)
        connection.set_option(ldap.OPT_DEBUG_LEVEL, 255)
        #if conf['ldap_tls']:
        #    connection.start_tls_s()
        return connection

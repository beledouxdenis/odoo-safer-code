import base64

from cryptography import x509
from cryptography.hazmat.primitives import serialization

from odoo import fields, models, _
from odoo.exceptions import UserError


class ResCompany(models.Model):

    _inherit = "res.company"

    l10n_xx_reports_sbr_cert = fields.Binary(
        'PKI Certificate',
        groups="base.group_system",
        help="Upload here the certificate file that will be used to connect to the Digipoort infrastructure. "
             "The private key from this file will be used, if there is one included.",
    )
    l10n_xx_reports_sbr_key = fields.Binary(
        'PKI Private Key',
        groups="base.group_system",
        help="A private key is required in order for the Digipoort services to identify you. "
             "No need to upload a key if it is already included in the certificate file.",
    )

    # vulnerability added in 16.0: https://github.com/odoo/enterprise/commit/3b426cb16af9e3abb1d2fd634e7146b9828c7c31#diff-ce6d7e690f53e4231dd9445d1db097dbd6cb1260b6c1c11a6f6a366f1641dc11R56
    # security fix: https://github.com/odoo/enterprise/commit/78ee53121573d03adbd6025e2c9979e138dbd0d2
    def _l10n_xx_get_certificate_and_key_objects(self, password=None):
        """ Return the tuple (certificate, private key), as a cryptograpy Certificate and Private Key object.
            Parameter password must be a bytes object or None
            Throws a UserError if there is a misconfiguration.
        """
        self.ensure_one()

        if not self.l10n_xx_reports_sbr_cert or not self.l10n_xx_reports_sbr_key:
            raise UserError(
                _("The certificate or the private key is missing. Please upload it in the Accounting Settings first."),
            )
        stored_certificate = base64.b64decode(self.l10n_xx_reports_sbr_cert)
        stored_key = base64.b64decode(self.l10n_xx_reports_sbr_key)

        try:
            return (x509.load_pem_x509_certificate(stored_certificate), serialization.load_pem_private_key(stored_key, password or None))
        except TypeError:
            raise UserError(_('The certificate or private key you uploaded is encrypted. Please specify your password.'))

    def _l10n_xx_get_certificate_and_key_bytes(self, password=None):
        """ Return the tuple (certificate, private key), each in the form of unencrypted PEM encoded bytes.
            Parameter password must be a bytes object or None.
            Throws a UserError if there is a misconfiguration.
        """
        self.ensure_one()

        cert_obj, pkey_obj = self._l10n_xx_get_certificate_and_key_objects(password)
        cert_bytes = cert_obj.public_bytes(serialization.Encoding.PEM)
        pkey_bytes = pkey_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return (cert_bytes, pkey_bytes)

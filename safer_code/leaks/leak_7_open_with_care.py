# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import models
from odoo.tools.misc import file_path


# https://github.com/odoo/odoo/commit/35565aa1b4995ac841ff2e6558858fe00b9d93c4
class IrQWeb(models.AbstractModel):
    _name = 'safer_code.ir.qweb'
    _description = 'Qweb'

    def get_asset_bundle(self, xmlid, files, env=None):
        return AssetsBundle(xmlid, files, env=env)


class AssetsBundle:
    def __init__(self, name, files, env=None):
        self.stylesheets = []
        for f in files:
            if f['atype'] == 'text/css':
                self.stylesheets.append(StylesheetAsset(self, url=f['url'], filename=f['filename'], inline=f['content'], media=f['media']))


class WebAsset:
    def __init__(self, bundle, inline=None, url=None, filename=None):
        self.bundle = bundle
        self.inline = inline
        self._filename = filename
        self.url = url

    def stat(self):
        if not (self.inline or self._filename or self._ir_attach):
            self._filename = file_path(self.url)
            if self._filename:
                return
            try:
                # Test url against ir.attachments
                attach = self.bundle.env['ir.attachment'].sudo().get_serve_attachment(self.url)
                self._ir_attach = attach[0]
            except Exception:  # noqa: BLE001
                raise Exception("Could not find %s" % self.name)

    def _fetch_content(self):
        """ Fetch content from file or database"""
        try:
            self.stat()
            if self._filename:
                with open(self._filename, 'rb') as fp:
                    return fp.read().decode('utf-8')
            else:
                return base64.b64decode(self._ir_attach['datas']).decode('utf-8')
        except UnicodeDecodeError:
            raise Exception('%s is not utf-8 encoded.' % self.name)
        except OSError:
            raise Exception('File %s does not exist.' % self.name)
        except Exception:  # noqa: BLE001
            raise Exception('Could not get content for %s.' % self.name)


class StylesheetAsset(WebAsset):
    def __init__(self, *args, **kw):
        self.media = kw.pop('media', None)
        super().__init__(*args, **kw)

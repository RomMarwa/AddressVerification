# -*- coding: utf-8 -*-

from odoo import api, models, fields


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    geonames_url = fields.Char(string='Goenames URL')

    def set_geonames_url(self):
        self.env['ir.config_parameter'].set_param(
            'geonames_url', (self.geonames_url or '').strip(), groups=['base.group_system'])

    def get_default_geonames_url(self, fields):
        geonames_url = self.env['ir.config_parameter'].get_param('geonames_url', default='http://download.geonames.org/export/zip/')
        return dict(geonames_url=geonames_url)


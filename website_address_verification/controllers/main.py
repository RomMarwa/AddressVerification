# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import requests
import tempfile
import StringIO
import zipfile
import os
import logging

try:
    import unicodecsv
except ImportError:
    unicodecsv = None

logger = logging.getLogger(__name__)


class WebsiteSaleAddressVerification(WebsiteSale):

    def search_zipCode_cities(self, country_code, zip_code, city):
        error = dict()

        config_url = request.env['ir.config_parameter'].get_param('geonames_url', default="http://download.geonames.org/export/zip/")

        url = config_url + country_code + '.zip'

        res_request = requests.get(url)

        error["config"] = False
        zip_code_is_valid = False

        if res_request.status_code != requests.codes.ok:
            logger.info('400 Bad Request error')
            error["config"] = True
            return error, zip_code_is_valid

        f_geonames = zipfile.ZipFile(StringIO.StringIO(res_request.content))
        tempdir = tempfile.mkdtemp(prefix='openerp')
        f_geonames.extract('%s.txt' % country_code, tempdir)
        logger.info('The geonames zipfile has been decompressed')
        data_file = open(os.path.join(tempdir, '%s.txt' % country_code), 'r')
        data_file.seek(0)
        reader = unicodecsv.reader(data_file, encoding='utf-8', delimiter='	')
        for i, row in enumerate(reader):
            if row[0] == country_code and row[1] == zip_code and row[2] == city:
                zip_code_is_valid = True
                break
        data_file.close()
        return error, zip_code_is_valid

    # Change Zip field to required
    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street", "city", "zip", "country_id"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "zip", "country_id"]

    def checkout_form_validate(self, mode, all_form_values, data):

        error, error_message = super(WebsiteSaleAddressVerification, self).checkout_form_validate(mode, all_form_values,
                                                                                                  data)
        if data.get('country_id') and data.get('city') and data.get('zip'):

            country_code = request.env['res.country'].browse(int(data.get('country_id'))).code
            #.strip() to delete the whitespaces on a string beginning or at the end; In case user make a whitespaces
            zip_code = str(data.get('zip')).strip()
            city = str(data.get('city')).strip()

            address_error, zip_code_is_valid = self.search_zipCode_cities(country_code, zip_code, city)

            # verify if the error is not related to the system configuration of Geonames, In this case ; the user will not be blocked!
            if not address_error["config"] and not zip_code_is_valid:
                error["zip"] = 'error'
                error["city"] = 'error'
                error_message.append(_('Invalid Zip Code! It does not match the City.'))

        return error, error_message

    @http.route(['/userInformation'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def userInformation(self, **kw):

        mode = (False, False)
        values = kw
        errors = {}

        if 'submitted' in kw:
            pre_values = self.values_preprocess(False, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            if errors:
                errors['error_message'] = error_msg
                values = kw

            else:
                # Without errors, add the information to database; create a customer
                request.env['res.partner'].sudo().create(values)

                render_values = {
                    'name': values['name'],
                }
                return request.render('website_address_verification.registration', render_values)

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or request.website.user_id.sudo().country_id

        render_values = {
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }
        return request.render("website_address_verification.userInfor", render_values)

    # For Test the page
    @http.route('/registrationsucceeded',type='http',methods=['GET', 'POST'], auth='public', website=True)
    def registration(self, **kw):
        render_values = {
            'name': "user"
        }
        return request.render("website_address_verification.registration", render_values)

# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
import datetime


class AccountMove(models.Model):
    _inherit = "account.move"

    FOR_MONTH = [('01', 'January'), ('02', 'February'), ('03', 'March'),
                 ('04', 'April'), ('05', 'May'), ('06', 'June'),
                 ('07', 'July'), ('08', 'August'), ('09', 'September'),
                 ('10', 'October'), ('11', 'November'), ('12', 'December')]

    FOR_YEAR = [('this_year', 'This year'), ('last_year', 'Last year')]

    def _get_default_date(self):
        today = fields.Date.today()
        if today.day < 5:
            month = fields.Date.today().month
            month = month - 1 if month != 1 else 12
            return today.replace(month=month, day=15)
        else:
            return fields.Date.today()

    eom_accumulation = fields.Date(
        string="EOM accumulation",
        help="End of Month Accumulation.", default=lambda self: self._get_default_date())

    @api.model
    def _get_default_for_month(self):
        return datetime.datetime.now().strftime('%m')

    @api.model
    def dynamic_year_selection(self):
        year = 2022  # start year
        year_list = []
        while year <= datetime.datetime.now().year:
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    @api.model
    def _get_default_for_year(self):
        return str(datetime.datetime.now().year)

    # def dynamic_selection(self):
    #     this_year = datetime.date.today().year
    #     last_year = this_year - 1
    #     selection_value = [(this_year, this_year), (last_year, last_year)]
    #
    #     return selection_value

    for_month = fields.Selection(FOR_MONTH, string='For month', default=_get_default_for_month)
    for_year_number = fields.Selection(selection=lambda self: self.dynamic_year_selection(), string='For year number', default=_get_default_for_year)
    for_year = fields.Selection(FOR_YEAR, string='For year', default='this_year')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('currency_id'):
                inv_currency = self.env['res.currency'].browse(vals.get('currency_id'))
                str_currency = inv_currency.name

                all_bank_with_currency = self.env['res.partner.bank'].search([('currency_id.name', '=', str_currency)])
                if all_bank_with_currency:
                    vals['partner_bank_id'] = all_bank_with_currency[0].id
                else:
                    bank_no_currency = self.env['res.partner.bank'].search([('currency_id', '=', False)])
                    if bank_no_currency:
                        vals['partner_bank_id'] = bank_no_currency[0].id
            if vals.get('eom_accumulation'):
                vals['eom_accumulation'] = vals.get('eom_accumulation')
        return super().create(vals_list)

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        # for rec in self:
        if self.currency_id:
            str_currency = self.currency_id.name
            all_bank_with_currency = self.env['res.partner.bank'].search([('currency_id.name', '=', str_currency)])
            if all_bank_with_currency:
                self.partner_bank_id = all_bank_with_currency[0]
                return {'domain': {'partner_bank_id': [('currency_id.name', '=', str_currency)]}}
            else:
                bank_no_currency = self.env['res.partner.bank'].search([('currency_id', '=', False)])
                if bank_no_currency:
                    self.partner_bank_id = bank_no_currency[0]
                return {'domain': {'partner_bank_id': [('currency_id', '=', False)]}}

    @api.onchange('for_month')
    def _onchange_for_month(self):
        if self.for_month and self.for_year_number:
            self.eom_accumulation = datetime.date(int(self.for_year_number), int(self.for_month), 15)
        else:
            raise ValidationError(_('You must choose for month and year!'))

    @api.onchange('for_year_number')
    def _onchange_for_year_number(self):
        if self.for_month and self.for_year_number:
            self.eom_accumulation = datetime.date(int(self.for_year_number), int(self.for_month), 15)
        else:
            raise ValidationError(_('You must choose for month and year!'))

    def get_data_first_table(self):
        for rec in self:
            next_number = len(rec.get_list_main_product()) + 1
            list_data = []
            invoice_line = rec.invoice_line_ids
            x = next_number
            for line in invoice_line:
                if not line.product_id:
                    list_data.append([x, line.name, rec.currency_id.name, line.price_subtotal])
                    x += 1
            return list_data

    def get_data_table_second(self):
        for rec in self:
            list_data = []
            invoice_line = rec.invoice_line_ids
            for line in invoice_line:
                if line.product_id:
                    list_data.append(['', line.name, line.quantity, line.price_unit])
            return list_data

    def get_list_main_product(self):
        for rec in self:
            invoice_line = rec.invoice_line_ids
            line_product = [line0 for line0 in invoice_line if line0.product_id]
            for x in line_product:
                line_product_without_x = [a for a in line_product]
                line_product_without_x.remove(x)
                for i in line_product_without_x:
                    if i.product_id.categ_id == x.product_id.categ_id:
                        line_product.remove(i)

            list_data_main_service = []
            num = 1
            for line in line_product:
                total_cost_of_one_service = 0
                for line1 in invoice_line:
                    if line1.product_id.categ_id == line.product_id.categ_id:
                        total_cost_of_one_service += line1.price_subtotal
                each_row = [num, line.product_id.categ_id.name, rec.currency_id.name, total_cost_of_one_service]
                list_data_main_service.append(each_row)
                num += 1
            return list_data_main_service

    # # xử lý sinh mã phiếu invoice theo mã khách hàng
    # def _post(self, soft=True):
    #     # chưa có mã hóa đơn: chỉ áp dụng loại hóa đơn khách hàng
    #     if (not self.name or self.name == '' or self.name == '/') and self.move_type == 'out_invoice':
    #         # xử lý sinh mã theo khách hàng
    #         current_year = datetime.date.today().year
    #         prefix_data = str(current_year) + '-' + self.partner_id.customer_code+'-'
    #         last_move = self.search([('name','ilike',prefix_data)], order='id desc', limit=1)
    #         if last_move:
    #             next_seq = int(last_move.name.split("-")[-1]) + 1
    #         elif self.partner_id.num_invoice:
    #             next_seq = int(self.partner_id.num_invoice) + 1
    #         else:
    #             total_by_customer = self.search([('partner_id','=',self.partner_id.id), ('move_type','=','out_invoice'),('state','=','posted')])
    #             next_seq = (len(total_by_customer) + 1) if total_by_customer else 1
    #         self.name = str(current_year) + '-' + self.partner_id.customer_code+'-'+str(next_seq).zfill(4)
    #     res = super(AccountMove, self)._post(soft)
    #     if self.partner_id.num_invoice:
    #         self.partner_id.num_invoice = next_seq
    #
    #     return res

    def _post(self, soft=True):
        # chưa có mã hóa đơn: chỉ áp dụng loại hóa đơn khách hàng
        if (not self.name or self.name == '' or self.name == '/') and self.move_type == 'out_invoice':
            # xử lý sinh mã theo khách hàng
            current_year = datetime.date.today().year

            prefix_data = str(current_year) + '-' + self.partner_id.customer_code + '-'
            last_move = self.search([('name', 'ilike', prefix_data)], order='id desc', limit=1)
            if last_move:
                next_seq = int(last_move.name.split("-")[-1]) + 1
            elif self.partner_id.num_invoice:
                next_seq = int(self.partner_id.num_invoice) + 1
            else:
                total_by_customer = self.search(
                    [('partner_id', '=', self.partner_id.id), ('move_type', '=', 'out_invoice'),
                     ('state', '=', 'posted')])
                next_seq = (len(total_by_customer) + 1) if total_by_customer else 1
            self.name = str(current_year) + '-' + self.partner_id.customer_code + '-' + str(next_seq).zfill(4)
        res = super(AccountMove, self)._post(soft)

        if self.partner_id.num_invoice and self.move_type == 'out_invoice':
            self.partner_id.num_invoice = int(self.partner_id.num_invoice) + 1

        return res

    def button_draft(self):
        super(AccountMove, self).button_draft()
        if self.partner_id.num_invoice and self.move_type == 'out_invoice':
            self.partner_id.num_invoice = int(self.partner_id.num_invoice) - 1

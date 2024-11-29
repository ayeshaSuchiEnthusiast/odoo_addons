# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import _, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    accountMove_ids = fields.Many2many(
        'account.move',
        'account_move_stock_picking_rel',
        'stock_picking_id',
        'account_move_id',
        string='Vendor Bills',
        copy='False'
    )
    accountMove_count = fields.Integer('Bill', compute="_compute_account_move_count")

    def button_validate(self):
        self.ensure_one()
        res = super().button_validate()

        # Gather all products and quantities from the picking
        picking_lines = self.move_line_ids_without_package
        product_quantities = {
            line.product_id.id: line.quantity for line in picking_lines
        }

        # Find vendor bills that are not already linked to any picking
        bills = self.env['account.move'].search([
            ('invoice_origin', '=', self.origin),
            ('state', '=', 'posted'),  # Ensure the bill is posted
            ('move_type', '=', 'in_invoice'),  # For vendor bills
            ('id', 'not in', self.env['stock.picking'].mapped('accountMove_ids').ids),  # Exclude already linked bills
        ])

        linked_bills = []
        for bill in bills:
            bill_lines = bill.invoice_line_ids
            for line in bill_lines:
                if (line.product_id.id in product_quantities and
                        line.quantity == product_quantities[line.product_id.id]):
                    linked_bills.append(bill.id)

        if linked_bills:
            # Link the matching bills to the current stock picking
            self.accountMove_ids = [(6, 0, linked_bills)]

        return res

    def _compute_account_move_count(self):
        for picking in self:
            picking.accountMove_count = len(picking.accountMove_ids)

    def get_account_move(self):
        return {
            'name': _('Bill'),
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.accountMove_ids.ids)],
        }

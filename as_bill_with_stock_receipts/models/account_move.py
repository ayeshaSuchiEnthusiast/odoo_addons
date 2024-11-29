from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    receipt_picking_ids = fields.Many2many(
        'stock.picking',
        'account_move_stock_picking_rel',
        'account_move_id',
        'stock_picking_id',
        string='Stock Pickings',
        copy='False'
    )
    receipt_picking_count = fields.Integer('Pickings', compute="_compute_receipt_picking_count")

    def action_post(self):
        for move in self:
            # Gather all products and quantities from the bill
            bill_lines = move.invoice_line_ids
            product_quantities = {
                line.product_id.id: line.quantity for line in bill_lines
            }
            # Find matching stock pickings
            pickings = self.env['stock.picking'].search([
                ('origin', '=', self.invoice_origin),
                ('state', '=', 'done'),  # Ensure only completed pickings are considered
                ('picking_type_id.code', '=', 'incoming'),  # For vendor receipts
                ('id', 'not in', self.env['account.move'].mapped('receipt_picking_ids').ids)
                # Exclude already linked pickings
            ])
            linked_pickings = []
            for picking in pickings:
                print("picking ", picking, "- ", picking.state)
                picking_lines = picking.move_line_ids_without_package
                for line in picking_lines:
                    if (line.product_id.id in product_quantities and
                            line.quantity == product_quantities[line.product_id.id]):
                        linked_pickings.append(picking.id)
            if linked_pickings:
                move.receipt_picking_ids = [(6, 0, linked_pickings)]
        return super().action_post()

    def _compute_receipt_picking_count(self):
        for move in self:
            move.receipt_picking_count = len(move.receipt_picking_ids)

    def get_picking(self):
        return {
            'name': _('Picking'),
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.receipt_picking_ids.ids)],
        }

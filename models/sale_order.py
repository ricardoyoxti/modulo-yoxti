from odoo import models, fields, api
import json
import base64
from datetime import datetime
class SaleOrder(models.Model):
_inherit = 'sale.order'
def action_export_customers_json(self):
    """Acción para abrir el wizard de exportación"""
    # Si hay pedidos seleccionados, usar esos
    if self.env.context.get('active_ids'):
        order_ids = self.env.context.get('active_ids')
        orders = self.browse(order_ids)
        partner_ids = orders.mapped('partner_id')
        date_from = min(orders.mapped('date_order')).date()
        date_to = max(orders.mapped('date_order')).date()
    else:
        # Si es desde un solo pedido
        partner_ids = self.partner_id
        date_from = self.date_order.date()
        date_to = self.date_order.date()

    return {
        'name': 'Exportar Clientes a JSON',
        'type': 'ir.actions.act_window',
        'res_model': 'customer.export.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_partner_ids': [(6, 0, partner_ids.ids)],
            'default_date_from': date_from,
            'default_date_to': date_to,
        }
    }

def export_customer_data_json(self):
    """Exporta directamente sin wizard (para un solo pedido)"""
    customer_data = self._prepare_customer_json_data([self])
    
    json_data = json.dumps(customer_data, ensure_ascii=False, indent=2)
    filename = f"customer_data_{self.partner_id.name}_{self.name}.json"
    
    # Crear attachment temporal
    attachment = self.env['ir.attachment'].create({
        'name': filename,
        'type': 'binary',
        'datas': base64.b64encode(json_data.encode('utf-8')),
        'res_model': 'sale.order',
        'res_id': self.id,
        'mimetype': 'application/json',
    })

    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/{attachment.id}/{filename}?download=true',
        'target': 'self',
    }

@api.model
def _prepare_customer_json_data(self, orders):
    """Prepara los datos JSON de los clientes"""
    customer_data = {}
    
    for order in orders:
        partner = order.partner_id
        partner_key = partner.id

        if partner_key not in customer_data:
            customer_info = {
                'id': partner.id,
                'name': partner.name or '',
                'email': partner.email or '',
                'phone': partner.phone or '',
                'mobile': partner.mobile or '',
                'vat': partner.vat or '',
                'street': partner.street or '',
                'street2': partner.street2 or '',
                'city': partner.city or '',
                'state_name': partner.state_id.name if partner.state_id else '',
                'zip': partner.zip or '',
                'country_name': partner.country_id.name if partner.country_id else '',
                'latitude': float(partner.partner_latitude) if partner.partner_latitude else None,
                'longitude': float(partner.partner_longitude) if partner.partner_longitude else None,
                'category_names': [cat.name for cat in partner.category_id],
                'is_company': partner.is_company,
                'orders': [],
                'total_orders': 0,
                'total_amount': 0.0
            }
            customer_data[partner_key] = customer_info

        # Información del pedido
        order_info = {
            'order_id': order.id,
            'name': order.name,
            'date_order': order.date_order.strftime('%Y-%m-%d %H:%M:%S'),
            'state': order.state,
            'amount_total': float(order.amount_total),
            'currency': order.currency_id.name if order.currency_id else '',
            'order_lines': []
        }

        # Líneas del pedido
        for line in order.order_line:
            if not line.display_type:  # Excluir líneas de sección y nota
                line_info = {
                    'product_name': line.product_id.name if line.product_id else '',
                    'product_code': line.product_id.default_code if line.product_id else '',
                    'quantity': float(line.product_uom_qty),
                    'unit_price': float(line.price_unit),
                    'subtotal': float(line.price_subtotal),
                }
                order_info['order_lines'].append(line_info)

        customer_data[partner_key]['orders'].append(order_info)
        customer_data[partner_key]['total_orders'] += 1
        customer_data[partner_key]['total_amount'] += float(order.amount_total)

    return {
        'export_info': {
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_customers': len(customer_data),
            'total_orders': len(orders)
        },
        'customers': list(customer_data.values())
    }
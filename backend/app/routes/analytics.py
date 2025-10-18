from flask import Blueprint, request, jsonify, send_file
from app import get_db
from app.utils.auth import role_required, get_current_user_id
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/brands/<brand_id>/insights', methods=['GET'])
@role_required('brand', 'admin')
def get_brand_insights(brand_id):
    """Get analytics insights for a brand"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Verify ownership (unless admin)
        from app.utils.auth import get_current_user_role
        if get_current_user_role() == 'brand':
            brand = db.brands.find_one({'userId': ObjectId(user_id)})
            if not brand or str(brand['_id']) != brand_id:
                return jsonify({'error': 'Not authorized'}), 403
        else:
            brand = db.brands.find_one({'_id': ObjectId(brand_id)})
        
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Get date range from query params
        start_date_str = request.args.get('start', (datetime.utcnow() - timedelta(days=30)).isoformat())
        end_date_str = request.args.get('end', datetime.utcnow().isoformat())
        
        start_date = datetime.fromisoformat(start_date_str.replace('Z', ''))
        end_date = datetime.fromisoformat(end_date_str.replace('Z', ''))
        
        # Get brand's products
        products = list(db.products.find({'brandId': ObjectId(brand_id)}))
        product_ids = [p['_id'] for p in products]
        
        if not product_ids:
            return jsonify({
                'totalSales': 0,
                'totalOrders': 0,
                'totalUnits': 0,
                'averageOrderValue': 0,
                'topProducts': [],
                'topSupermarkets': [],
                'salesByDate': [],
                'refundRate': 0
            }), 200
        
        # Get orders containing brand's products
        orders = list(db.orders.find({
            'items.productId': {'$in': product_ids},
            'createdAt': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Calculate metrics
        total_sales = 0
        total_units = 0
        product_sales = defaultdict(lambda: {'units': 0, 'revenue': 0, 'name': ''})
        supermarket_sales = defaultdict(lambda: {'orders': 0, 'revenue': 0, 'name': ''})
        daily_sales = defaultdict(float)
        
        delivered_orders = [o for o in orders if o.get('status') == 'delivered']
        cancelled_orders = [o for o in orders if o.get('status') == 'cancelled']
        
        for order in delivered_orders:
            for item in order.get('items', []):
                if item['productId'] in product_ids:
                    item_total = item['qty'] * item['unitPrice']
                    total_sales += item_total
                    total_units += item['qty']
                    
                    # Product sales
                    product_id = str(item['productId'])
                    product_sales[product_id]['units'] += item['qty']
                    product_sales[product_id]['revenue'] += item_total
                    product_sales[product_id]['name'] = item.get('name', '')
                    
                    # Daily sales
                    date_key = order['createdAt'].strftime('%Y-%m-%d')
                    daily_sales[date_key] += item_total
            
            # Supermarket sales
            if order.get('supermarketPickedFrom'):
                sm_id = str(order['supermarketPickedFrom'])
                supermarket_sales[sm_id]['orders'] += 1
                
                # Calculate revenue from brand products only
                brand_revenue = sum(
                    item['qty'] * item['unitPrice']
                    for item in order.get('items', [])
                    if item['productId'] in product_ids
                )
                supermarket_sales[sm_id]['revenue'] += brand_revenue
        
        # Top products
        top_products = sorted(
            product_sales.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:10]
        
        top_products_list = [
            {
                'productId': pid,
                'name': data['name'],
                'units': data['units'],
                'revenue': data['revenue']
            }
            for pid, data in top_products
        ]
        
        # Top supermarkets
        for sm_id in supermarket_sales.keys():
            supermarket = db.supermarkets.find_one({'_id': ObjectId(sm_id)})
            if supermarket:
                supermarket_sales[sm_id]['name'] = supermarket['name']
        
        top_supermarkets = sorted(
            supermarket_sales.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:10]
        
        top_supermarkets_list = [
            {
                'supermarketId': sid,
                'name': data['name'],
                'orders': data['orders'],
                'revenue': data['revenue']
            }
            for sid, data in top_supermarkets
        ]
        
        # Sales by date
        sales_by_date = [
            {'date': date, 'sales': amount}
            for date, amount in sorted(daily_sales.items())
        ]
        
        # Calculate metrics
        total_orders = len(delivered_orders)
        average_order_value = total_sales / total_orders if total_orders > 0 else 0
        refund_rate = len(cancelled_orders) / len(orders) if len(orders) > 0 else 0
        
        # Average delivery time
        delivery_times = []
        for order in delivered_orders:
            if order.get('createdAt') and order.get('actualDeliveryTime'):
                delta = order['actualDeliveryTime'] - order['createdAt']
                delivery_times.append(delta.total_seconds() / 60)  # in minutes
        
        avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
        
        return jsonify({
            'totalSales': round(total_sales, 2),
            'totalOrders': total_orders,
            'totalUnits': total_units,
            'averageOrderValue': round(average_order_value, 2),
            'averageDeliveryTime': round(avg_delivery_time, 2),
            'refundRate': round(refund_rate * 100, 2),
            'topProducts': top_products_list,
            'topSupermarkets': top_supermarkets_list,
            'salesByDate': sales_by_date
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/brands/<brand_id>/insights/export', methods=['GET'])
@role_required('brand', 'admin')
def export_brand_insights(brand_id):
    """Export brand insights as CSV, XLSX, or PDF"""
    try:
        db = get_db()
        user_id = get_current_user_id()
        
        # Verify ownership
        from app.utils.auth import get_current_user_role
        if get_current_user_role() == 'brand':
            brand = db.brands.find_one({'userId': ObjectId(user_id)})
            if not brand or str(brand['_id']) != brand_id:
                return jsonify({'error': 'Not authorized'}), 403
        else:
            brand = db.brands.find_one({'_id': ObjectId(brand_id)})
        
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Get export format
        export_format = request.args.get('format', 'csv').lower()
        
        # Get date range
        start_date_str = request.args.get('start', (datetime.utcnow() - timedelta(days=30)).isoformat())
        end_date_str = request.args.get('end', datetime.utcnow().isoformat())
        
        start_date = datetime.fromisoformat(start_date_str.replace('Z', ''))
        end_date = datetime.fromisoformat(end_date_str.replace('Z', ''))
        
        # Get data
        products = list(db.products.find({'brandId': ObjectId(brand_id)}))
        product_ids = [p['_id'] for p in products]
        
        orders = list(db.orders.find({
            'items.productId': {'$in': product_ids},
            'status': 'delivered',
            'createdAt': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Prepare data for export
        export_data = []
        for order in orders:
            for item in order.get('items', []):
                if item['productId'] in product_ids:
                    export_data.append({
                        'Order ID': str(order['_id']),
                        'Date': order['createdAt'].strftime('%Y-%m-%d %H:%M:%S'),
                        'Product': item.get('name', ''),
                        'Quantity': item['qty'],
                        'Unit Price': item['unitPrice'],
                        'Total': item['qty'] * item['unitPrice'],
                        'Status': order['status']
                    })
        
        # Generate export file
        if export_format == 'csv':
            df = pd.DataFrame(export_data)
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{brand["name"]}_insights_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        
        elif export_format == 'xlsx':
            df = pd.DataFrame(export_data)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sales Data')
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{brand["name"]}_insights_{datetime.now().strftime("%Y%m%d")}.xlsx'
            )
        
        elif export_format == 'pdf':
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(f"<b>{brand['name']} - Sales Report</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Date range
            date_info = Paragraph(
                f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                styles['Normal']
            )
            elements.append(date_info)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Summary statistics
            total_revenue = sum(row['Total'] for row in export_data)
            total_orders = len(set(row['Order ID'] for row in export_data))
            
            summary = Paragraph(
                f"<b>Summary:</b><br/>"
                f"Total Orders: {total_orders}<br/>"
                f"Total Revenue: ₹{total_revenue:.2f}<br/>"
                f"Total Items Sold: {len(export_data)}",
                styles['Normal']
            )
            elements.append(summary)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Table
            if export_data:
                table_data = [list(export_data[0].keys())]
                table_data.extend([list(row.values()) for row in export_data[:50]])  # Limit to 50 rows for PDF
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
            
            doc.build(elements)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'{brand["name"]}_insights_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
        
        else:
            return jsonify({'error': 'Invalid format. Use csv, xlsx, or pdf'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

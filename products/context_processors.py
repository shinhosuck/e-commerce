from django.contrib.auth.models import User
from .models import Receipt, ShippingAddress
from django.conf import settings
from django.core.files import File
from decimal import Decimal
import uuid



def get_cart_total(request):
    user = request.user
    vat_rate = Decimal('.12')
    discount_amount = []
    product_subtotals = []
    

    try:
        customer = User.objects.get(id=user.id)
    except User.DoesNotExist:
        return {'error': 'User is not authenticated.'}
    
    orders = customer.orders.filter(open=True).select_related('product')
    
    if orders.exists():
        for order in orders:
            # get discount amount
            amount = order.product.get_discount_price()
            if amount:
                discount_price = amount.replace(',', '')
                discount = round((order.product.price - Decimal(discount_price)) * order.quantity, 2)
                discount_amount.append(discount)
            
        # Add discount amount
        if discount_amount:
            discount_amount = f'{sum(discount_amount):,.2f}'

        # Add order quantity
        order_quantity = sum([order.quantity for order in orders])

        # each product sub_total
        for order in orders:
            amount = order.get_order_total()
            product_subtotals.append({'id':order.product.id, 'subtotal':amount})

        # order summary sub_total
        sub_total = sum([Decimal(order.get_order_total().replace(',', '')) for order in orders])
        sub_total = f'{sub_total:,.2f}'

        # calculate tax/vat
        edit_sub_total = Decimal(sub_total.replace(',', ''))
        vat_amount = edit_sub_total * vat_rate
        
        total = f'{vat_amount + edit_sub_total:,.2f}'
        vat = f'{vat_amount:,.2f}'

        return {
            'num_of_product': order_quantity, 
            'sub_total': sub_total, 
            'discount_amount': discount_amount or '',
            'product_subtotals': product_subtotals,
            'total': total,
            'vat': vat
        }
    
    return {'num_of_product': 0}
    

def create_checkout_summary(request, receipts=None, receipt_id=None):
    if receipt_id:
        try:
            receipt = Receipt.objects.get(id=receipt_id)
        except Receipt.DoesNotExist:
            return {'error': 'Receipt does not exist.'}
        
        if not receipt.checkout_summary:
            media_root = settings.MEDIA_ROOT
            id = uuid.uuid4()

            address = ShippingAddress.objects.get(customer=receipt.customer)
            full_name = f'{address.first_name} {address.last_name}'

            saving = ''
            if not receipt.saving:
                saving = 'n/a'
            else:
                saving = receipt.saving
            
            receipt_id = receipt.id
            customer = full_name
            saving = saving
            sub_total = receipt.sub_total
            tax = receipt.tax 
            total = receipt.total

            with open(f'{media_root}/checkout_summary/checkout_summary-{id}.txt', 'w') as f:
                file = File(f)
                file.write(f'ID: {receipt_id}\nCustomer: {customer}\nSaving: {saving}\nSub-total: {sub_total}\nTax: {tax}\nTotal: {total}')
                receipt.checkout_summary = f'/checkout_summary/checkout_summary-{id}.txt'
                receipt.save()
    return ''
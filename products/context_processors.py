from django.contrib.auth.models import User
from .models import CheckoutReceipt
from decimal import Decimal

def get_basket_total(request):
    user = request.user
    discount_amount = []
    order_total = []
    
    try:
        customer = User.objects.get(username=user.username)
    except Exception as e:
        return {'error': f'{e}', 'num_of_product': 0}
    
    if customer:
        query_set = customer.order_set.all().filter(open=True)
        for obj in query_set:
            if obj.product.get_discount_price():
                discount_price = obj.product.get_discount_price().replace(',', '')
                discount = round((obj.product.price - Decimal(discount_price)) * obj.quantity, 2)
                if discount:
                    discount_amount.append(discount)

        order_quantity = [order.quantity for order in customer.order_set.all().filter(open=True)]
        sub_total = [order.get_order_total() for order in customer.order_set.all().filter(open=True)]

        # format get_order_total() from Order model
        for order in customer.order_set.all().filter(open=True):
            total = order.get_order_total()
            decimal_to_str = f'{str(total)[:-6]},{str(total)[-6:]}'
            order_total.append({'id':order.product.id, 'order_total': decimal_to_str})

        # format discount_amount
        savings_amount = f'{str(round(sum(discount_amount), 2))[0:-6]},{str(round(sum(discount_amount), 2))[-6:]}'
        if str(sum(discount_amount)) != '0':
            discount_amount = savings_amount

        # calculate tax/vat
        cal_vat = str(round(float(sum(sub_total)), 2)*.12)
        for char in cal_vat:
            if char == '.':
                index = cal_vat.index(char)
                cal_vat = cal_vat[0 : index+3]

        vat = str(Decimal(cal_vat))
        vat = f'{vat[0:-6]},{vat[-6:]}'

        cal_total = f'{Decimal(cal_vat)+sum(sub_total)}'
        total = f'{cal_total[0:-6]},{cal_total[-6:]}'

        # format sub_total
        total_amount = f'{str(round(sum(sub_total), 2))[0:-6]},{str(round(sum(sub_total), 2))[-6:]}'
        sub_total = total_amount
       
        if order_quantity:
            return {
                'num_of_product': sum(order_quantity), 
                'sub_total': sub_total, 
                'discount_amount': discount_amount,
                'order_total': order_total,
                'total': total,
                'vat': vat
            }
    return {'num_of_product': 0}
    

def get_customer_receipt(request):
    
    try:
        receipt = CheckoutReceipt.objects.get(id=id)
    except Exception as e:
       return {'error': f'{e}'}
    
    
    discount_amount = []
    orders = receipt.checkout.order.all()
    order_total = []

    for order in orders:
        total = f'{str(order.get_order_total())[0:-6]},{str(order.get_order_total())[-6:]}'
        order_total.append({'id':order.id, 'total':total})

        if order.product.get_discount_price():
            discount_price = order.product.get_discount_price().replace(',', '')
            amount = round((order.product.price - Decimal(discount_price)) * order.quantity, 2)
            discount_amount.append({'id':order.product.id, 'discount_amount': f'{str(amount)[0:-6]},{str(amount)[-6:]}'})

    total = round(Decimal(round(float(receipt.checkout.total_amount_due)*.12, 2)) + receipt.checkout.total_amount_due, 2)
    total = f'{str(total)[0:-6]},{str(total)[-6:]}'

    tax = round(float(receipt.checkout.total_amount_due)*.12, 2)
    tax = f'{str(tax)[0:-6]},{str(tax)[-6:]}'

    total_amount = round(receipt.checkout.total_amount_due, 2)
    total_amount = f'{str(total_amount)[0:-6]},{str(total_amount)[-6:]}'

    return {
        'receipt_id': receipt.id, 
        'customer': receipt.checkout.customer.username,
        'orders': orders, 
        'receipt_discount_amount': discount_amount,
        'receipt_order_total': order_total,
        'total_amount': total_amount,
        'tax': tax,
        'receipt_total': total
    }

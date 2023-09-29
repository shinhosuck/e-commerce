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
                discount = (obj.product.price - Decimal(discount_price)) * obj.quantity
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
        savings_amount = f'{str(sum(discount_amount))[0:-6]},{str(sum(discount_amount))[-6:]}'
        if str(sum(discount_amount)) == '0':
            discount_amount = '0'
        else:
            discount_amount = savings_amount

        # calculate tax/vat
        cal_vat = str(float(sum(sub_total))*.12)
        for char in cal_vat:
            if char == '.':
                index = cal_vat.index(char)
                cal_vat = cal_vat[0 : index+3]

        vat = str(Decimal(cal_vat))
        vat = f'{vat[0:-6]},{vat[-6:]}'

        cal_total = f'{Decimal(cal_vat)+sum(sub_total)}'
        total = f'{cal_total[0:-6]},{cal_total[-6:]}'

        # format sub_total
        total_amount = f'{str(sum(sub_total))[0:-6]},{str(sum(sub_total))[-6:]}'
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
    customer = request.user

    try:
        receipt = CheckoutReceipt.objects.get(customer=customer, sent=False)
    except Exception as e:
       return {'error': f'{e}'}
    
    discount_amount = []
    orders = receipt.checkout.order.all()
    for order in orders:
        if order.product.get_discount_price():
            amount = (order.product.price - order.product.get_discount_price()) * order.quantity
            discount_amount.append(
                {
                    'name':order.product.name, 
                    'discount_amount': amount
                }
            )

    receipt.sent = True
    receipt.save()
    return {
        'receipt_id': receipt.id, 
        'customer': receipt.checkout.customer.username,
        'orders': orders, 
        'discount_amount': discount_amount,
        'total_amount_paid': receipt.checkout.total_amount_due
    }
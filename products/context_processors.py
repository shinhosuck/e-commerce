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
    

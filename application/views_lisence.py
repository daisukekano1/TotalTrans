from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from application.models import CustomUser, UserPayment
from application.customlib import GoogleApiLib, CookieLib
import payjp

@login_required
def activatelisence(request):
    CookieLib.setLanguage(request)
    user = CustomUser.objects.filter(id=request.user.id).first()
    data = {
        'user' : user
    }
    return render(request, 'app/lisence_activation.html', data)


@login_required
def saveactivatelisence(request):
    payjp.api_key = 'sk_test_f606684ccf89682213b11a1e'
    plan_month = "pln_50a7332afd19d5fe8dd611ac65e6"
    user = CustomUser.objects.filter(id=request.user.id).first()
    ##顧客作成
    userpayment = UserPayment.objects.filter(user_id=request.user.id).first()
    customer = None
    if userpayment == None:
        customer = payjp.Customer.create(
            description = user.email
        )
        userpayment = UserPayment(
            user_id = request.user.id,
            customerid = customer.id
        )
        userpayment.save()
    else:
        customer = payjp.Customer.retrieve(userpayment.customerid)

    ##トークン作成
    token = payjp.Token.create(
        card={
            'number': '4242424242424242',
            'cvc': '123',
            'exp_month': '2',
            'exp_year': '2024'
            # 'number': str(request.POST['number']),
            # 'cvc': str(request.POST['cvc']),
            # 'exp_month': str(request.POST['exp_month']),
            # 'exp_year': str(request.POST['exp_year'])
        },
        headers={'X-Payjp-Direct-Token-Generate': 'true'}
    )
    ##カード作成
    customer.cards.create(
        card = token.id
    )
    ##定期課金作成
    payjp.Subscription.create(
        plan = plan_month,
        customer=customer.id
    )
    user = CustomUser.objects.filter(id=request.user.id).first()
    data = {
        'user' : user
    }
    return render(request, 'app/lisence_activation.html', data)
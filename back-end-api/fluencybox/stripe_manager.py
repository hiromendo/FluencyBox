import stripe
from fluencybox.config import STRIPE_API_KEY, HANASU_PLAN_ID

def get_stripe():
    stripe.api_key = STRIPE_API_KEY
    return stripe

def create_customer(user):
    try:
        resp_dict = {}
        stripe = get_stripe()

        customer = stripe.Customer.create(
        description=user.email_address,
        email = user.email_address,
        name = user.first_name + ' ' +  user.last_name
        )
        
        resp_dict['status'] = 'success'
        resp_dict['message'] = customer
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def create_payment_token():
    try:
        resp_dict = {}
        stripe = get_stripe()

        payment_token = stripe.Token.create(card={"number": "4242424242424242", "exp_month": 12, "exp_year": 2020, "cvc": "314"})

        resp_dict['status'] = 'success'
        resp_dict['message'] = payment_token
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def create_card(customer, payment_token):
    try:
        resp_dict = {}
        stripe = get_stripe()

        card = stripe.Customer.create_source(customer,source=payment_token)

        resp_dict['status'] = 'success'
        resp_dict['message'] = card
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict


def create_subscription(customer, card_id):
    try:
        resp_dict = {}
        stripe = get_stripe()

        subscription = stripe.Subscription.create(customer=customer,default_payment_method = card_id, items=[{"plan": HANASU_PLAN_ID}])

        resp_dict['status'] = 'success'
        resp_dict['message'] = subscription
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def get_invoice(invoice_id):
    try:
        resp_dict = {}
        stripe = get_stripe()

        invoice = stripe.Invoice.retrieve(invoice_id)

        resp_dict['status'] = 'success'
        resp_dict['message'] = invoice
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

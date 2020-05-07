from flask import request, Response
import json
import stripe
from fluencybox import db
from fluencybox.models import Subscriptions, Subscription_Contracts, Credit_Cards, Current_Subscription_Contracts
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

def delete_card(customer_id, card_id):
    try:
        resp_dict = {}
        stripe = get_stripe()

        delete_response = stripe.Customer.delete_source(customer_id, card_id)

        resp_dict['status'] = 'success'
        resp_dict['message'] = delete_response
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def delete_subscription(subscription_id):
    try:
        resp_dict = {}
        
        stripe = get_stripe()
        cancel_response = stripe.Subscription.delete(subscription_id)
      
        resp_dict['status'] = 'success'
        resp_dict['message'] = cancel_response
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def webhook_event_handler(payload):
    resp_dict = {}
    stripe = get_stripe()

    try:
        event = None
        
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        # Invalid payload
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict
    
    try:
        if event.type == 'customer.subscription.deleted':
            customer_subscription = event.data.object
            
            my_subscription = Subscriptions.query.filter_by(stripe_subscription_id = customer_subscription.id).first()
            my_subscription.status = 'inactive'
            db.session.commit()

            resp_dict['status'] = 'success'
        elif event.type == 'invoice.created':
            invoice = event.data.object
            #Get my subscription
            my_subscription = Subscriptions.query.filter_by(stripe_subscription_id = invoice.subscription).first()
            #Get the latest card added
            my_card = Credit_Cards.query.filter_by(user_id = my_subscription.user_id).order_by(Credit_Cards.id.desc()).first()
            
            period_start = datetime.datetime.fromtimestamp(int(invoice.period_start)).strftime('%Y-%m-%d %H:%M:%S')
            period_end = datetime.datetime.fromtimestamp(int(invoice.period_end)).strftime('%Y-%m-%d %H:%M:%S')

            new_subscription_contract = Subscription_Contracts(subscription = my_subscription, stripe_plan_id =  HANASU_PLAN_ID, amount = 999, stripe_invoice_id = invoice.id, credit_card = my_card, period_start = period_start, period_end = period_end)
            db.session.add(new_subscription_contract)
            db.session.commit()

            
            resp_dict['status'] = 'success'
        elif event.type == 'invoice.payment_failed':
            payment_failed_invoice = event.data.object

            #Get my subscription
            my_subscription = Subscriptions.query.filter_by(stripe_subscription_id = payment_failed_invoice.subscription).first()

            #Get my current subscription contract
            my_current_subscription_contract = Current_Subscription_Contracts.query.filter_by(subscription_id = my_subscription.id).first()

            #Get my subscription contract
            my_subscription_contract = Subscription_Contracts.query.filter_by(stripe_invoice_id = payment_failed_invoice.id).first()

            #If my subscription contract for the failed invoice doesn't exist, insert it
            if not my_subscription_contract:
                #Get the latest card added
                my_card = Credit_Cards.query.filter_by(user_id = my_subscription.user_id).order_by(Credit_Cards.id.desc()).first()
            
                period_start = datetime.datetime.fromtimestamp(int(payment_failed_invoice.period_start)).strftime('%Y-%m-%d %H:%M:%S')
                period_end = datetime.datetime.fromtimestamp(int(payment_failed_invoice.period_end)).strftime('%Y-%m-%d %H:%M:%S')

                new_subscription_contract = Subscription_Contracts(subscription = my_subscription, stripe_plan_id =  HANASU_PLAN_ID, amount = 999, stripe_invoice_id = payment_failed_invoice.id, credit_card = my_card, period_start = period_start, period_end = period_end)
                db.session.add(new_subscription_contract)
                my_current_subscription_contract.subscription_contract = new_subscription_contract
                db.session.commit()


            my_current_subscription_contract.subscription_contract = my_subscription_contract
            my_subscription.status = 'inactive'
            db.session.commit()

            
            resp_dict['status'] = 'success'
        elif event.type == 'invoice.payment_succeeded':
            payment_succeeded = event.data.object 
            #Get my subscription
            my_subscription = Subscriptions.query.filter_by(stripe_subscription_id = payment_succeeded.subscription).first()

            #Get my current subscription contract
            my_current_subscription_contract = Current_Subscription_Contracts.query.filter_by(subscription_id = my_subscription.id).first()

            #Get my subscription contract
            my_subscription_contract = Subscription_Contracts.query.filter_by(stripe_invoice_id = payment_succeeded.id).first()

            #If my subscription contract for the failed invoice doesn't exist, insert it
            if not my_subscription_contract:
                #Get the latest card added
                my_card = Credit_Cards.query.filter_by(user_id = my_subscription.user_id).order_by(Credit_Cards.id.desc()).first()
            
                period_start = datetime.datetime.fromtimestamp(int(payment_succeeded.period_start)).strftime('%Y-%m-%d %H:%M:%S')
                period_end = datetime.datetime.fromtimestamp(int(payment_succeeded.period_end)).strftime('%Y-%m-%d %H:%M:%S')

                new_subscription_contract = Subscription_Contracts(subscription = my_subscription, stripe_plan_id =  HANASU_PLAN_ID, amount = 999, stripe_invoice_id = payment_succeeded.id, stripe_charge_id = payment_succeeded.charge, credit_card = my_card, period_start = period_start, period_end = period_end)
                db.session.add(new_subscription_contract)
                my_current_subscription_contract.subscription_contract = new_subscription_contract
                db.session.commit()
            
            my_current_subscription_contract.subscription_contract = my_subscription_contract
            my_current_subscription_contract.stripe_charge_id = payment_succeeded.charge
            my_subscription.status = 'active'
            db.session.commit()
            
            
            resp_dict['status'] = 'success'
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'unexpected event received'
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict





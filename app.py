from flask import Flask, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from random import choice
from responses import *
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://EComCSSA:3ComC22A@ecomcs.c390nx6k6ql6.us-east-1.rds.amazonaws.com:1433/EComCS_v1'
db = SQLAlchemy(app)


metadata = MetaData()
metadata.reflect(db.engine)
Base = automap_base(metadata=metadata)
Base.prepare()

Customer = Base.classes.Customer
Order = Base.classes.Order
OrderItems = Base.classes.OrderItems
Ticket = Base.classes.Ticket
Feedback = Base.classes.Feedback
Product = Base.classes.Product


def save(self):
    current_db_sessions = db.session.object_session(self)
    current_db_sessions.add(self)
    current_db_sessions.commit()


def remove(self):
    current_db_sessions = db.session.object_session(self)
    current_db_sessions.delete(self)
    current_db_sessions.commit()
    return self


setattr(Customer, 'save', save)
setattr(Order, 'save', save)
setattr(OrderItems, 'save', save)
setattr(Ticket, 'save', save)
setattr(Feedback, 'save', save)
setattr(Product, 'save', save)

setattr(Customer, 'remove', remove)
setattr(Order, 'remove', remove)
setattr(OrderItems, 'remove', remove)
setattr(Ticket, 'remove', remove)
setattr(Feedback, 'remove', remove)
setattr(Product, 'remove', remove)

setattr(Customer, 'filter_by', db.session.query(Customer).filter_by)
setattr(Order, 'filter_by', db.session.query(Order).filter_by)
setattr(OrderItems, 'filter_by', db.session.query(OrderItems).filter_by)
setattr(Ticket, 'filter_by', db.session.query(Ticket).filter_by)
setattr(Feedback, 'filter_by', db.session.query(Feedback).filter_by)
setattr(Product, 'filter_by', db.session.query(Product).filter_by)


def respond(res):
    return make_response(jsonify({'fulfillmentText': res+ ' \n Would you like to share experience to get us more better?'}))

global customer
@app.route('/', methods=['POST'])
def home():
    res = ''
    req = request.get_json()
    parameters = None
    result = req.get('queryResult')
    action = result.get('action')

    if action == 'support.feedback.event.feedback':
        # result = db.session.query(Customer).filter(Customer.email == email)

        message = result.get('quertText') 
        customer = Customer.filter_by(email=email).first()
        if customer:
            feed_dict = {'customer': customer,
                         'feedback': message, 'tag': 'customer'}
            feedback = Feedback(**feed_dict)
            feedback.save()
            response_messages = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                f"We have recorded your feedback as follows: \n{message}"
                            ]
                        },
                        "text": {
                            "text": [
                               "We take your feedback very seriously. Thank you for sharing it with us." 
                            ]
                        }
                    }
                ]
            }
            res = 'Thank you for providing the feedback. You make us serve better'
        else:
            res = 'I was unable to verify your email id. \
                       Please enter the correct email id.'
    elif 'support.feedback' in action:
        message = result.get('outputContexts')[0].get(
            'parameters').get('message.original')

        customer = Customer.filter_by(email=email).first()
        
        if customer:
            feed_dict = {'customer': customer,
                         'feedback': message, 'tag': 'customer'}
            feedback = Feedback(**feed_dict)
            feedback.save()
            response_messages = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                f"We have recorded your feedback as follows: \n{message}"
                            ]
                        },
                        "text": {
                            "text": [
                               "We take your feedback very seriously. Thank you for sharing it with us." 
                            ]
                        }
                    }
                ]
            }
            res = 'Thank you for providing the feedback. You make us serve better.'
        

    if action == 'supportfeedbackevent.supportfeedbackevent-yes.email':
            email = result.get('outputContexts')[0].get('parameters').get('email')
            customer = Customer.filter_by(email=email).first()  
            if customer:
                pass
            else:
                res = 'I was unable to verify your email id. \
                       Please enter the correct email id.'
                

    if action == 'support.refund' or action == 'support.refund-context:supportrefund':
        return handle_refund(result.get('parameters'), ask_feedback=True)

    if action == 'supportproblem-contextsupport-problem.email':
        email = result.get('parameters').get('email')
        customer = Customer.filter_by(email=email).first()
        if customer:
            complaints = result.get('outputContexts')[1].get('parameters').get('message')
            return solve_problem(result.get('parameters'), complaints, ask_feedback = True)
        else:
            res = 'You entered wrong email. Please give the registerd email id.'

    if action == 'support.feedback-contextsupport-directfeedback':
        email = result.get('parameters').get('email')
        customer = Customer.filter_by(email=email).first()
        message = result.get('outputContexts')[0].get('parameters').get('message')
        if customer:
            return direct_feedback(email,message,ask_feedback = True)
        else:
            res = 'You entered wrong email. Please give the registerd email id.'
    
    if action == 'supportfeedbackevent.supportfeedbackevent-yes':
        email = result.get('outputContexts')[2].get('parameters').get('email')
        if email:
            res = 'I am going to record your feedback for email id ' + email
        else:
            res = 'In order to record your feedback, I am going to need your email id.'

    ##  This check is for voice conversation

    if action == 'system.orderID':
        ord_id = int(result.get('parameters').get('order-id'))
        order = db.session.query(Order).filter_by(id=ord_id).first()
        print(ord_id)
        if order:
            order_item = OrderItems.filter_by(order=order).first()
            if order.status == 'Completed':
                res = choice(REFUND_ORDER_COMPLETED).format(order_item.product.title, order.status)
            if order.status == 'Approved' or order.status == 'Pending':
                res = choice(REFUND_ORDER_APPROVED_PENDING).format(order_item.product.title, order.status)
            if order.status == 'Voided':
                res = choice(REFUND_ORDER_VOIDED)
            res = res + ' Do you want me to connect you with the agent for further information'
            # if ask_feedback:
            #     return feedback(res,'')
        else:
            res = 'Please mention the correct order id.'
        return jsonify({'fulfillmentText': res})


def direct_feedback(email,message, ask_feedback = True):
        customer = Customer.filter_by(email=email).first()
        
        if customer:
            feed_dict = {'customer': customer,
                         'feedback': message, 'tag': 'customer'}
            feedback = Feedback(**feed_dict)
            feedback.save()
            res = 'Thank you for providing the feedback. You make us serve better.'
        else:
            res = 'I was unable to verify your email id. \
                       Please enter the correct email id.'
        if ask_feedback:
            directfeedback(res,'')

        return jsonify({'fulfillmentText': res})


def handle_refund(params, ask_feedback=False):
    res = "We did not find any order for your id. Please enter the correct id."
    ord_id = int(params.get('transaction-id'))
    order = db.session.query(Order).filter_by(id=ord_id).first()
    if order:
        order_item = OrderItems.filter_by(order=order).first()
        if order.status == 'Completed':
            res = choice(REFUND_ORDER_COMPLETED).format(order_item.product.title, order.status)
        if order.status == 'Approved' or order.status == 'Pending':
            res = choice(REFUND_ORDER_APPROVED_PENDING).format(order_item.product.title, order.status)
        if order.status == 'Voided':
            res = choice(REFUND_ORDER_VOIDED)
        res = res + ' Would you like to share experience to get us more better?'
        if ask_feedback:
            return feedback(res,'') 
    return jsonify({'fulfillmentText': res})

def solve_problem(params, complaints, ask_feedback = True):

    email = params.get('email')
    customer = Customer.filter_by(email=email).first()
    # complaints = result.get('outputContexts')[1].get('parameters').get('message')
    if customer:
        # res = 'We are happy to help you. I have raised a ticket for your issue.'
        ticket_dict = {'tag':'customer', 'customer':customer, 'complaints':complaints, 'status':"Active",}
        ticket = Ticket(**ticket_dict)
        ticket.save()
        res = 'We are happy to help you. I have raised a '+str(ticket.id)+' ticket for your issue. \
               Would you like to share experience to get us more better?'
    else:
        res = 'Please give the registered mail id.'
    if ask_feedback:
            return feedback(res,'')
    return jsonify({'fulfillments' : res})
        
def feedback(*args):
    parameters = {f"response_{i+1}":response for i, response in enumerate(args)}
    return jsonify(
        {'followupEventInput': {"name": "ask_feedback",
                                "parameters": parameters,
                                "lifespan": 1}
        })

def directfeedback(*args):
    parameters = {f"response_{i+1}":response for i, response in enumerate(args)}
    return jsonify(
        {'followupEventInput': {"name": "actions_intent_CANCEL",
                                "parameters": parameters,
                                "lifespan": 1}
        })

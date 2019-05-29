from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from settings import db

database_uri = 'mssql+pymssql://EComCSSA:3ComC22A@ecomcs.c390nx6k6ql6.us-east-1.rds.amazonaws.com:1433/EComCS'
engine = create_engine(database_uri)
metadata = MetaData()
metadata.reflect(engine)
Base = automap_base(metadata=metadata)
Base.prepare()

Customer = Base.classes.Customer
Order = Base.classes.Order
OrderItems = Base.classes.OrderItems
Ticket = Base.classes.Ticket
Feedback = Base.classes.Feedback
Product = Base.classes.Product

def save(self):
    db.session.add(self)
    db.session.commit()

def remove(self):
    db.session.delete(self)
    db.session.commit()
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


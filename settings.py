from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)                                  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://EComCSSA:3ComC22A@ecomcs.c390nx6k6ql6.us-east-1.rds.amazonaws.com:1433/EComCS'
db = SQLAlchemy(app)

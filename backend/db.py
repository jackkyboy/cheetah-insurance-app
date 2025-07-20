# /Users/apichet/Downloads/cheetah-insurance-app/backend/db.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index  # ✅ เพิ่มบรรทัดนี้

db = SQLAlchemy()

Model = db.Model
Column = db.Column
Integer = db.Integer
String = db.String
DateTime = db.DateTime
Date = db.Date
Time = db.Time
Boolean = db.Boolean
Float = db.Float
ForeignKey = db.ForeignKey
Text = db.Text
relationship = db.relationship
backref = db.backref     # ✅ เพิ่มบรรทัดนี้
func = db.func
JSON = db.JSON

__all__ = [
    "db", "Model", "Column", "Integer", "String", "DateTime", "Date", "Time",
    "Boolean", "Float", "ForeignKey", "Text", "relationship", "backref",
    "func", "JSON", "Index"  # ✅ เพิ่ม Index
]

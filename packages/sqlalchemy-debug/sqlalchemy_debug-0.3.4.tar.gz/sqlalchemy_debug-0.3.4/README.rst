==============================
SQLAlchemy ORM Debug Script
==============================

You can write code in your application::  

    from sqlalchemy_debug import debug_statement
    model = "your ORM Model"
    statement = session.query(...)
    debug_statement(statement)
    
    record = model.__table__.insert(...)
    debug_statement(record)

    debug_statement(model) # show create table statement
# !/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Company, CarType, User

engine = create_engine('sqlite:///carscompanieswithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Khalaf Alzwaid", email="ibnzwaid@gmail.com",
             picture=' ')
session.add(User1)
session.commit()

# Cars for Toyota
Company1 = Company(user_id=1, name="Toyota")

session.add(Company1)
session.commit()

CarType0 = CarType(
    user_id=1,
    name="Camry",
    description="""An automobile sold internationally
     by the Japanese manufacturer Toyota
     since 1982, spanning multiple generations.
    """,
    price="42000.25",
    company_id=1)

session.add(CarType0)
session.commit()


CarType1 = CarType(
    user_id=1,
    name="Corolla",
    description="""a line of subcompact and compact cars
     manufactured by Toyota. Introduced in 1966, the Corolla
     was the best-selling car worldwide by 1974 and has been
     one of the best-selling cars in the world since then.
    """,
    price="22000",
    company_id=1)

session.add(CarType1)
session.commit()

CarType2 = CarType(
    user_id=1,
    name="Land Cruiser",
    description="""a series of four-wheel drive vehicles
     produced by the Japanese automobile manufacturer Toyota.
     It is Toyota's longest running series of models.
    """,
    price="54000",
    company_id=1)

session.add(CarType2)
session.commit()

# Cars for Honda
Company2 = Company(user_id=1, name="Honda")

session.add(Company2)
session.commit()

CarType3 = CarType(
    user_id=1,
    name="Acura",
    description="""The brand was launched in the United States
     and Canada on 27 March 1986, marketing luxury, performance,
     and high-performance vehicles.
    """,
    price="17950",
    company_id=2)

session.add(CarType3)
session.commit()

CarType4 = CarType(
    user_id=1,
    name="Civic",
    description="""a line of cars manufactured by Honda.
     Originally a subcompact, the Civic has gone through
     several generational changes, becoming both larger and
     more upmarket and moving into the compact car segment.
    """,
    price="15000",
    company_id=2)

session.add(CarType4)
session.commit()

CarType5 = CarType(
    user_id=1,
    name="ATVs",
    description="""a high-performance ATC produced by Honda
     from 1981 to 1986. Early models (1981-1984) used an
     air-cooled, 248 cc single-cylinder two-stroke engine.
    """,
    price="13000",
    company_id=2)

session.add(CarType5)
session.commit()

# Cars for Chevrolet
Company3 = Company(user_id=1, name="Chevrolet")
session.add(Company3)
session.commit()

CarType6 = CarType(
    user_id=1,
    name="Camaro",
    description="""An American automobile manufactured by
     Chevrolet, classified as a pony car and some versions
     also as a muscle car.
    """,
    price="18569",
    company_id=3)

session.add(CarType6)
session.commit()

CarType7 = CarType(
    user_id=1,
    name="Corvette",
    description="""The Chevrolet Corvette, known also as the
     Vette or Chevy Corvette, is a front engine, rear drive,
     two-door, two-passenger sports car manufactured and marketed
     by Chevrolet across more than sixty years of production
     and seven design generations.
    """,
    price="21000",
    company_id=3)

session.add(CarType7)
session.commit()

CarType8 = CarType(
    user_id=1,
    name="Trucks",
    description="""Advance-Design was a truck series by Chevrolet,
     their first major redesign after WWII. It was billed as a larger,
     stronger, and sleeker design in comparison to the earlier AK Series.
    """,
    price="33200",
    company_id=3)
session.add(CarType8)
session.commit()


print "added menu items!"

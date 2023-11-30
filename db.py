import datetime
import logging
from typing import List

from sqlalchemy import String, Integer, Date, create_engine, ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

class HRDBBase(DeclarativeBase):
    pass

class Employee(HRDBBase):
    __tablename__ = "hrms_employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    fname: Mapped[str] =  mapped_column(String(50))
    lname: Mapped[str] =  mapped_column(String(50))
    email: Mapped[str] =  mapped_column(String(120))
    phone: Mapped[str] =  mapped_column(String(50))
    designation_id: Mapped[int] = mapped_column(ForeignKey('hrms_designations.id'))
    designation: Mapped["Designation"] = relationship(back_populates = "employees")

class Designation(HRDBBase):
    __tablename__ = "hrms_designations"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] =  mapped_column(String(100))
    max_leaves: Mapped[int] = mapped_column(Integer)
    employees: Mapped[List["Employee"]] = relationship(back_populates = "title")


def create_all(db_url):
    logger = logging.getLogger("VCARDGEN")
    engine = create_engine(db_url)
    HRDBBase.metadata.create_all(engine)
    logger.info("Intialised database and created table")

def get_session(db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind = engine)
    session = Session()
    return session
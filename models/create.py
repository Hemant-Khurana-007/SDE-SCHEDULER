from sqlalchemy import create_engine,Column,Integer,String,select,insert,ForeignKey,DateTime,Float,func,and_,update,delete
from sqlalchemy.orm import Session,declarative_base

Base = declarative_base()
class User(Base):
    __tablename__="user"
    id = Column(Integer , primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True,nullable=False)
    password = Column(String(30),nullable=False)
    fname = Column(String(30),nullable=False)
    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, password={self.password}, fname={self.fname})"
    

engine = create_engine("sqlite:///models/data.sqlite3")
Base.metadata.create_all(engine)
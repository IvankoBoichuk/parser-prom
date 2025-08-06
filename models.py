from sqlalchemy import Column, Integer, BigInteger, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Competitor(Base):
    __tablename__ = "competitors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    site_url = Column(String(100))

class CompetitorProduct(Base):
    __tablename__ = "competitors_products"
    id = Column(BigInteger, primary_key=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=True)
    name = Column(String(2048))
    category = Column(String(256))
    price = Column(Float)
    bought_count = Column(Integer)
    description = Column(Text)
    url = Column(String(2048))

class CompetitorReview(Base):
    __tablename__ = "competitors_reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("competitors_products.id"), nullable=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=True)
    review_average = Column(Float)
    review_text = Column(Text)
    author = Column(String(50))
    date = Column(DateTime)
    tags = Column(String(256))

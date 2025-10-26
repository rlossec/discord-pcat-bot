"""
Base SQLAlchemy commune à toutes les entités
"""
from sqlalchemy.ext.declarative import declarative_base

# Instance unique de declarative_base pour toutes les entités
Base = declarative_base()
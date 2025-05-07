
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey ,func
from sqlalchemy.orm import relationship

from datetime import datetime
from .base import Base 


class Resource(Base):
    """Stores information about the original content resources (books, movies, music)"""
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True ,nullable=False)
    title = Column(String,nullable=False)
    content_type = Column(String,nullable=False)  # 'movie', 'book', 'article', 'music'
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime)
    
    # Relationships
    files = relationship("ContentFile", back_populates="resource")
    links = relationship("DiscoveredLink", back_populates="resource")

class ContentFile(Base):
    """Stores direct links to downloadable content (mp4, pdf, mp3 etc.)"""
    __tablename__ = 'content_files'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True,nullable=False)
    file_type = Column(String ,nullable=False)
    file_size = Column(Integer,nullable=False)  # in bytes
    resource_id = Column(Integer, ForeignKey('resources.id'),nullable=False)
    image_src = Column(String)
    description = Column(String)
    # Relationships
    resource = relationship("Resource", back_populates="files")

class DiscoveredLink(Base):
    """Tracks discovered links that need to be explored"""
    __tablename__ = 'discovered_links'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True ,nullable=False)
    explored = Column(Boolean, default=False,nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'))
    
    # Relationships
    resource = relationship("Resource", back_populates="links")

    def __repr__(self):
        return f"<(url={self.url} ,num={self.id})"
    def __str__(self):
        return self.__repr__()
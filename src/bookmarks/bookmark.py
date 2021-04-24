from __future__ import annotations

from typing import Optional, Set

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from bookmarks._db import Base, ScopedSession


class Bookmark(Base):
    __tablename__ = 'bookmarks'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    comment = Column(String, nullable=False, index=True)

    _FIELDS = set(('id', 'url', 'title', 'comment'))
    _ID_FIELD = 'id'
    _REQUIRED_FIELDS = _FIELDS - set((_ID_FIELD,))
    
    def serialize(self) -> dict:
        return {
            field: getattr(self, field)
            for field in Bookmark._FIELDS
        }

    @staticmethod
    def deserialize(data: dict, fields: Set[str] = _FIELDS) -> Bookmark:
        data_keys = set(data.keys())
        allowed_keys = data_keys.intersection(fields)
        
        invalid_keys = data_keys - allowed_keys
        missing_keys = Bookmark._REQUIRED_FIELDS - allowed_keys
        
        errors = []
        if len(missing_keys) > 0:
            errors.append(f'missing fields: {list(missing_keys)}')
        if len(invalid_keys) > 0:
            errors.append(f'excess fields: {list(invalid_keys)}')
        
        if len(errors) > 0:
            raise ValueError(', '.join(errors))
        
        return Bookmark(**{key: data[key] for key in allowed_keys})

    @staticmethod
    def deserialize_without_id(data: dict) -> Bookmark:
        return Bookmark.deserialize(data, Bookmark._FIELDS - set((Bookmark._ID_FIELD,)))

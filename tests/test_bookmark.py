import pytest

from bookmarks.bookmark import Bookmark


class TestSerialize:
    def test_normal(self):
        b_id, b_url, b_title, b_comment = (
            1,
            'http://example.com',
            'Example title',
            'Example comment'
        )
        b = Bookmark(id=b_id, url=b_url, title=b_title, comment=b_comment)
        serialized = b.serialize()
        
        assert serialized['id'] == b_id
        assert serialized['url'] == b_url
        assert serialized['title'] == b_title
        assert serialized['comment'] == b_comment

    def test_empty(self):
        b = Bookmark(id=None, url='', title='', comment='')
        serialized = b.serialize()
        
        assert serialized['id'] is None
        assert serialized['url'] == ''
        assert serialized['title'] == ''
        assert serialized['comment'] == '' 

    def test_without_id(self):
        b_id, b_url, b_title, b_comment = (
            1,
            'http://example.com',
            'Example title',
            'Example comment'
        )
        b = Bookmark(id=b_id, url=b_url, title=b_title, comment=b_comment)
        serialized = b.serialize_without_id()
        
        assert serialized['url'] == b_url
        assert serialized['title'] == b_title
        assert serialized['comment'] == b_comment

        assert 'id' not in serialized


class TestDeserialize:
    def test_normal(self):
        b_id, b_url, b_title, b_comment = (
            1,
            'http://example.com',
            'Example title',
            'Example comment'
        )
                
        serialized = {
            'id': b_id,
            'url': b_url,
            'title': b_title,
            'comment': b_comment
        }
        b = Bookmark.deserialize(serialized)
        
        assert b.id == b_id
        assert b.url == b_url
        assert b.title == b_title
        assert b.comment == b_comment
            
    def test_id_not_required(self):
        b_url, b_title, b_comment = (
            'http://example.com',
            'Example title',
            'Example comment'
        )
                
        serialized = {
            'url': b_url,
            'title': b_title,
            'comment': b_comment
        }
        
        b = Bookmark.deserialize(serialized)
        
        assert b.id is None
        assert b.url == b_url
        assert b.title == b_title
        assert b.comment == b_comment
    
    def test_url_required(self):
        serialized = {
            'id': 1,
            'title': 'nop',
            'comment': 'nop'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize(serialized)
    
    def test_title_required(self):
        serialized = {
            'id': 1,
            'url': 'nop',
            'comment': 'nop'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize(serialized)
    
    def test_comment_required(self):
        serialized = {
            'id': 1,
            'title': 'nop',
            'url': 'nop'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize(serialized)
    
    def test_excess_field(self):
        serialized = {
            'id': 0,
            'url': 'nop',
            'title': 'nop',
            'comment': 'nop',
            'excess_field': 'value'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize(serialized)


class TestDeserializeIgnoreId:
    def test_normal(self):
        b_url, b_title, b_comment = (
            'http://example.com',
            'Example title',
            'Example comment'
        )
                
        serialized = {
            'url': b_url,
            'title': b_title,
            'comment': b_comment
        }
        b = Bookmark.deserialize_ignore_id(serialized)
        
        assert b.id is None
        assert b.url == b_url
        assert b.title == b_title
        assert b.comment == b_comment

    def test_id_ignore(self): 
        b_url, b_title, b_comment = (
            'http://example.com',
            'Example title',
            'Example comment'
        )   
        serialized = {
            'id': 16,
            'url': b_url,
            'title': b_title,
            'comment': b_comment
        }
        
        b = Bookmark.deserialize_ignore_id(serialized)
        
        assert b.id is None  # ID is idnored
        assert b.url == b_url
        assert b.title == b_title
        assert b.comment == b_comment
    

    def test_url_required(self):
        serialized = {
            'title': 'nop',
            'comment': 'nop'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize_ignore_id(serialized)
    
    def test_title_required(self):
        serialized = {
            'url': 'nop',
            'comment': 'nop'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize_ignore_id(serialized)
    
    def test_comment_required(self):
        serialized = {
            'title': 'nop',
            'url': 'nop'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize_ignore_id(serialized)
    
    def test_excess_field(self):
        serialized = {
            'url': 'nop',
            'title': 'nop',
            'comment': 'nop',
            'excess_field': 'value'
        }
        
        with pytest.raises(ValueError):
            b = Bookmark.deserialize_ignore_id(serialized)

import json
from http import HTTPStatus


from bookmarks.bookmark import Bookmark


class TestGet:        
    def test_empty_list(self, api, api_route):
        r = api.get(api_route('/bookmarks'))
        assert r.status_code == HTTPStatus.OK
        
        resp = json.loads(r.data)
        assert resp['status'] == 'success'
        assert isinstance(resp['data'], list)
        assert len(resp['data']) == 0
    
    def test_bookmark_404(self, api, api_route):
        r = api.get(api_route('/bookmarks/42'))
        assert r.status_code == HTTPStatus.NOT_FOUND
        
        resp = json.loads(r.data)
        assert resp['status'] == 'error'
    
    def test_bookmark_get(self, api, api_route, add_bookmark):
        b_id, b_url, b_title, b_comment = (
            1,
            'http://example.com',
            'Example title',
            'Example comment'
        )
        b = Bookmark(id=b_id, url=b_url, title=b_title, comment=b_comment)
        add_bookmark(b)
        
        r = api.get(api_route(f'/bookmarks/{b_id}'))
        assert r.status_code == HTTPStatus.OK
        
        resp = json.loads(r.data)
        assert resp['status'] == 'success'
        assert isinstance(resp['data'], dict)
        
        deserialized = Bookmark.deserialize(resp['data'])
        
        assert deserialized.id == b_id
        assert deserialized.url == b_url
        assert deserialized.title == b_title
        assert deserialized.comment == b_comment

    def test_bookmarks_list(self, api, api_route, add_bookmark):
        BOOKMARKS_COUNT = 5
        bookmarks = [
            Bookmark(id=num, url=f'test url {num}', title=f'test title {num}', comment=f'test comment {num}')
            for num
            in range(BOOKMARKS_COUNT)
        ]
        
        for b in bookmarks:
            add_bookmark(b)
        
        r = api.get(api_route(f'/bookmarks'))
        assert r.status_code == HTTPStatus.OK
        
        resp = json.loads(r.data)
        assert resp['status'] == 'success'
        assert isinstance(resp['data'], list)
        
        bookmarks_deserialized = [Bookmark.deserialize(b) for b in resp['data']]
        returned_ids = set()
        for b in bookmarks_deserialized:
            assert b.id >= 0 and b.id < BOOKMARKS_COUNT
            assert b.url == f'test url {b.id}'
            assert b.title == f'test title {b.id}'
            assert b.comment == f'test comment {b.id}'
            returned_ids.add(b.id)
        assert len(returned_ids) == BOOKMARKS_COUNT


class TestPost:
    def test_post_multiple(self, api, api_route, get_all_bookmarks):
        BOOKMARKS_COUNT = 5
        bookmarks = [
            Bookmark(url=f'test url {num}', title=f'test title {num}', comment=f'test comment {num}')
            for num
            in range(BOOKMARKS_COUNT)
        ]
        
        for idx, b in enumerate(bookmarks):
            r = api.post(api_route(f'/bookmarks'), json=b.serialize_without_id())
            assert r.status_code == HTTPStatus.CREATED
            
            resp = json.loads(r.data)
            assert resp['status'] == 'success'
            assert isinstance(resp['data'], dict)
            
            returned_bookmark = Bookmark.deserialize(resp['data'])
            assert returned_bookmark.id is not None
            assert returned_bookmark.url == f'test url {idx}'
            assert returned_bookmark.title == f'test title {idx}'
            assert returned_bookmark.comment == f'test comment {idx}'

        all_bookmarks = get_all_bookmarks()
        assert len(all_bookmarks) == BOOKMARKS_COUNT
        
        saved_ids = set()
        for idx, b in enumerate(sorted(all_bookmarks, key=lambda b: b.id)):
            assert b.id is not None
            assert b.url == f'test url {idx}'
            assert b.title == f'test title {idx}'
            assert b.comment == f'test comment {idx}'
            saved_ids.add(idx)
        
        assert len(saved_ids) == BOOKMARKS_COUNT

    def test_id_ignored(self, api, api_route, add_bookmark):
        EXISTING_ID = 42
        # Make sure the newly added bookmark's id would not == EXISTING_ID
        add_bookmark(Bookmark(id=EXISTING_ID, url='nop', title='nop', comment='nop'))
        
        b = Bookmark(id=EXISTING_ID, url='test url', title='test title', comment='test comment')
        
        r = api.post(api_route('/bookmarks'), json=b.serialize())
        assert r.status_code == HTTPStatus.CREATED
        
        resp = json.loads(r.data)
        assert resp['status'] == 'success'
        assert isinstance(resp['data'], dict)
        
        deserialized = Bookmark.deserialize(resp['data'])
        assert deserialized.id != EXISTING_ID
        assert deserialized.url == b.url
        assert deserialized.title == b.title
        assert deserialized.comment == b.comment
    

class TestPut:
    def test_update_single(self, api, api_route, add_bookmark, get_all_bookmarks, db_session):
        b_id, b_url, b_title, b_comment = (
            1,
            'http://example.com',
            'Example title',
            'Example comment'
        )
        b = Bookmark(id=b_id, url=b_url, title=b_title, comment=b_comment)
        add_bookmark(b)
        
        new_bookmark = Bookmark(
            id=b.id,
            url=b.url,
            title=b.title,
            comment=b.comment
        )
        
        r = api.put(api_route(f'/bookmarks/{b.id}'), json=new_bookmark.serialize_without_id())
        assert r.status_code == HTTPStatus.OK
        
        resp = json.loads(r.data)
        assert resp['status'] == 'success'
        assert isinstance(resp['data'], dict)
        
        returned_bookmark = Bookmark.deserialize(resp['data'])
        
        assert returned_bookmark.id == new_bookmark.id
        assert returned_bookmark.url == new_bookmark.url
        assert returned_bookmark.title == new_bookmark.title
        assert returned_bookmark.comment == new_bookmark.comment


class TestDelete:
    def test_delete_single(self, api, api_route, add_bookmark, get_all_bookmarks):
        b_id, b_url, b_title, b_comment = (
            1,
            'http://example.com',
            'Example title',
            'Example comment'
        )
        b = Bookmark(id=b_id, url=b_url, title=b_title, comment=b_comment)
        add_bookmark(b)
        
        r = api.delete(api_route(f'/bookmarks/{b.id}'))
        assert r.status_code == HTTPStatus.OK
        
        resp = json.loads(r.data)
        assert resp['status'] == 'success'
        
        all_bookmarks = get_all_bookmarks()
        assert len(all_bookmarks) == 0

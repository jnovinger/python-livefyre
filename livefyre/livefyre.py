# -*- coding: utf-8 -*-

import hashlib
import json
import urlparse

import jwt
import requests


DEFAULT_LIVEFYRE_NETWORK = 'dailydot'
DEFAULT_LIVEFYRE_SITE_ID = 123456
DEFAULT_LIVEFYRE_SITE_SECRET = 'sekret'


LIVEFYRE_API_BASE = 'http://quill.{network}.fyre.co/api/v3.0/site/{site_id}'


def jwt_encode(payload, secret):
    """Uses SHA-256 per Livefyre doc specs"""
    return jwt.encode(payload, secret, "HS256")

class Livefyre(object):
    """A Livefyre v3 API client."""

    ENDPOINTS = {
        'COLLECTIONS': {
            '_base': 'collection',
            'create': 'create',
        }
    }

    def __init__(self, network=None, site_id=None, site_secret=None):
        super(Livefyre, self).__init__()

        self.network = network or DEFAULT_LIVEFYRE_NETWORK
        self.site_id = site_id or DEFAULT_LIVEFYRE_SITE_ID
        self.site_secret = site_secret or DEFAULT_LIVEFYRE_SITE_SECRET

        self.api = LIVEFYRE_API_BASE.format(network=self.network,
                                            site_id=self.site_id)
        self.session = requests.session()

    def create_collection(self, title, url, article_id, stream_type, tags):
        collection = Collection(
            title, url, article_id, stream_type, tags, self.site_secret)
        response = self.send_data(
            endpoint='/collection/create',
            payload=collection.payload()
        )

        return collection, response

    def send_data(self, endpoint, payload):

        url = '{}{}'.format(self.api, endpoint)
        return self.session.post(url, data=payload)


class Collection(object):
    """Represents a Livefyre StreamHub Collection"""

    TYPES = ['livecomments', 'liveblog', 'livechat']

    def __init__(self,
            title,
            url,
            article_id,
            stream_type='livecomments',
            tags=None,
            site_secret=None):

        assert title, 'title may not be empty.'
        assert article_id, 'article_id may not be empty'

        _url = urlparse.urlparse(url)
        assert 'http' in _url.scheme, 'The URL must be a fully qualified url whose scheme is either "http" or "https".'

        assert stream_type in self.TYPES, 'stream_type must be one of {}'.format(self.TYPES)

        _collection = {
            'title': title if len(title) < 256 else title[:255],
            'url': url,
            'article_id': article_id if len(article_id) < 256 else article_id[:255],
            'stream_type': stream_type,
            'tags': self._tagify(tags),
        }
        self.collection = _collection
        self.site_secret = site_secret

    def _tagify(self, tags):
        if tags:
            return tags.split(',')
        return []

    def meta(self):
        return jwt_encode(self.collection, self.site_secret)

    def checksum(self):
        hash_ = hashlib.md5()
        hash_.update(self.meta())
        return hash_.hexdigest()

    def payload(self):
        payload_ = json.dumps({
            'collectionMeta': self.meta(),
            'type': self.collection['stream_type'],
            'checksum': self.checksum(),
        })
        return payload_

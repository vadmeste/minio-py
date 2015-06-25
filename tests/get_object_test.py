# Minimal Object Storage Library, (C) 2015 Minio, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unittest import TestCase

import mock
from nose.tools import raises

from minio import minio
from minio.exceptions import InvalidBucketNameException
from minio.parsers import ResponseError
from .minio_mocks import MockResponse
from .helpers import generate_error

__author__ = 'minio'


class GetObjectTest(TestCase):
    @raises(TypeError)
    def test_bucket_is_string(self):
        client = minio.Minio('http://localhost:9000')
        client.get_object(1234, 'world')

    @raises(ValueError)
    def test_bucket_is_not_empty_string(self):
        client = minio.Minio('http://localhost:9000')
        client.get_object('  \t \n  ', 'world')

    @raises(TypeError)
    def test_object_is_string(self):
        client = minio.Minio('http://localhost:9000')
        client.get_object('hello', 1234)

    @raises(ValueError)
    def test_object_is_not_empty_string(self):
        client = minio.Minio('http://localhost:9000')
        client.get_object('hello', ' \t \n ')

    @mock.patch('requests.get')
    def test_get_object_works(self, mock_request):
        mock_request.return_value = MockResponse('GET', 'http://localhost:9000/hello', {}, 200, content='hello world')
        client = minio.Minio('http://localhost:9000')
        object_iter = client.get_object('hello', 'world')
        actual_object = []
        for object_chunk in object_iter:
            actual_object.append(object_chunk)

    @mock.patch('requests.get')
    @raises(InvalidBucketNameException)
    def test_get_object_invalid_name(self, mock_request):
        mock_request.return_value = MockResponse('GET', 'http://localhost:9000/hello', {}, 400)
        client = minio.Minio('http://localhost:9000')
        client.get_object('1234', 'world')

    @mock.patch('requests.get')
    @raises(ResponseError)
    def test_get_object_invalid_name(self, mock_request):
        error_xml = generate_error('code', 'message', 'request_id', 'host_id', 'resource')
        mock_request.return_value = MockResponse('GET', 'http://localhost:9000/hello', {}, 400, content=error_xml)
        client = minio.Minio('http://localhost:9000')
        client.get_object('hello', 'world')


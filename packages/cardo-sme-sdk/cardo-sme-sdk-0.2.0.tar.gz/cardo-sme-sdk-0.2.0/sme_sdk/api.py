from functools import cached_property
from http import HTTPStatus
from urllib import parse

import requests

from sme_sdk.blob import BlobStorageClient
from sme_sdk.config import APIConfig
from sme_sdk.exceptions import BatchCreationFailed, BatchResultRetrieveFailed
from sme_sdk.types import BatchResultID
from sme_sdk.urls import Url


class APIClient:
    FILE_URL_NAME = 'file_url'

    def __init__(self, api_config: APIConfig):
        self.api_config = api_config

    def _form_url(self, partial_url) -> str:
        return parse.urljoin(self.api_config.host, partial_url)

    @cached_property
    def _headers(self):
        return {
            'Authorization': f'{self.api_config.api_key}',
        }

    def create_new_batch(self, data, blob_storage_client: BlobStorageClient) -> BatchResultID:
        file_url = blob_storage_client.save_data(data)
        response = requests.post(
            url=self._form_url(Url.batch_result.value),
            json={self.FILE_URL_NAME: file_url},
            headers=self._headers
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            raise BatchCreationFailed(response.text, response.status_code)

    def get_batch_result(self, batch_id: BatchResultID):
        response = requests.get(
            url=f'{self._form_url(Url.batch_result.value)}/{batch_id}',
            headers=self._headers
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            raise BatchResultRetrieveFailed(response.text, response.status_code)

from http import HTTPStatus
from typing import Union, Dict, Optional

import aiohttp

from daemon.clients.peas import AsyncPeaClient
from daemon.clients.mixin import AsyncToSyncMixin
from daemon.helper import if_alive, error_msg_from
from daemon.models.id import DaemonID, daemonize


class AsyncPodClient(AsyncPeaClient):
    """Async Client to create/update/delete Peods on remote JinaD"""

    _kind = 'pod'
    _endpoint = '/pods'

    @if_alive
    async def rolling_update(
        self,
        id: Union[str, 'DaemonID'],
        uses_with: Optional[Dict] = None,
    ) -> str:
        """Update a Flow on remote JinaD (only rolling_update supported)

        :param id: Pod ID
        :param uses_with: the uses_with to update the Executor
        :return: Pod ID
        """
        async with aiohttp.request(
            method='PUT',
            url=f'{self.store_api}/rolling_update/{daemonize(id, self._kind)}',
            json=uses_with,
            timeout=self.timeout,
        ) as response:
            response_json = await response.json()
            if response.status != HTTPStatus.OK:
                error_msg = error_msg_from(response_json)
                self._logger.error(
                    f'{self._kind.title()} update failed as: {error_msg}'
                )
                return error_msg
            return response_json

    @if_alive
    async def scale(self, id: Union[str, 'DaemonID'], replicas: int) -> str:
        """Scale a remote Pod

        :param id: Pod ID
        :param replicas: The number of replicas to scale to
        :return: Pod ID
        """
        async with aiohttp.request(
            method='PUT',
            url=f'{self.store_api}/scale/{daemonize(id, self._kind)}',
            params={'replicas': replicas},
            timeout=self.timeout,
        ) as response:
            response_json = await response.json()
            if response.status != HTTPStatus.OK:
                error_msg = error_msg_from(response_json)
                self._logger.error(
                    f'{self._kind.title()} update failed as: {error_msg}'
                )
                return error_msg
            return response_json


class PodClient(AsyncToSyncMixin, AsyncPodClient):
    """Client to create/update/delete Pods on remote JinaD"""

from typing import TypeVar, Union

from interactions.api.models.misc import MISSING
from interactions.client.bot import Client as _Client

from .dummy import AutoShardedClient, DummyClient

__all__ = ("shard",)

Client = TypeVar("Client", bound=_Client)


async def _get_shard_count(client: Client) -> int:
    data = await client._http.get_bot_gateway()
    return data[0]


def generate_shard_list(shard_count: int) -> list:
    """
    Generates a list of shards.
    """
    return [[shard, shard_count] for shard in range(shard_count)]


def shard(
    _client: _Client, shard_count: int = MISSING, max_shard_count: int = MISSING
) -> Union[Client, AutoShardedClient]:
    # sourcery skip: compare-via-equals
    _replacer = AutoShardedClient(intents=_client._intents, token=_client._token)

    if shard_count and shard_count != MISSING and isinstance(shard_count, int):
        _shard_count = shard_count
    else:
        _shard_count = _client._loop.run_until_complete(_get_shard_count(_client))

    if (
        max_shard_count is not MISSING
        and isinstance(max_shard_count, int)
        and _shard_count > max_shard_count
    ):
        _shard_count = max_shard_count

    shards = generate_shard_list(_shard_count)

    _client._shard = shards[0]

    _client._loop.run_until_complete(
        _client._Client__register_name_autocomplete()
    )  # ensure everything is registered

    _clients = []

    for shard in shards[1:]:
        __client = DummyClient(
            _client._token, shards=shard, intents=_client._intents, presence=_client._presence
        )
        _clients.append(__client)
    _replacer._clients = _clients
    _replacer._websocket._dispatch.events = _client._websocket._dispatch.events
    _replacer._Client__command_coroutines = _client._Client__command_coroutines
    _replacer._Client__name_autocomplete = _client._Client__name_autocomplete
    setattr(_client, "_clients", _clients)
    setattr(_client, "start", _replacer.start)
    setattr(_client, "_ready", _replacer._ready)
    setattr(_client, "_Client__ready", _replacer._AutoShardedClient__ready)
    setattr(_client, "_Client__login", _replacer._AutoShardedClient__login)
    setattr(_client, "remove", _replacer.remove)
    setattr(_client, "total_latency", _replacer.total_latency)
    setattr(_client, "run_gathered", _replacer.run_gathered)
    setattr(_client, "load", _replacer.load)

    return _client

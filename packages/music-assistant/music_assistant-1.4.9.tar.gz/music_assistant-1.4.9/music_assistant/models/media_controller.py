"""Model for a base media_controller."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from time import time
from typing import (
    TYPE_CHECKING,
    AsyncGenerator,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from databases import Database as Db

from music_assistant.models.errors import MediaNotFoundError, ProviderUnavailableError
from music_assistant.models.event import MassEvent

from .enums import EventType, MediaType, ProviderType
from .media_items import MediaItemType, media_from_dict

if TYPE_CHECKING:
    from music_assistant.mass import MusicAssistant

ItemCls = TypeVar("ItemCls", bound="MediaControllerBase")

REFRESH_INTERVAL = 60 * 60 * 24 * 30


class MediaControllerBase(Generic[ItemCls], metaclass=ABCMeta):
    """Base model for controller managing a MediaType."""

    media_type: MediaType
    item_cls: MediaItemType
    db_table: str

    def __init__(self, mass: MusicAssistant):
        """Initialize class."""
        self.mass = mass
        self.logger = mass.logger.getChild(f"music.{self.media_type.value}")

    @abstractmethod
    async def add(self, item: ItemCls) -> ItemCls:
        """Add item to local db and return the database item."""
        raise NotImplementedError

    @abstractmethod
    async def add_db_item(
        self, item: ItemCls, overwrite_existing: bool = False, db: Optional[Db] = None
    ) -> ItemCls:
        """Add a new record for this mediatype to the database."""
        raise NotImplementedError

    @abstractmethod
    async def update_db_item(
        self,
        item_id: int,
        item: ItemCls,
        overwrite: bool = False,
        db: Optional[Db] = None,
    ) -> ItemCls:
        """Update record in the database, merging data."""
        raise NotImplementedError

    async def library(self, limit: int = 500, offset: int = 0) -> List[ItemCls]:
        """Get all in-library items."""
        match = {"in_library": True}
        return [
            self.item_cls.from_db_row(db_row)
            for db_row in await self.mass.database.get_rows(
                self.db_table, match, order_by="name", limit=limit, offset=offset
            )
        ]

    async def count(self) -> int:
        """Return number of in-library items for this MediaType."""
        return await self.mass.database.get_count(self.db_table, {"in_library": 1})

    async def get(
        self,
        provider_item_id: str,
        provider: Optional[ProviderType] = None,
        provider_id: Optional[str] = None,
        force_refresh: bool = False,
        lazy: bool = True,
        details: ItemCls = None,
    ) -> ItemCls:
        """Return (full) details for a single media item."""
        assert provider or provider_id, "provider or provider_id must be supplied"
        if isinstance(provider, str):
            provider = ProviderType(provider)
        db_item = await self.get_db_item_by_prov_id(
            provider_item_id=provider_item_id,
            provider=provider,
            provider_id=provider_id,
        )
        if db_item and (time() - db_item.last_refresh) > REFRESH_INTERVAL:
            # it's been too long since the full metadata was last retrieved (or never at all)
            force_refresh = True
        if db_item and force_refresh:
            # get (first) provider item id belonging to this db item
            provider_id, provider_item_id = await self.get_provider_id(db_item)
        elif db_item:
            # we have a db item and no refreshing is needed, return the results!
            return db_item
        if not details and provider_id:
            # no details provider nor in db, fetch them from the provider
            details = await self.get_provider_item(provider_item_id, provider_id)
        if not details and provider:
            # check providers for given provider type one by one
            for prov in self.mass.music.providers:
                if not prov.available:
                    continue
                if prov.type == provider:
                    try:
                        details = await self.get_provider_item(
                            provider_item_id, prov.id
                        )
                    except MediaNotFoundError:
                        pass
                    else:
                        break
        if not details:
            # we couldn't get a match from any of the providers, raise error
            raise MediaNotFoundError(
                f"Item not found: {provider.value or provider_id}/{provider_item_id}"
            )
        # create job to add the item to the db, including matching metadata etc. takes some time
        # in 99% of the cases we just return lazy because we want the details as fast as possible
        # only if we really need to wait for the result (e.g. to prevent race conditions), we
        # can set lazy to false and we await to job to complete.
        add_job = self.mass.add_job(self.add(details), f"Add {details.uri} to database")
        if not lazy:
            await add_job.wait()
            return add_job.result

        return db_item if db_item else details

    async def search(
        self,
        search_query: str,
        provider: Optional[ProviderType] = None,
        provider_id: Optional[str] = None,
        limit: int = 25,
    ) -> List[ItemCls]:
        """Search database or provider with given query."""
        # create safe search string
        search_query = search_query.replace("/", " ").replace("'", "")
        if provider == ProviderType.DATABASE or provider_id == "database":
            return [
                self.item_cls.from_db_row(db_row)
                for db_row in await self.mass.database.search(
                    self.db_table, search_query
                )
            ]

        prov = self.mass.music.get_provider(provider_id or provider)
        if not prov:
            return {}

        # prefer cache items (if any)
        cache_key = (
            f"{prov.type.value}.search.{self.media_type.value}.{search_query}.{limit}"
        )
        if cache := await self.mass.cache.get(cache_key):
            return [media_from_dict(x) for x in cache]
        # no items in cache - get listing from provider
        items = await prov.search(
            search_query,
            [self.media_type],
            limit,
        )
        # store (serializable items) in cache
        self.mass.create_task(
            self.mass.cache.set(
                cache_key, [x.to_dict() for x in items], expiration=86400 * 7
            )
        )
        return items

    async def add_to_library(
        self,
        provider_item_id: str,
        provider: Optional[ProviderType] = None,
        provider_id: Optional[str] = None,
    ) -> None:
        """Add an item to the library."""
        # make sure we have a valid full item
        # note that we set 'lazy' to False because we need a full db item
        db_item = await self.get(
            provider_item_id, provider=provider, provider_id=provider_id, lazy=False
        )
        # add to provider libraries
        for prov_id in db_item.provider_ids:
            if prov := self.mass.music.get_provider(prov_id.prov_id):
                await prov.library_add(prov_id.item_id, self.media_type)
        # mark as library item in internal db
        if not db_item.in_library:
            db_item.in_library = True
            await self.set_db_library(db_item.item_id, True)
            self.mass.signal_event(
                MassEvent(
                    EventType.MEDIA_ITEM_UPDATED, object_id=db_item.uri, data=db_item
                )
            )

    async def remove_from_library(
        self,
        provider_item_id: str,
        provider: Optional[ProviderType] = None,
        provider_id: Optional[str] = None,
    ) -> None:
        """Remove item from the library."""
        # make sure we have a valid full item
        # note that we set 'lazy' to False because we need a full db item
        db_item = await self.get(
            provider_item_id, provider=provider, provider_id=provider_id, lazy=False
        )
        # remove from provider's libraries
        for prov_id in db_item.provider_ids:
            if prov := self.mass.music.get_provider(prov_id.prov_id):
                await prov.library_remove(prov_id.item_id, self.media_type)
        # unmark as library item in internal db
        if db_item.in_library:
            db_item.in_library = False
            await self.set_db_library(db_item.item_id, False)
            self.mass.signal_event(
                MassEvent(
                    EventType.MEDIA_ITEM_UPDATED, object_id=db_item.uri, data=db_item
                )
            )

    async def get_provider_id(
        self, item: ItemCls, db: Optional[Db] = None
    ) -> Tuple[str, str]:
        """Return provider and item id."""
        if item.provider == ProviderType.DATABASE:
            # make sure we have a full object
            item = await self.get_db_item(item.item_id, db=db)
        for prov in item.provider_ids:
            # returns the first provider that is available
            if not prov.available:
                continue
            if self.mass.music.get_provider(prov.prov_id):
                return (prov.prov_id, prov.item_id)
        return None, None

    async def get_db_items(
        self,
        query: Optional[str] = None,
        query_params: Optional[dict] = None,
        limit: int = 500,
        offset: int = 0,
        db: Optional[Db] = None,
    ) -> List[ItemCls]:
        """Fetch all records from database."""
        if query is not None:
            func = self.mass.database.get_rows_from_query(
                query, query_params, limit=limit, offset=offset, db=db
            )
        else:
            func = self.mass.database.get_rows(
                self.db_table, limit=limit, offset=offset, db=db
            )
        return [self.item_cls.from_db_row(db_row) for db_row in await func]

    async def get_db_item(self, item_id: int, db: Optional[Db] = None) -> ItemCls:
        """Get record by id."""
        match = {"item_id": int(item_id)}
        if db_row := await self.mass.database.get_row(self.db_table, match, db=db):
            return self.item_cls.from_db_row(db_row)
        return None

    async def get_db_item_by_prov_id(
        self,
        provider_item_id: str,
        provider: Optional[ProviderType] = None,
        provider_id: Optional[str] = None,
        db: Optional[Db] = None,
    ) -> ItemCls | None:
        """Get the database item for the given prov_id."""
        assert provider or provider_id, "provider or provider_id must be supplied"
        if isinstance(provider, str):
            provider = ProviderType(provider)
        if provider == ProviderType.DATABASE or provider_id == "database":
            return await self.get_db_item(provider_item_id, db=db)
        for item in await self.get_db_items_by_prov_id(
            provider=provider,
            provider_id=provider_id,
            provider_item_ids=(provider_item_id,),
            db=db,
        ):
            return item
        return None

    async def get_db_items_by_prov_id(
        self,
        provider: Optional[ProviderType] = None,
        provider_id: Optional[str] = None,
        provider_item_ids: Optional[Tuple[str]] = None,
        limit: int = 500,
        offset: int = 0,
        db: Optional[Db] = None,
    ) -> List[ItemCls]:
        """Fetch all records from database for given provider."""
        assert provider or provider_id, "provider or provider_id must be supplied"
        if isinstance(provider, str):
            provider = ProviderType(provider)
        if provider == ProviderType.DATABASE or provider_id == "database":
            return await self.get_db_items(limit=limit, offset=offset, db=db)

        query = f"SELECT * FROM {self.db_table}, json_each(provider_ids)"
        if provider_id is not None:
            query += (
                f" WHERE json_extract(json_each.value, '$.prov_id') = '{provider_id}'"
            )
        elif provider is not None:
            query += f" WHERE json_extract(json_each.value, '$.prov_type') = '{provider.value}'"
        if provider_item_ids is not None:
            prov_ids = str(tuple(provider_item_ids))
            if prov_ids.endswith(",)"):
                prov_ids = prov_ids.replace(",)", ")")
            query += f" AND json_extract(json_each.value, '$.item_id') in {prov_ids}"

        return await self.get_db_items(query, limit=limit, offset=offset, db=db)

    async def iterate_db_items(
        self,
        db: Optional[Db] = None,
    ) -> AsyncGenerator[ItemCls, None]:
        """Iterate all records from database."""
        async for db_row in self.mass.database.iterate_rows(self.db_table, db=db):
            yield self.item_cls.from_db_row(db_row)

    async def set_db_library(
        self, item_id: int, in_library: bool, db: Optional[Db] = None
    ) -> None:
        """Set the in-library bool on a database item."""
        match = {"item_id": item_id}
        await self.mass.database.update(
            self.db_table, match, {"in_library": in_library}, db=db
        )

    async def get_provider_item(
        self,
        item_id: str,
        provider_id: str,
    ) -> ItemCls:
        """Return item details for the given provider item id."""
        if provider_id == "database":
            item = await self.get_db_item(item_id)
        else:
            provider = self.mass.music.get_provider(provider_id)
            if not provider:
                raise ProviderUnavailableError(
                    f"Provider {provider_id} is not available!"
                )
            item = await provider.get_item(self.media_type, item_id)
        if not item:
            raise MediaNotFoundError(
                f"{self.media_type.value} {item_id} not found on provider {provider.name}"
            )
        return item

    async def remove_prov_mapping(
        self, item_id: int, prov_id: str, db: Optional[Db] = None
    ) -> None:
        """Remove provider id(s) from item."""
        async with self.mass.database.get_db(db) as db:
            if db_item := await self.get_db_item(item_id, db=db):
                db_item.provider_ids = {
                    x for x in db_item.provider_ids if x.prov_id != prov_id
                }
                if not db_item.provider_ids:
                    # item has no more provider_ids left, it is completely deleted
                    await self.delete_db_item(db_item.item_id)
                    return
                await self.update_db_item(
                    db_item.item_id, db_item, overwrite=True, db=db
                )

        self.logger.debug("removed provider %s from item id %s", prov_id, item_id)

    async def delete_db_item(self, item_id: int, db: Optional[Db] = None) -> None:
        """Delete record from the database."""
        async with self.mass.database.get_db(db) as db:

            # delete item
            await self.mass.database.delete(
                self.db_table,
                {"item_id": int(item_id)},
                db=db,
            )
        # NOTE: this does not delete any references to this item in other records!
        self.logger.debug("deleted item with id %s from database", item_id)

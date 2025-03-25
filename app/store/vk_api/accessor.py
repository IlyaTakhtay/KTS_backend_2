import random
import typing
import aiohttp
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateMessage, UpdateObject
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.session = aiohttp.ClientSession()
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        query = self._build_query(
            host="https://api.vk.com/method/",
            method='groups.getLongPollServer',
            params={
                'manage': self.app.config.bot.group_id,
                'access_token': self.app.config.bot.token
            }
        )
        async with self.session.get(query) as resp:
            data = (await resp.json())["response"]
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]

        async def poll(self):
            query = self._build_query(
                host=self.server, method='', params={
                    'act': 'a_check',
                    'key': self.key,
                    'ts': self.ts,
                    'wait': 25
                }
            )
        async with self.session.get(query) as resp:
            data = await resp.json()
            self.ts = data["ts"]
            raw_updates = data.get("updates", [])
            updates = []
            for update in raw_updates:
                updates.append(
                    Update(
                        type=update["type"],
                        object=UpdateObject(
                            message=UpdateMessage(
                                from_id=update["object"]["user_id"],
                                text=update["object"]["body"],
                                id=update["object"]["id"],
                            )
                        ),
                    )
                )
            await self.app.store.bots_manager.handle_updates(updates)

    async def send_message(self, message: Message) -> None:
        query = self._build_query(
                    host="https://api.vk.com/method/",
                    method="messages.send",
                    params={
                        "user_id": message.user_id,
                        "random_id": random.randint(1, 2 ** 32),
                        "peer_id": "-" + str(self.app.config.bot.group_id),
                        "message": message.text,
                        "access_token": self.app.config.bot.token,
                    },
                )
        async with self.session.get(query) as resp:
            data = await resp.json()
            self.logger.info(data)

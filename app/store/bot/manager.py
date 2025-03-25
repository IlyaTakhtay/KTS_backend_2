import typing

from app.store.vk_api.dataclasses import Message, Update, UpdateMessage, UpdateObject

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            update_object: UpdateObject = update.object
            message: UpdateMessage = update_object.message
            from_id: int = message.from_id
            await self.app.store.vk_api.send_message(
                Message(user_id=from_id, text='Oh, hi Mark')
            )

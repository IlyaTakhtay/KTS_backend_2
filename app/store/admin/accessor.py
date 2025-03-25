import typing
import uuid
from hashlib import sha256

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        # TODO: создать админа по данным в config.yml здесь
        admin_email = app.config.admin.email
        admin_password = app.config.admin.password
        admin = Admin(
            id=1,
            email=admin_email,
            password = sha256(admin_password.encode("utf-8")).hexdigest()
        )
        app.database.admins.append(admin)

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = Admin(
            1,
            email=email,
            password = sha256(password.encode("utf-8")).hexdigest()
            )
        return admin

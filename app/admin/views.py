from hashlib import sha256
from aiohttp_apispec import request_schema, response_schema
from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp_session import new_session

from app.admin.models import Admin
from app.admin.schemes import AdminRequestSchema, AdminResponseSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

# Тут сделать вюхи для создания логинки в админку
class AdminLoginView(View):
    @request_schema(AdminRequestSchema)
    @response_schema(AdminResponseSchema, 200)
    async def post(self):
        data = await self.request.json()
        hashed_password = sha256(data['password'].encode('utf-8')).hexdigest()
        admin: Admin | None = await self.store.admins.get_by_email(email=data['email'])

        if admin is None or admin.password != hashed_password:
            raise HTTPForbidden

        session = await new_session(request=self.request)
        session['email'] = admin.email
        session['password'] = admin.password

        return json_response(data=AdminResponseSchema().dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminResponseSchema, 200)
    async def get(self):
        admin = await self.check_auth(request=self.request)
        return json_response(data=AdminResponseSchema().dump(admin))
        

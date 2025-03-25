from aiohttp_apispec import response_schema, request_schema
from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound

from app.quiz.models import Question, Theme
from app.quiz.schemes import QuestionListSchema, QuestionRequestSchema, QuestionResponseSchema, ThemeListSchema, ThemeRequestSchema, ThemeResponseSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(AuthRequiredMixin, View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    @request_schema(ThemeRequestSchema)
    @response_schema(ThemeResponseSchema, 200)
    async def post(self):
        await self.check_auth(request=self.request)
        title = self.data['title']
        theme: Theme|None = await self.store.quizzes.get_theme_by_title(title=title)
        # TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        if theme is not None:
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeResponseSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema, 200)
    async def get(self):
        await self.check_auth(request=self.request)
        themes: list[Theme] = await self.store.quizzes.list_themes()
        return json_response(ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionRequestSchema)
    @response_schema(QuestionResponseSchema, 200)
    async def post(self):
        await self.check_auth(request=self.request)
        title: str = self.data['title']
        theme_id: int = self.data['theme_id']
        if await self.store.quizzes.get_theme_by_id(id_=theme_id) is None:
            raise HTTPNotFound
        answers: list[str] = self.data['answers']
        good_answers: list[str] = list(filter(lambda a: a.get('is_correct'), answers))
        if len(answers) < 2 or len(good_answers) != 1:
            raise HTTPBadRequest
        question: Question | None = await self.store.quizzes.get_question_by_title(title=title)
        if question is not None:
            raise HTTPConflict
        
        question = await self.store.quizzes.create_question(
            title=title, theme_id=theme_id, answers=answers
        )
        print(question)
        return json_response(data=QuestionResponseSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @response_schema(QuestionListSchema, 200)
    async def get(self):
        await self.check_auth(request=self.request)
        questions = await self.store.quizzes.list_questions()
        return json_response(data=QuestionListSchema().dump({"questions": questions}))

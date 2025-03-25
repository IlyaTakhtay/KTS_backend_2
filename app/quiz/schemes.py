from marshmallow import Schema, fields


class ThemeRequestSchema(Schema):
    title = fields.Str(required=True)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionRequestSchema(Schema):
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True)


class ThemeResponseSchema(ThemeRequestSchema):
    id = fields.Int(required=False)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeResponseSchema, many=True)

class QuestionResponseSchema(QuestionRequestSchema):
    id = fields.Int(required=True)
    
class QuestionListSchema(Schema):
    questions = fields.Nested(QuestionResponseSchema, many=True)

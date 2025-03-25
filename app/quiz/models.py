from dataclasses import dataclass


@dataclass
class Theme:
    id: int | None
    title: str


@dataclass
class Answer:
    title: str
    is_correct: bool


@dataclass
class Question:
    id: int | None
    theme_id: int | None
    title: str
    answers: list[Answer]

import json

from pathlib import Path

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone

from .data import (
    COURSE,
    COURSE_TOPICS,
    QUESTIONS,
    get_public_questions,
    calculate_result,
)


# Путь к файлу с результатами тестирования
RESULTS_FILE = Path(settings.BASE_DIR) / "data" / "results.json"


def index(request):
    """Главная страница проекта."""
    return render(
        request,
        "core/index.html",
        {"course": COURSE}
    )

def course(request):
    """Страница с теоретическими материалами курса."""
    context = {
        "course": COURSE,
        "topics": COURSE_TOPICS,
    }

    return render(request, "core/course.html", context)


def test_view(request):
    """Страница тестирования и обработка ответов пользователя."""

    if request.method == "GET":
        # При начале новой попытки удаляем предыдущий результат из сессии
        request.session.pop("course_result", None)

        context = {
            "course": COURSE,
            "questions": get_public_questions(),
        }

        return render(request, "core/test.html", context)

    if request.method == "POST":
        answers = {}

        # Получаем ответы и проверяем заполнение каждого вопроса
        for question in QUESTIONS:
            question_id = str(question["id"])
            answer = request.POST.get(f"question_{question_id}", "")

            valid_answers = {
                option["value"] for option in question["options"]
            }

            if answer not in valid_answers:
                return render(
                    request,
                    "core/access_denied.html",
                    {
                        "message": (
                            "Не удалось отправить тест. "
                            "Ответьте на все вопросы и попробуйте ещё раз."
                        )
                    },
                    status=400,
                )

            answers[question_id] = answer

        # Проверяем ответы и рассчитываем результат
        result_data = calculate_result(answers)

        # Сохраняем результат в JSON-файл
        try:
            RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

            if RESULTS_FILE.exists():
                with open(RESULTS_FILE, "r", encoding="utf-8") as file:
                    results = json.load(file)
            else:
                results = []

            if not isinstance(results, list):
                results = []

            attempt = {
                "date": timezone.localtime().isoformat(),
                **result_data,
            }

            results.append(attempt)

            with open(RESULTS_FILE, "w", encoding="utf-8") as file:
                json.dump(results, file, ensure_ascii=False, indent=4)

        except (OSError, json.JSONDecodeError):
            return render(
                request,
                "core/access_denied.html",
                {
                    "message": (
                        "Не удалось сохранить результат тестирования. "
                        "Попробуйте повторить попытку позже."
                    )
                },
                status=500,
            )

        # Передаём результат на отдельную страницу
        request.session["course_result"] = result_data

        return redirect("result")

    return redirect("course")


def result(request):
    """Страница с результатом прохождения теста."""
    result_data = request.session.get("course_result")

    if not result_data:
        return redirect("course")

    context = {
        "course": COURSE,
        "result": result_data,
    }

    return render(request, "core/result.html", context)


def access_denied(request):
    """Страница обработки отказа в выполнении действия."""
    context = {
        "message": (
            "Доступ к запрошенному действию запрещён. "
            "Вернитесь к курсу и повторите попытку."
        )
    }

    return render(
        request,
        "core/access_denied.html",
        context,
        status=403,
    )
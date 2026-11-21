from django.db import DatabaseError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from .data import (
    COURSE,
    COURSE_TOPICS,
    QUESTIONS,
    calculate_result,
    get_public_questions,
)
from .models import Event, TestResult, UserAnswer


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
    """Страница тестирования и сохранение попытки в базе данных."""

    if request.method == "GET":
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

        # Сохраняем попытку и ответы пользователя в базе данных.
        # Транзакция не даёт записать попытку без её ответов.
        try:
            with transaction.atomic():
                attempt = TestResult.objects.create(
                    score=result_data["correct_count"],
                    max_score=result_data["total_questions"],
                    percent=result_data["percentage"],
                    grade=result_data["grade"],
                    passed=result_data["passed"],
                )

                UserAnswer.objects.bulk_create([
                    UserAnswer(
                        test_result=attempt,
                        question_id=question["id"],
                        selected_option=answers[str(question["id"])],
                        is_correct=(
                            answers[str(question["id"])] == question["correct"]
                        ),
                    )
                    for question in QUESTIONS
                ])

                Event.objects.create(
                    test_result=attempt,
                    message=(
                        f"Попытка №{attempt.pk} завершена: "
                        f"{attempt.score} из {attempt.max_score}, "
                        f"оценка «{attempt.grade}»"
                    ),
                )

        except DatabaseError:
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

        return redirect("result", pk=attempt.pk)

    return redirect("course")


def results(request):
    """Список всех попыток тестирования, сохранённых в базе данных."""
    attempts = TestResult.objects.all()

    context = {
        "course": COURSE,
        "attempts": attempts,
    }

    return render(request, "core/results.html", context)


def events(request):
    """Экран уведомлений о событиях системы."""
    event_list = Event.objects.select_related("test_result").all()

    context = {
        "course": COURSE,
        "events": event_list,
    }

    return render(request, "core/events.html", context)


def result(request, pk):
    """Карточка одной попытки тестирования, прочитанная из базы данных."""
    attempt = get_object_or_404(
        TestResult.objects.prefetch_related("answers"),
        pk=pk,
    )

    questions = {question["id"]: question for question in QUESTIONS}

    answers = [
        {
            "number": answer.question_id,
            "text": questions.get(answer.question_id, {}).get("text", ""),
            "is_correct": answer.is_correct,
        }
        for answer in attempt.answers.all()
    ]

    context = {
        "course": COURSE,
        "attempt": attempt,
        "answers": answers,
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

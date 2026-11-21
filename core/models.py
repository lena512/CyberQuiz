from django.db import models
from django.utils import timezone


class TestResult(models.Model):
    """Результат прохождения итогового тестирования."""

    completed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время прохождения"
    )

    score = models.PositiveSmallIntegerField(
        verbose_name="Количество правильных ответов"
    )

    max_score = models.PositiveSmallIntegerField(
        verbose_name="Максимальное количество баллов"
    )

    percent = models.PositiveSmallIntegerField(
        verbose_name="Процент выполнения"
    )

    grade = models.CharField(
        max_length=30,
        verbose_name="Итоговая оценка"
    )

    passed = models.BooleanField(
        verbose_name="Курс пройден"
    )

    class Meta:
        verbose_name = "Результат тестирования"
        verbose_name_plural = "Результаты тестирования"
        ordering = ["-completed_at"]

    def __str__(self):
        return f"Результат №{self.id}: {self.score}/{self.max_score}"


class UserAnswer(models.Model):
    """Ответ пользователя на отдельный вопрос теста."""

    test_result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Результат тестирования"
    )

    question_id = models.PositiveSmallIntegerField(
        verbose_name="Номер вопроса"
    )

    selected_option = models.CharField(
        max_length=1,
        verbose_name="Выбранный вариант ответа"
    )

    is_correct = models.BooleanField(
        verbose_name="Правильный ответ"
    )

    class Meta:
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответы пользователей"
        ordering = ["question_id"]

        constraints = [
            models.UniqueConstraint(
                fields=["test_result", "question_id"],
                name="unique_answer_per_question_attempt"
            )
        ]

    def __str__(self):
        return (
            f"Вопрос №{self.question_id}, "
            f"результат №{self.test_result_id}"
        )


class Event(models.Model):
    """Уведомление о событии, произошедшем в системе."""

    STATUS_NEW = "new"
    STATUS_READ = "read"
    STATUS_CHOICES = [
        (STATUS_NEW, "Новое"),
        (STATUS_READ, "Прочитано"),
    ]

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время события"
    )

    event_type = models.CharField(
        max_length=50,
        default="attempt_completed",
        verbose_name="Тип события"
    )

    message = models.CharField(
        max_length=255,
        verbose_name="Сообщение"
    )

    test_result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Запись, вызвавшая событие"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name="Статус уведомления"
    )

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Событие №{self.id}: {self.message}"

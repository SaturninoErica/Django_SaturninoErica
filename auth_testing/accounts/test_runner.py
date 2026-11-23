from datetime import datetime
from pathlib import Path
from unittest.runner import TextTestResult

from docx import Document
from django.conf import settings
from django.test.runner import DiscoverRunner


class WordTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append((test.id(), "УСПЕХ", ""))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append(
            (test.id(), "ОШИБКА", self._exc_info_to_string(err, test))
        )

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append(
            (test.id(), "СБОЙ", self._exc_info_to_string(err, test))
        )

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append((test.id(), "ПРОПУЩЕН", reason))

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.records.append(
            (test.id(), "ОЖИДАЕМАЯ ОШИБКА", self._exc_info_to_string(err, test))
        )

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.records.append((test.id(), "НЕОЖИДАННЫЙ УСПЕХ", ""))


class WordReportRunner(DiscoverRunner):
    test_result = None

    def get_resultclass(self):
        return WordTestResult

    def run_suite(self, suite, **kwargs):
        self.test_result = super().run_suite(suite, **kwargs)
        return self.test_result

    def run_tests(self, test_labels, **kwargs):
        failures = super().run_tests(test_labels, **kwargs)
        self.write_report()
        return failures

    def write_report(self):
        result = self.test_result
        if result is None:
            raise RuntimeError("Django не вернул результаты выполненных тестов.")

        report_path = Path(settings.TEST_REPORT_PATH)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        document = Document()
        document.add_heading("Результаты Django-тестирования", level=0)
        document.add_paragraph(
            f"Дата и время: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
        document.add_paragraph(f"Всего тестов: {result.testsRun}")
        passed = sum(status == "УСПЕХ" for _, status, _ in result.records)
        document.add_paragraph(f"Успешно: {passed}")
        document.add_paragraph(f"Ошибок: {len(result.failures)}")
        document.add_paragraph(f"Сбоев: {len(result.errors)}")
        document.add_paragraph(f"Пропущено: {len(result.skipped)}")

        table = document.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        for cell, heading in zip(table.rows[0].cells, ("Тест", "Результат", "Подробности")):
            cell.text = heading

        for test_id, status, details in result.records:
            cells = table.add_row().cells
            cells[0].text = test_id
            cells[1].text = status
            cells[2].text = details or "—"

        document.save(report_path)

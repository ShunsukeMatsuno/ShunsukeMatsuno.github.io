import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from google.analytics.data_v1beta.types import (
    DimensionHeader,
    DimensionValue,
    MetricHeader,
    MetricValue,
    Row,
    RunReportRequest,
    RunReportResponse,
)


script = Path(__file__).resolve().parents[1] / 'scripts' / 'details.py'
spec = importlib.util.spec_from_file_location('ga_details', script)
details = importlib.util.module_from_spec(spec)
spec.loader.exec_module(details)


class ReportPaginationTests(unittest.TestCase):
    def test_recent_rows_beyond_default_limit_reach_processed_report(self):
        request = details.create_report_request('123')
        self.assertEqual(request.limit, 10000)
        self.assertEqual(
            [order.dimension.dimension_name for order in request.order_bys],
            [dimension.name for dimension in request.dimensions],
        )

        def make_row(time):
            return Row(
                dimension_values=[DimensionValue(value=value) for value in (
                    time, 'Example country', 'Example city', '123', 'desktop',
                    '(not set)', '/', '(not set)', '(not set)',
                )],
                metric_values=[MetricValue(value='1'), MetricValue(value='1')],
            )

        first_page = RunReportResponse(
            dimension_headers=[DimensionHeader(name=dim.name) for dim in request.dimensions],
            metric_headers=[MetricHeader(name=metric.name) for metric in request.metrics],
            rows=[make_row('202610021100')] * 10000,
            row_count=10001,
        )
        last_page = RunReportResponse(rows=[make_row('202610111225')], row_count=10001)
        requests = []

        def run_report(page_request):
            requests.append(RunReportRequest(page_request))
            return first_page if page_request.offset == 0 else last_page

        response = details.fetch_report(Mock(run_report=run_report), request)
        self.assertEqual(len(response.rows), 10001)
        self.assertEqual([page.offset for page in requests], [0, 10000])
        self.assertEqual(request.offset, 0)
        with patch.object(details, 'tqdm', side_effect=lambda rows, **kwargs: rows):
            frame = details.process_response(response)
        self.assertEqual(frame['time'].max(), '2026-10-11 12:25:00')

    def test_short_pages_advance_by_actual_number_of_rows(self):
        request = details.create_report_request('123')
        request.limit = 3
        pages = iter([
            RunReportResponse(rows=[Row(), Row()], row_count=5),
            RunReportResponse(rows=[Row()], row_count=5),
            RunReportResponse(rows=[Row(), Row()], row_count=5),
        ])
        offsets = []

        def run_report(page_request):
            offsets.append(page_request.offset)
            return next(pages)

        response = details.fetch_report(Mock(run_report=run_report), request)
        self.assertEqual(len(response.rows), 5)
        self.assertEqual(offsets, [0, 2, 3])

    def test_empty_page_cannot_silently_save_incomplete_report(self):
        client = Mock()
        client.run_report.side_effect = [
            RunReportResponse(rows=[Row()], row_count=2),
            RunReportResponse(row_count=2),
        ]
        with self.assertRaisesRegex(RuntimeError, 'empty page at offset 1'):
            details.fetch_report(client, details.create_report_request('123'))

    def test_complete_or_empty_report_needs_only_one_request(self):
        for rows in ([], [Row()]):
            with self.subTest(row_count=len(rows)):
                client = Mock()
                client.run_report.return_value = RunReportResponse(rows=rows, row_count=len(rows))
                response = details.fetch_report(client, details.create_report_request('123'))
                self.assertEqual(len(response.rows), len(rows))
                client.run_report.assert_called_once()


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock

from reports_module.reportslib.interannual_manager import InterAnnualManager


class TestInterannual(unittest.TestCase):
    def test_match_factsheet(self):
        logger_manager = MagicMock()
        i_manager = InterAnnualManager(logger_manager)
        start_date = i_manager._get_previous_month_start_date()
        end_date = i_manager._get_previous_month_end_date()
        now_fact_name = "{0}_{1}_test".format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        old_fact_name = "2010-09-01_2017-09-30_2017-10-26_19-9-31-707217"
        c = i_manager._match_factsheet(now_fact_name)
        self.assertEqual(c, True)
        c = i_manager._match_factsheet(old_fact_name)
        self.assertEqual(c, False)

    def test_get_latest_factsheet(self):
        logger_manager = MagicMock()
        i_manager = InterAnnualManager(logger_manager)
        i_manager._get_factsheets = MagicMock(return_value=['C', 'A', 'B'])
        f = i_manager._get_latest_factsheet()
        self.assertEqual(f, 'C')

    def test_append_previous_month_data_to_base_file(self):
        logger_manager = MagicMock()
        i_manager = InterAnnualManager(logger_manager)
        year = '{0}'.format(i_manager._get_previous_month_start_date().year)
        month = '{0}'.format(i_manager._get_previous_month_end_date().month)

        factsheet = {'stats': {}}
        factsheet['stats'][year] = {'months': {}}
        factsheet['stats'][year]['months'][month] = {'total': 123}
        i_manager._get_factsheet = MagicMock(return_value=factsheet)

        base = {'stats': {}}
        base['stats'][year] = {'months': {'0': {'total': 100}}}
        i_manager._get_base_file = MagicMock(return_value=base)

        i_manager._append_previous_month_data_to_base_file()
        r = i_manager.interannual_factsheet

        # Check base document is there
        self.assertTrue('0' in r['stats'][year]['months'])
        # Chack factsheet is there
        self.assertTrue(month in r['stats'][year]['months'])
        # Check total is there
        self.assertEqual(r['stats'][year]['months'][month]['total'], 123)

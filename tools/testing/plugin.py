"""
pytest plugin: reporter parecido a mocha.js
"""

from collections import Counter
from functools import partial
from typing import Callable, Dict, List, Mapping, Optional

from _pytest import timing
from _pytest.reports import BaseReport, CollectReport, TestReport
from _pytest.terminal import (
    TerminalReporter,
    WarningReport,
    _color_for_type,
    _color_for_type_default,
    _folded_skips,
    _get_line_with_reprcrash_message,
    _get_node_id_with_markup,
    format_session_duration,
)
from colorama import Fore, Style

from .loader import load_test_info

STORAGE = {'parents': {}}
STATUS_ICONS = {
    'passed': '✓',
    'failed': '✖',
    'skipped': '!',
    'error': 'E',
    'xfailed': '✖',
    'xpassed': '✓',
}
COLORS = {
    'passed': Fore.GREEN,
    'failed': Fore.RED,
    'skipped': Fore.YELLOW,
    'error': Fore.RED,
    'xfailed': Fore.YELLOW,
    'xpassed': Fore.YELLOW,
    'link': Fore.BLUE,
}


def logend_replacer(self: TerminalReporter, nodeid: int, location: str) -> None:
    pass


def logstart_replacer(self: TerminalReporter, nodeid: int, location: str) -> None:
    pass


def summary_warnings(self: TerminalReporter) -> None:
    if self.hasopt('w'):
        all_warnings: Optional[List[WarningReport]] = self.stats.get('warnings')
        if not all_warnings:
            return

        final = self._already_displayed_warnings is not None
        if final:
            warning_reports = all_warnings[self._already_displayed_warnings :]
        else:
            warning_reports = all_warnings
        self._already_displayed_warnings = len(warning_reports)
        if not warning_reports:
            return

        reports_grouped_by_message: Dict[str, List[WarningReport]] = {}
        for wr in warning_reports:
            reports_grouped_by_message.setdefault(wr.message, []).append(wr)

        def collapsed_location_report(reports: List[WarningReport]) -> str:
            locations = []
            for w in reports:
                location = w.get_location(self.config)
                if location:
                    locations.append(location)

            if len(locations) < 10:
                return '\n'.join(map(str, locations))

            counts_by_filename = Counter(str(loc).split('::', 1)[0] for loc in locations)
            return '\n'.join(
                '{}: {} warning{}'.format(k, v, 's' if v > 1 else '')
                for k, v in counts_by_filename.items()
            )

        self.write('\n\nWarnings\n', yellow=True, bold=True)
        self.write_sep('-', None, yellow=True, bold=True)
        for message, _ in reports_grouped_by_message.items():
            message = message.rstrip()
            self._tw.line(message)
            self._tw.line()


def summary_stats(self: TerminalReporter) -> None:
    if self.verbosity < -1:
        return

    self.write('\nSummary\n', purple=True, bold=True)
    self.write_sep('-', None, purple=True, bold=True)

    session_duration = timing.time() - self._sessionstarttime
    (parts, main_color) = self.build_summary_stats_line()
    line_parts = []

    for text, markup in parts:
        with_markup = self._tw.markup(text, **markup)
        line_parts.append(with_markup)
    msg = ', '.join(line_parts)

    main_markup = {main_color: True}
    duration = f' in {format_session_duration(session_duration)}'
    duration_with_markup = self._tw.markup(duration, **main_markup)
    msg += duration_with_markup + '\n'

    self.write_line(msg, **main_markup)


def summary_failures_replacer(self: TerminalReporter) -> None:
    if self.config.option.tbstyle != 'no':
        reports: List[BaseReport] = self.getreports('failed')
        if not reports:
            return

        self.write('\nFailures\n', red=True, bold=True)
        self.write_sep('-', None, red=True, bold=True)

        if self.config.option.tbstyle == 'line':
            for rep in reports:
                line = self._getcrashline(rep)
                self.write_line(line)
        else:
            for rep in reports:
                msg = self._getfailureheadline(rep)
                self.write(f'\n{msg}\n', red=True, bold=True)

                self._outrep_summary(rep)
                self._handle_teardown_sections(rep.nodeid)


def short_test_summary_replacer(self: TerminalReporter) -> None:
    if not self.reportchars:
        return

    def show_simple(lines: List[str], *, stat: str) -> None:
        failed = self.stats.get(stat, [])
        if not failed:
            return
        config = self.config
        for rep in failed:
            color = _color_for_type.get(stat, _color_for_type_default)
            line = _get_line_with_reprcrash_message(config, rep, self._tw, {color: True})
            lines.append(line)

    def show_xfailed(lines: List[str]) -> None:
        xfailed = self.stats.get('xfailed', [])
        for rep in xfailed:
            verbose_word = rep._get_verbose_word(self.config)
            markup_word = self._tw.markup(verbose_word, **{_color_for_type['warnings']: True})
            nodeid = _get_node_id_with_markup(self._tw, self.config, rep)
            line = f'{markup_word} {nodeid}'
            reason = rep.wasxfail
            if reason:
                line += ' - ' + str(reason)

            lines.append(line)

    def show_xpassed(lines: List[str]) -> None:
        xpassed = self.stats.get('xpassed', [])
        for rep in xpassed:
            verbose_word = rep._get_verbose_word(self.config)
            markup_word = self._tw.markup(verbose_word, **{_color_for_type['warnings']: True})
            nodeid = _get_node_id_with_markup(self._tw, self.config, rep)
            reason = rep.wasxfail
            lines.append(f'{markup_word} {nodeid} {reason}')

    def show_skipped(lines: List[str]) -> None:
        skipped: List[CollectReport] = self.stats.get('skipped', [])
        fskips = _folded_skips(self.startpath, skipped) if skipped else []
        if not fskips:
            return
        verbose_word = skipped[0]._get_verbose_word(self.config)
        markup_word = self._tw.markup(verbose_word, **{_color_for_type['warnings']: True})
        prefix = 'Skipped: '
        for num, fspath, lineno, reason in fskips:
            if reason.startswith(prefix):
                reason = reason[len(prefix) :]
            if lineno is not None:
                lines.append('%s [%d] %s:%d: %s' % (markup_word, num, fspath, lineno, reason))
            else:
                lines.append('%s [%d] %s: %s' % (markup_word, num, fspath, reason))

    REPORTCHAR_ACTIONS: Mapping[str, Callable[[List[str]], None]] = {
        'x': show_xfailed,
        'X': show_xpassed,
        'f': partial(show_simple, stat='failed'),
        's': show_skipped,
        'p': partial(show_simple, stat='passed'),
        'E': partial(show_simple, stat='error'),
    }

    lines: List[str] = []
    for char in self.reportchars:
        action = REPORTCHAR_ACTIONS.get(char)
        if action:  # skipping e.g. "P" (passed with output) here.
            action(lines)

    if lines:
        self.write('\nProblems\n', purple=True, bold=True)
        self.write_sep('-', None, purple=True, bold=True)
        for line in lines:
            self.write_line(line)


def report_replacer(self: TerminalReporter, report: TestReport) -> None:
    res = self.config.hook.pytest_report_teststatus(report=report, config=self.config)
    category, letter, word = res
    self.stats.setdefault(category, []).append(report)
    if not letter and not word:
        return

    file_name, text = load_test_info(report.nodeid)
    text = [x.strip() for x in text.split('::')]
    parents = []
    if len(text) >= 1:
        parents.extend(text[:-1])
    if not parents:
        parents = [file_name]

    text = text[-1]

    indent = '    '
    test_indent = indent
    tmp_keys = []
    upper_parent_changed = False
    for idx, parent in enumerate(parents):
        tmp_keys.append(idx)
        test_indent = indent * (idx + 1)
        old_parent = STORAGE['parents'].get(idx, None)
        if not upper_parent_changed and parent == old_parent:
            continue

        upper_parent_changed = True
        STORAGE['parents'][idx] = parent

        parent_line = parent
        if idx == 0 and parent != file_name:
            parent_line = '{parent} ({color}{file_name}{reset})'

        self._tw.write(
            '\n' if idx > 0 else '\n\n',
        )

        self._tw.write(
            indent * idx
            + parent_line.format(
                parent=parent, file_name=file_name, color=COLORS['link'], reset=Style.RESET_ALL
            )
        )

    for key in list(STORAGE['parents']):
        if key not in tmp_keys:
            STORAGE['parents'].pop(key)

    category = category.strip()
    self._tw.line()
    self._tw.write(
        '{color}{indent}{icon} {text}{reset}'.format(
            color=COLORS[category],
            indent=test_indent,
            icon=STATUS_ICONS[category],
            text=text,
            reset=Style.RESET_ALL,
        )
    )


def pytest_configure() -> None:
    import importlib

    import _pytest
    import _pytest.terminal

    _pytest.terminal.TerminalReporter.summary_warnings = summary_warnings  # type: ignore
    _pytest.terminal.TerminalReporter.pytest_runtest_logstart = logstart_replacer  # type: ignore
    _pytest.terminal.TerminalReporter.pytest_runtest_logreport = report_replacer
    _pytest.terminal.TerminalReporter.pytest_runtest_logfinish = logend_replacer  # type: ignore
    _pytest.terminal.TerminalReporter.summary_failures = summary_failures_replacer
    _pytest.terminal.TerminalReporter.short_test_summary = short_test_summary_replacer
    _pytest.terminal.TerminalReporter.summary_stats = summary_stats
    importlib.reload(_pytest)

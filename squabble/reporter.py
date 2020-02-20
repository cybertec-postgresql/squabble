# coding: utf-8

import functools
import json
import sys

import pglast
from colorama import Fore, Style

import squabble
from squabble.lint import Severity

_REPORTERS = {}


class UnknownReporterException(squabble.SquabbleException):
    """Raised when a configuration references a reporter that doesn't exist."""
    def __init__(self, name):
        super().__init__('unknown reporter: "%s"' % name)


def reporter(name):
    """
    Decorator to register function as a callback when the config sets the
    ``"reporter"`` config value to ``name``.

    The wrapped function will be called with each
    :class:`squabble.lint.LintIssue` and the contents of the file
    being linted. Each reporter should return a list of lines of
    output which will be printed to stderr.

    >>> from squabble.lint import LintIssue
    >>> @reporter('no_info')
    ... def no_info(issue, file_contents):
    ...     return ['something happened']
    ...
    >>> no_info(LintIssue(), file_contents='')
    ['something happened']
    """
    def wrapper(fn):
        _REPORTERS[name] = fn

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapped

    return wrapper


def report(reporter_name, issues, files):
    """
    Call the named reporter function for every issue in the list of
    issues. All lines of output returned will be printed to stderr.

    :param reporter_name: Issue reporter format to use.
    :type reporter_name: str
    :param issues: List of generated :class:`squabble.lint.LintIssue`.
    :type issues: list
    :param files: Map of file name to contents of file.
    :type files: dict

    >>> import sys; sys.stderr = sys.stdout  # for doctest.
    >>> from squabble.lint import LintIssue
    >>> @reporter('message_and_severity')
    ... def message_and_severity_reporter(issue, contents):
    ...     return ['%s:%s' % (issue.severity.name, issue.message_text)]
    ...
    >>> issue = LintIssue(severity=Severity.CRITICAL,
    ...                   message_text='bad things!')
    >>> report('message_and_severity', [issue], files={})
    CRITICAL:bad things!
    """
    if reporter_name not in _REPORTERS:
        raise UnknownReporterException(reporter_name)

    reporter_fn = _REPORTERS[reporter_name]

    for i in issues:
        file_contents = files.get(i.file, '')
        for line in reporter_fn(i, file_contents):
            _print_err(line)


def _print_err(msg):
    print(msg, file=sys.stderr)


def _format_message(issue):
    if issue.message_text:
        return issue.message_text

    return issue.message.format()


def _issue_info(issue):
    """Return a dictionary of metadata for an issue."""
    formatted = _format_message(issue)

    return {
        **issue._asdict(),
        **(issue.message.asdict() if issue.message else {}),
        'message_formatted': formatted,
        'severity': issue.severity.name,
    }


_SIMPLE_FORMAT = '{file}:{line}:{column} {severity}: {message_formatted}'

# Partially pre-format the message since the color codes will be static.
_COLOR_FORMAT = '{bold}{{file}}:{reset}{{line}}:{{column}}{reset} '\
    '{{severity}} {{message_formatted}}'\
    .format(bold=Style.BRIGHT, reset=Style.RESET_ALL)


@reporter("plain")
def plain_text_reporter(issue, file_contents):
    """Simple single-line output format that is easily parsed by editors."""
    info = _issue_info(issue, file_contents)
    return [
        _SIMPLE_FORMAT.format(**info)
    ]


_SEVERITY_COLOR = {
    Severity.CRITICAL: Fore.RED,
    Severity.HIGH: Fore.RED,
    Severity.MEDIUM: Fore.YELLOW,
    Severity.LOW: Fore.BLUE,
}


@reporter('color')
def color_reporter(issue, file_contents):
    """
    Extension of :func:`squabble.reporter.plain_text_reporter`, uses
    ANSI color and shows error location.
    """
    info = _issue_info(issue, file_contents)
    info['severity'] = '{color}{severity}{reset}'.format(
        color=_SEVERITY_COLOR[issue.severity],
        severity=issue.severity.name,
        reset=Style.RESET_ALL
    )

    output = [_COLOR_FORMAT.format(**info)]

    if 'message_code' in info:
        output[0] += ' [{message_code}]'.format(**info)

    if info['line_text'] != '':
        arrow = ' ' * info['column'] + '^'
        output.append(info['line_text'])
        output.append(Style.BRIGHT + arrow + Style.RESET_ALL)

    return output


@reporter('json')
def json_reporter(issue, _file_contents):
    """Dump each issue as a JSON dictionary"""

    # Swap out all of the non-JSON serializable elements:
    issue = issue._replace(severity=issue.severity.name)

    if issue.node:
        issue = issue._replace(node=issue.node.parse_tree)

    if issue.message:
        issue = issue._replace(message=issue.message.asdict())

    obj = {
        k: v for k, v in issue._asdict().items()
        if v is not None
    }

    return [
        json.dumps(obj)
    ]


_SQLINT_FORMAT = '{file}:{line}:{column}:{severity} {message_formatted}'


@reporter('sqlint')
def sqlint_reporter(issue, file_contents):
    """
    Format compatible with ``sqlint``, which is already integrated into
    Flycheck and other editor linting frameworks.

    Main difference is really just that there are only two severity
    levels: ``ERROR`` and ``WARNING``.
    """

    error_level = {Severity.HIGH, Severity.CRITICAL}

    info = _issue_info(issue, file_contents)
    info['severity'] = 'ERROR' if issue.severity in error_level else 'WARNING'

    return [
        _SQLINT_FORMAT.format(**info)
    ]

import shutil

import click

from openldap_acl_test import __name__, __version__
from openldap_acl_test.conf import load_conf, load_testcases
from openldap_acl_test.log import init_logger
from openldap_acl_test.testcase import ACLTestCase


@click.command()
@click.option(
    "-c",
    "--conffile",
    help="conffile path",
    type=click.Path(exists=True),
    default="acltest_conf.yml",
    show_default=True,
    envvar="ACLTEST_CONFFILE",
)
@click.option(
    "--slapacl",
    help="slapacl path",
    type=click.Path(exists=True),
    default="/usr/sbin/slapacl",
    show_default=True,
    envvar="ACLTEST_SLAPACL",
)
@click.option("--dry-run", help="dry run", is_flag=True)
@click.option("-v", "--verbose", help="verbose output", is_flag=True)
@click.help_option("-h", "--help")
@click.version_option(version=__version__, package_name=__name__)
def main(conffile, slapacl, dry_run, verbose):
    logger = init_logger("INFO")
    if verbose:
        logger = init_logger("DEBUG")
    logger.debug(f"load conffile {conffile=}")
    testcases: list[ACLTestCase] = []
    try:
        confdata = load_conf(conffile)
        testcases = load_testcases(confdata)
    except Exception as error:
        raise click.FileError(conffile, hint=error)

    for testcase in testcases:
        logger.debug(
            f"RUN TEST {testcase.requester} -> {testcase.target} (testcase.acl)"
        )
        if dry_run:
            logger.debug("not run [--dry-run]")
            continue
        try:
            testcase.run_test(slapacl)
        except Exception as error:
            if verbose:
                logger.exception(error)
            else:
                logger.error(error)
            raise click.Abort()
    report = report_output(testcases)
    logger.info(report)


def report_output(testcases: list[ACLTestCase]):
    """
    testcases内のresult_listの値を集計し、レポート結果を出力する。
    """
    lines = []
    terminal_size = 80
    try:
        terminal_size, _ = shutil.get_terminal_size()
    except Exception:
        pass
    total_result = {"ok": 0, "ng": 0}
    for testcase in testcases:
        total_result["ok"] += testcase.get_success_count()
        total_result["ng"] += testcase.get_failure_count()
        text = (
            f"[{testcase.requester} -> {testcase.target}({testcase.acl})]"
            f" {testcase.get_result_dots()}"
        )
        lines.append(text)
    lines.append("")

    lines.append("-" * terminal_size)
    lines.append(
        f"SUCCESS: {total_result['ok']}  FAILURE: {total_result['ng']} TESTCASES: {len(testcases)}"  # noqa: E501
    )
    return "\n".join(lines)

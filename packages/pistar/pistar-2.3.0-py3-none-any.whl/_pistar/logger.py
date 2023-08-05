from typing import Optional, TYPE_CHECKING

from _pistar.caller import ExecuteInfo
from _pistar.utilities.testcase.steps import Step
from _pistar.utilities.exceptions.testcase import PassedException
from _pistar.config.cmdline import hookimpl

if TYPE_CHECKING:
    from _pistar.result import Result
    from _pistar.utilities.testcase.case import TestCase


@hookimpl(hookwrapper=True)
def pistar_make_report(case: "TestCase", call_info: ExecuteInfo, step: Optional[Step]):
    result: "Result" = (yield).get_result()
    if result.passed and isinstance(result.exception, PassedException):
        case.clazz.info(str(result.exception))
    elif result.longrepr and result.failed:
        case.clazz.error(result.longrepr)


@hookimpl(hookwrapper=True)
def pistar_step_call(step: Step):
    set_execution_log(step.parent, f"step {step.name} start.")
    if step.stepobj.description:
        set_execution_log(step.parent, f"step {step.name} description: {step.stepobj.description}")
    yield


def set_execution_log(case, msg):
    case._obj.info(msg)

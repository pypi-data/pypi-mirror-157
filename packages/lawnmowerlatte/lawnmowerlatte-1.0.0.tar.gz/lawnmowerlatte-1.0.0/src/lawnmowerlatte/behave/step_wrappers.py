import os
import time
import json
import errno
import signal
import inspect
import pathlib
import functools
import logging as log
from functools import wraps
from behave.step_registry import registry as the_step_registry
from behave.model import ScenarioOutline
from lawnmowerlatte.behave.lexical_analyzer import parse_path_string


class Step(object):
    def __init__(self, step_text):
        self.step_text = step_text
        self.fn = None

    def __str__(self):
        return f"<Step [{self.step_text} -> {self.fn}]>"

    def __call__(self, fn):
        def wrapped(context, *args, **kwargs):
            # Get the names of the arguments from signature
            kwkeys = [
                k for k in inspect.signature(fn).parameters.keys() if k != "context"
            ]

            # Get default values from signature
            defaults = {
                k: v.default
                for k, v in inspect.signature(fn).parameters.items()
                if isinstance(v.default, str) and k in kwkeys
            }

            # If no kwargs are presented, use args
            if len(kwargs) == 0:
                kwargs = {}
                index = 0
                for k in kwkeys:
                    if len(args) > index:
                        kwargs[k] = args[index]
                    else:
                        kwargs[k] = None
                    index += 1

            # Set merged with default values
            merged_kwargs = defaults.copy()

            # Overwrite defaults if set
            for k, v in kwargs.items():
                if k in merged_kwargs.keys():
                    if v is not None:
                        merged_kwargs[k] = v
                else:
                    merged_kwargs[k] = v

            # Set initial value
            replaced_kwargs = {}

            # Lookup values
            for k, v in merged_kwargs.items():
                r = parse_path_string(context, v)
                replaced_kwargs[k] = r

            log.info("{} was called".format(fn.__name__))
            log.info("Argument names are: {}".format(kwkeys))
            log.info("Default value are: {}".format(defaults))
            log.info("Function args are: {}".format(args))
            log.info("Function kwargs are: {}".format(kwargs))
            log.info("Merged kwargs are: {}".format(merged_kwargs))
            log.info("Replaced kwargs are: {}".format(replaced_kwargs))

            return fn(context, **replaced_kwargs)

        self.fn = wrapped
        the_step_registry.add_step_definition("step", self.step_text, self.fn)
        # This line adds the step to Behave
        # This works just fine and removes the need for both @parse
        # and @step however, PyCharm doesn't understand so it can't find
        # the steps for navigation

        print(self)
        return self.fn


def parse(step_function):
    @wraps(step_function)
    def wrapper(context, *args, **kwargs):
        # Get the names of the arguments from signature
        kwkeys = [
            k
            for k in inspect.signature(step_function).parameters.keys()
            if k != "context"
        ]

        # Get default values from signature
        defaults = {
            k: v.default
            for k, v in inspect.signature(step_function).parameters.items()
            if isinstance(v.default, str) and k in kwkeys
        }

        # If no kwargs are presented, use args
        if len(kwargs) == 0:
            kwargs = {}
            index = 0
            for k in kwkeys:
                if len(args) > index:
                    kwargs[k] = args[index]
                else:
                    kwargs[k] = None
                index += 1

        # Set merged with default values
        merged_kwargs = defaults.copy()

        # Overwrite defaults if set
        for k, v in kwargs.items():
            if k in merged_kwargs.keys():
                if v is not None:
                    merged_kwargs[k] = v
            else:
                merged_kwargs[k] = v

        # Set initial value
        replaced_kwargs = {}

        # Lookup values
        for k, v in merged_kwargs.items():
            r = parse_path_string(context, v)
            replaced_kwargs[k] = r

        # log.debug("{} was called".format(step_function.__name__))
        # log.debug("Argument names are: {}".format(kwkeys))
        # log.debug("Default value are: {}".format(defaults))
        # log.debug("Function args are: {}".format(args))
        # log.debug("Function kwargs are: {}".format(kwargs))
        # log.debug("Merged kwargs are: {}".format(merged_kwargs))
        # log.debug("Replaced kwargs are: {}".format(replaced_kwargs))

        return step_function(context, **replaced_kwargs)

    return wrapper


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def timeout_decorator(step_function):
        @wraps(step_function)
        def wrapper(context, *args, **kwargs):
            log.debug(f"Step timeout set to {seconds}s")

            def _handle_timeout(signum, frame):
                log.critical(f"Timeout received! Signal {signum} from {frame}")
                raise TimeoutError(error_message)

            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            log.debug(f"Arrange for alarm in {seconds}s")
            try:
                result = step_function(context, *args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return timeout_decorator


def write_retry_report(filename, report):
    try:
        with open(filename, "r") as f:
            contents = json.load(f)
    except:
        contents = []

    report["timestamp"] = int(time.time())
    contents.append(report)

    with open(filename, "w") as f:
        json.dump(contents, f, separators=(",", ": "), indent=4)


def retryable(
    max_attempts=None,
    instance_timeout=None,
    global_timeout=None,
    backoff_delay=250,
    backoff_multiplier=2.2,
    backoff_maximum=120000,
):
    """
    Wraps steps to allow them to be retried if they fail initially. This can be controlled either by
    max_attempts, global_timeout, or both. Backoff delays between failures are configurable as well.

    :param max_attempts: Maximum number of retries allowed. Optional. Default behavior is no limit.
    :param instance_timeout: Maximum number of seconds to wait for each execution of the step.
    :param global_timeout: Maximum number of seconds to wait overall for a successful pass.
    :param backoff_delay: Initial time between attempts in milliseconds.
    :param backoff_multiplier: Rate of increase in backoff_delay over successive attempts.
    :param backoff_maximum: Maximum time between attempts in milliseconds.
    """
    # Validate settings to avoid improper use and infinite loops
    if max_attempts is not None and max_attempts <= 0:
        raise RuntimeError("Max attempts cannot be set to a non-positive integer")

    if max_attempts is None and instance_timeout is None and global_timeout is None:
        raise RuntimeError("Steps cannot be marked as @retryable without parameters")

    if max_attempts is None and global_timeout is None:
        raise RuntimeError("Infinite retries require a global timeout")

    def retryable_decorator(step_function):
        @wraps(step_function)
        def wrapper(context, *args, **kwargs):
            if context.env["use_external_fixture"]:
                log.debug(f"No retryable for external fixtures")
                step_function(context, *args, **kwargs)
                return

            def _handle_timeout(signum, frame):
                log.debug(f"Timeout received! Signal {signum} from {frame}")
                raise TimeoutError(os.strerror(errno.ETIME))

            log.debug(f"This step can be retried: {step_function}")

            exception = None
            attempt = 1
            success = False
            delay = backoff_delay

            report = {
                "function": step_function.__name__,
                "location": inspect.getfile(step_function),
                "line": inspect.getsourcelines(step_function)[1],
                "args": args,
                "kwargs": kwargs,
                "max_attempts": max_attempts,
                "attempts": [],
                "instance_timeout": instance_timeout,
                "global_timeout": global_timeout,
                "backoff_delay": backoff_delay,
                "backoff_multiplier": backoff_multiplier,
                "backoff_maximum": backoff_maximum,
                "result": "undefined",
            }

            try:
                report["feature"] = {
                    "feature": context.feature.name,
                    "filename": context.scenario.filename,
                    "line": context.feature.line,
                }
            except:
                pass

            try:
                report["scenario"] = {
                    "scenario": context.scenario.name,
                    "line": context.scenario.line,
                }
            except:
                pass

            try:
                report["step"] = {
                    "step": context.step.name,
                    "line": context.step.line,
                }
            except:
                pass

            report_path = os.path.join(
                "reports",
                "retries",
                "steps",
                os.path.relpath(inspect.getfile(step_function)),
            )
            report_filename = os.path.join(
                report_path, f"{step_function.__name__}.json"
            )
            pathlib.Path(report_path).mkdir(parents=True, exist_ok=True)

            start_time = time.time()
            report["start_time"] = int(start_time)

            # Set global end time
            if global_timeout is not None:
                deadline = start_time + global_timeout

            else:
                deadline = None

            # While step has not passed, the max attempts has not been reached and the global timeout has not been reached.
            # Note, the global timeout is only checked at the end of an instance. Multiple signals alarms are not supported.
            while (
                (not success)
                and (max_attempts is None or attempt <= max_attempts)
                and (deadline is None or time.time() < deadline)
            ):

                # Set per-instance timeout
                if instance_timeout is not None:
                    signal.signal(signal.SIGALRM, _handle_timeout)
                    signal.alarm(int(instance_timeout))

                try:
                    result = step_function(context, *args, **kwargs)
                    end_time = time.time()
                    report["attempts"].append("Pass")
                    report["end_time"] = int(end_time)
                    report["duration"] = int((end_time - start_time) * 1000)

                    if attempt > 1:
                        # Only generate a report if the step actually used the retryable functionality
                        log.debug(
                            "@retryable step passed after {attempt} attempts, dumping log"
                        )
                        report["result"] = "passed"
                        report["cause"] = None
                        write_retry_report(report_filename, report)
                    return result
                except TimeoutError as ex:
                    log.warning(
                        f"Instance execution timeout reached on attempt {attempt}, waiting {delay}ms"
                    )
                    exception = ex
                    report["attempts"].append(str(exception))
                except Exception as ex:
                    log.warning(f"Step failed on attempt {attempt}, waiting {delay}ms")
                    exception = ex
                    report["attempts"].append(str(exception))
                finally:
                    # Clear the signal
                    signal.alarm(0)
                    # Add backoff delay and recalculate next
                    time.sleep(delay / 1000)
                    delay = int(delay * backoff_multiplier)
                    delay = min(delay, backoff_maximum)
                    attempt += 1

            end_time = time.time()
            report["result"] = "failed"
            report["end_time"] = int(end_time)
            report["duration"] = int((end_time - start_time) * 1000)

            if deadline is not None and deadline < end_time:
                report["cause"] = "timed out"
            else:
                report["cause"] = "gave up"

            report["exception"] = str(exception)
            write_retry_report(report_filename, report)

            log.critical(f"Retryable step failed: {str(exception)}")
            raise exception

        return wrapper

    return retryable_decorator


def patch_with_autoretry(scenario, max_attempts=3):
    """
    Cloned from behave.contrib.scenario_autoretry with added logging
    Monkey-patches :func:`~behave.model.Scenario.run()` to auto-retry a
    scenario that fails. The scenario is retried a number of times
    before its failure is accepted.

    This is helpful when the test infrastructure (server/network environment)
    is unreliable (which should be a rare case).

    :param scenario:        Scenario or ScenarioOutline to patch.
    :param max_attempts:    How many times the scenario can be run.
    """

    def scenario_run_with_retries(scenario_run, *args, **kwargs):
        scenario = scenario_run.__self__
        report = {
            "feature": scenario.feature.name,
            "scenario": scenario.name,
            "filename": scenario.filename,
            "line": scenario.line,
            "args": args[1:],
            "kwargs": kwargs,
            "max_attempts": max_attempts,
            "attempts": [],
            "result": "undefined",
        }

        report_path = os.path.join("reports", "retries", "scenarios", scenario.filename)
        report_filename = os.path.join(report_path, f"{scenario.line}.json")
        pathlib.Path(report_path).mkdir(parents=True, exist_ok=True)

        for attempt in range(1, max_attempts + 1):
            scenario_result = scenario_run(*args, **kwargs)
            report["attempts"].append(not scenario_result)
            if not scenario_result:
                if attempt > 1:
                    message = "AUTO-RETRY SCENARIO PASSED (after {0} attempts)"
                    log.info(message.format(attempt))

                    # Only generate a report if the step actually used the autoretry functionality
                    report["result"] = "passed"
                    write_retry_report(report_filename, report)
                return False  # -- NOT-FAILED = PASSED
            # -- SCENARIO FAILED:
            if attempt < max_attempts:
                log.error("AUTO-RETRY SCENARIO (attempt {0})".format(attempt))
        message = "AUTO-RETRY SCENARIO FAILED (after {0} attempts)"
        log.critical(message.format(max_attempts))
        report["result"] = "failed"
        write_retry_report(report_filename, report)
        return True

    if isinstance(scenario, ScenarioOutline):
        scenario_outline = scenario
        for scenario in scenario_outline.scenarios:
            scenario_run = scenario.run
            scenario.run = functools.partial(scenario_run_with_retries, scenario_run)
    else:
        scenario_run = scenario.run
        scenario.run = functools.partial(scenario_run_with_retries, scenario_run)


def skip_if_external(func):
    def check_for_fixture(context, *args, **kwargs):
        if context.config.userdata.get("external", False):
            log.debug(f"Skipping {func} for external check")
            return
        func(context, *args, **kwargs)

    return check_for_fixture


def skip_if(func, condition):
    def run_step_if(context, *args, **kwargs):
        if condition:
            log.info(f"Skipping step {func} based on conditional")
            return
        func(context, *args, **kwargs)

    return run_step_if

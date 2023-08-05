import traceback
import sys
import os
from pathlib import Path
from .common import ProcessedMessageArgs, ExceptionArgs, TBLineParseFailure


__author__ = "IncognitoCoding"
__copyright__ = "Copyright 2022, formatter"
__credits__ = ["IncognitoCoding"]
__license__ = "MIT"
__version__ = "0.3.11"
__maintainer__ = "IncognitoCoding"
__status__ = "Beta"


def exception_formatter(processed_message_args: ProcessedMessageArgs, exception_args: ExceptionArgs) -> str:
    """
    The exception formatter creates consistent clean exception output.
    No logging will take place within this function.\\
    The exception output will have an origination location based on the exception section.\\
    Any formatted raised exceptions will originate from the calling function.\\
    All local function or Attribute errors will originate from this function.

    The user can override the exception type from the general custom exception module classes above.

    Args:
        processed_message_args (ProcessedMessageArgs):\\
        \t\\- Message args to populate the formatted exception message.
        exception_args (ExceptionArgs):
        \t\\- Exception args to populate the formatted exception message.
    """
    # #################################################
    # ###########Formats Lists or Str Output###########
    # #################################################
    if processed_message_args.expected_result:
        if isinstance(processed_message_args.expected_result, list):
            formatted_expected_result: str = str(
                "  - " + "\n  - ".join(map(str, processed_message_args.expected_result))
            )
        else:
            formatted_expected_result: str = f"  - {processed_message_args.expected_result}"
    if processed_message_args.returned_result:
        if isinstance(processed_message_args.returned_result, list):
            formatted_returned_result: str = str(
                "  - " + "\n  - ".join(map(str, processed_message_args.returned_result))
            )
        else:
            formatted_returned_result: str = f"  - {processed_message_args.returned_result}"
    if processed_message_args.suggested_resolution:
        if isinstance(processed_message_args.suggested_resolution, list):
            formatted_suggested_resolution: str = str(
                "  - " + "\n  - ".join(map(str, processed_message_args.suggested_resolution))
            )
        else:
            formatted_suggested_resolution = f"  - {processed_message_args.suggested_resolution}"
    if processed_message_args.original_exception:
        formatted_original_exception: str = str(
            "\n            "
            + "\n            ".join(map(str, str(processed_message_args.original_exception).splitlines()))
        )

    # #################################################
    # #######Constructs Message Based On Input#########
    # #################################################
    if processed_message_args.main_message:
        formatted_main_message: str = f"{processed_message_args.main_message}\n"
    else:
        formatted_main_message: str = " None: No Message Provided\n"

    if processed_message_args.expected_result:
        formatted_expected_result: str = "Expected Result:\n" + f"{formatted_expected_result}\n\n"
    else:
        formatted_expected_result: str = ""

    if processed_message_args.returned_result:
        formatted_returned_result: str = "Returned Result:\n" + f"{formatted_returned_result}\n\n"
    else:
        formatted_returned_result: str = ""

    if processed_message_args.original_exception:
        # Gets all active traceback info.
        exc_type, exc_value, exc_traceback = sys.exc_info()
        # Formats the traceback exceptions into individual sections.
        tb_sections: list[str] = traceback.format_exception(exc_type, exc_value, exc_traceback)

        formatted_non_fexception_trace_details: str = ""
        # Checks if the original exception is a previous fexception exception or external exception.
        # Nested fexception will be embedded in the original exception, so no action is required.
        if (
            "Exception:" not in str(tb_sections)
            and "Module:" not in str(tb_sections)
            and "Name:" not in str(tb_sections)
            and "Line:" not in str(tb_sections)
        ):
            # This pulls the Nested traceback (tb) line from the trackback to get the original tb point.
            # This output will contain the failure line and failure value/details on the next line.
            # Output Example:
            # File "C:\GitHub_Repositories\test_exceptions\src\l3.py", line 10, in l3_t1
            #  x
            tb_exception_output = tb_sections[-2].split("\n")
            if len(tb_exception_output) >= 1:
                # Replace Example:
                #   Original: File "C:\GitHub_Repositories\test_exceptions\src\l3.py", line 10, in l3_t1
                #   Replaced: split_tb_exception_line[0] = File "C:\GitHub_Repositories\test_exceptions\src\l3.py"
                #             split_tb_exception_line[1] = line 10
                #             split_tb_exception_line[2] = in l3_t1
                split_tb_exception_output: list[str] = str(tb_exception_output[0]).strip().split(", ")
                # Replace Example:
                #   Original: File "C:\GitHub_Repositories\test_exceptions\src\l3.py"
                #   Replaced: C:\GitHub_Repositories\test_exceptions\src\l3.py
                tb_exception_module: str = split_tb_exception_output[0].replace("File ", "").replace('"', "")

                # Checks if the module path exists.
                if os.path.exists(tb_exception_module):
                    # Gets the module name from the full path.
                    # Replace Example:
                    #   Original: C:\GitHub_Repositories\test_exceptions\src\l3.py
                    #   Replaced: l3
                    tb_exception_module = Path(tb_exception_module).stem
                else:
                    raise TBLineParseFailure(
                        "The traceback line had an invalid traceback module path. fexception expected the second to last line to hold the initiating traceback module path.\n"
                        f"  - Traceback Lines: {tb_sections}\nExiting...."
                    )  # pragma: no cover
                # Replace Example:
                #   Original: line 10
                #   Replaced: 10
                if split_tb_exception_output[1].replace("line ", "").isnumeric():
                    tb_exception_line: int = int(split_tb_exception_output[1].replace("line ", ""))
                else:
                    raise TBLineParseFailure(
                        "The traceback line has no valid line number. The traceback line has no valid line number.\n"
                        f"  - Traceback Lines: {tb_sections}\nExiting...."
                    )  # pragma: no cover
                # Replace Example:
                #   Original: in l3_t1
                #   Replaced: in l3_t1
                tb_exception_name: str = split_tb_exception_output[2].replace("in ", "")
            else:
                raise TBLineParseFailure(
                    "The returned trackback line does not contain the correct section output. fexception expected more than one line of traceback output.\n"
                    f"  - Traceback Lines: {tb_sections}\nExiting...."
                )  # pragma: no cover

            tb_reason = tb_sections[-1]
            # This pulls the exception name and exception value.
            # Replace Example:
            #   Original: NameError: name 'x' is not defined
            #   Replaced: split_tb_reason[0] = NameError
            #             split_tb_reason[1] = name 'x' is not defined
            split_tb_reason = tb_reason.split(": ")
            exception_msg = split_tb_reason[1]
            formatted_original_exception: str = str(
                "\n            " + "\n            ".join(map(str, str(exception_msg).splitlines()))
            )

            # Sets the trace details even if the limit is 0.
            # Without the trace details, the nested message would be useless with a limit of 0.
            formatted_non_fexception_trace_details: str = (
                f"            Exception Trace Details:\n"
                f"              - Exception: {type(processed_message_args.original_exception).__name__}\n"
                f"              - Module: {tb_exception_module}\n"
                f"              - Name: {tb_exception_name}\n"
                f"              - Line: {tb_exception_line}\n"
            )

        formatted_original_exception: str = (
            "Nested Exception:\n\n"
            + "            "
            + (("~" * 150) + "\n            ")
            + (("~" * 59) + "Start Nested Exception Exception" + ("~" * 59) + "\n            ")
            + (("~" * 150) + "\n            \n")
            + f"{formatted_original_exception}\n\n"
            + f"{formatted_non_fexception_trace_details}"
            + "            "
            + (("~" * 150) + "\n            ")
            + (("~" * 60) + "End Nested Exception Exception" + ("~" * 60) + "\n            ")
            + (("~" * 150) + "\n            \n")
        )
    else:
        formatted_original_exception: str = ""

    if processed_message_args.suggested_resolution:
        formatted_suggested_resolution: str = "Suggested Resolution:\n" f"{formatted_suggested_resolution}\n\n"
    else:
        formatted_suggested_resolution: str = ""

    # Sets the trace details if the limit is anything other than 0.
    if exception_args.tb_limit != 0:
        caller_name: str = exception_args.caller_name
        if str(caller_name) == "<module>":  # pragma: no cover
            caller_name = "__main__"

        formatted_trace_details: str = (
            "Exception Trace Details:\n"
            f"  - Exception: {exception_args.exception_type.__name__}\n"  # type: ignore
            f"  - Module: {exception_args.caller_module}\n"
            f"  - Name: {caller_name}\n"
            f"  - Line: {exception_args.caller_line}\n"
        )
    else:
        formatted_trace_details: str = ""

    exception_message: str = (
        formatted_main_message
        + (("-" * 150) + "\n")
        + (("-" * 65) + "Additional Information" + ("-" * 63) + "\n")
        + (("-" * 150) + "\n")
        + formatted_expected_result
        + formatted_returned_result
        + formatted_original_exception
        + formatted_suggested_resolution
        + formatted_trace_details
        + (("-" * 150) + "\n") * 2
    )
    return exception_message

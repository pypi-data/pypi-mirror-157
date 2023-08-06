"""Handle button presses to submit and preview jobs.

Preview, open a window containing the submission script JSON, and
eventually also the structure of the submission and the JSON objects
that will be sent to Conductor.

Submit, send jobs straight to Conductor.
"""
import ix
import os
import webbrowser
from cioclarisse import utils
from cioclarisse import preview_ui
from cioclarisse.submission import Submission
from cioclarisse import validation
from ciocore.validator  import ValidationError

 
def submit(*args):
    """
    Validate and submit directly.
    """
    node = args[0]
    try:
        validation.run(node)
    except ValidationError as ex:
        ix.log_error(str(ex))
        return

    with utils.waiting_cursor():
        submission = Submission(node)
        response = submission.submit()
    if response:
        show_submission_responses(response)
    else:
        ix.log_error(str("No Response"))

def write_render_package(*args):
    node = args[0]
    with utils.waiting_cursor():
        submission = Submission(node)
        submission.write_render_package()

def preview(*args):
    """
    Validate and show the script in a panel.

    Submission can be invoked from the preview panel.
    """
    node = args[0]
    with utils.waiting_cursor():
        submission = Submission(node)
    preview_ui.build(submission)


def show_submission_responses(response):
    """
    Display submission responese in a window.

    Args:
        response dict: elements contain response codes and descriptsions
    """

    if response.get("status"):
        domain = os.environ.get("CONDUCTOR_AUTH_URL", "https://dashboard.conductortech.com")
        url = "{}{}".format(domain,str(response["uri"].replace("jobs", "job")))

        result = ix.application.message_box(
            url,
            "Conductor Submission: Info",
            ix.api.AppDialog.ok(),
            ix.api.AppDialog.STYLE_OK_CANCEL
        )
        if result.is_ok():
            webbrowser.open_new(url)

        return

    msg = "Submission failed"
    ix.application.message_box(
        msg,
        "Conductor Submission: Info",
        ix.api.AppDialog.yes(),
        ix.api.AppDialog.STYLE_OK,
        )

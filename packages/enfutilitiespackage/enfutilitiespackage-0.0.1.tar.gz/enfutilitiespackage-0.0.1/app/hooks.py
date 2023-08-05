from flask import request, g
from nanoid import generate

from app import constants, settings
from app.logging import logger
from app.main import app


@app.before_request
def setup_log_context():
    """
    Initializes & Collect log_context & request_id for logging

    The log_context & request_id will get appended in each log within the request life cycle
    """
    try:
        # Initialize log_context for each request
        g.log_context = dict()

        # Extract gcp_trace from headers and use it as request_id
        gcp_trace_context = request.headers.get("X-Cloud-Trace-Context")
        if gcp_trace_context:
            gcp_trace = gcp_trace_context.split("/")[0]
            g.request_id = gcp_trace

            # Add GCP Trace Context to correlate Application Logs with CloudRun Request Logs.
            # See https://cloud.google.com/run/docs/logging#correlate-logs
            if settings.GCP_PROJECT and settings.ENABLE_TRACES:
                g.log_context["logging.googleapis.com/trace"] = f"projects/{settings.GCP_PROJECT}/traces/{gcp_trace}"
        else:
            # If the Cloud-Trace-Context is not available, generate the random request_id
            g.request_id = generate(size=12)
    except Exception as e:
        logger.warning("Failed to setup log_context", exc_info=e)
    finally:
        return None


@app.before_request
def setup_trace_id():
    """
    Setup trace_id for logging and tracking purpose.

    This method tries to extract trace_id from headers & body (in case it is triggered via PubSub),
    if the trace_id is available, it sets it to None
    If its a public-facing CloudRun, you need to generate the trace_id in this method

    The trace_id will get appended in each log within the request life cycle and
    can be accessed via `g.trace_id` to pass it further to other services for tracing
    """
    try:
        trace_id = request.headers.get(constants.TRACE_ID_HEADER, None)
        if not trace_id:
            event = request.get_json(force=True, silent=True, cache=True)
            if event:
                attributes = event["message"]["attributes"]
                trace_id = attributes.get("traceId", None)

        g.trace_id = trace_id
    except Exception as e:
        logger.warning("Failed to setup trace_id", exc_info=e)
    finally:
        return None

from http import HTTPStatus

from app import app
from app.logging import logger


@app.route("/")
def index():
    """
    Index View Function
    """
    logger.debug("Invoked")
    return dict(message="success"), HTTPStatus.OK

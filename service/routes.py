"""
Account Service

This microservice handles the lifecycle of Accounts
"""
from flask import Blueprint, jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status  # HTTP Status Codes
from flask import current_app

bp = Blueprint('routes', __name__)

############################################################
# Health Endpoint
############################################################
@bp.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK

######################################################################
# GET INDEX
######################################################################
@bp.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )

######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@bp.route("/accounts", methods=["POST"])
def create_accounts():
    """Creates an Account"""
    current_app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    location_url = url_for("routes.read_account", account_id=account.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################
@bp.route("/accounts", methods=["GET"])
def list_accounts():
    """List all Accounts"""
    current_app.logger.info("Request to list Accounts")
    accounts = Account.all()
    results = [account.serialize() for account in accounts]
    return jsonify(results), status.HTTP_200_OK

######################################################################
# READ AN ACCOUNT
######################################################################
@bp.route("/accounts/<int:account_id>", methods=["GET"])
def read_account(account_id):
    """Read a single Account"""
    current_app.logger.info("Request to read account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found.")
    return jsonify(account.serialize()), status.HTTP_200_OK

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@bp.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """Update an Account"""
    current_app.logger.info("Request to update an Account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")
    account.deserialize(request.get_json())
    account.update()
    return account.serialize(), status.HTTP_200_OK

######################################################################
# DELETE AN ACCOUNT
######################################################################
@bp.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """Delete an Account"""
    current_app.logger.info("Request to delete an Account with id: %s", account_id)
    account = Account.find(account_id)
    if account:
        account.delete()
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    current_app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )

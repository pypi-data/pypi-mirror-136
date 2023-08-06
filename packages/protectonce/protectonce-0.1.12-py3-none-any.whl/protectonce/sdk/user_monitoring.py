from ..core_interface import invoke_core_method
from ..rules.handlers import cls
from .. import common_utils
from ..instrument.po_exceptions import SecurityException


def __get_session_id():
    data = {
        "config": {
            "property": "__poSessionId"
        }
    }

    return cls.get_property(data)


def report_signup(user_name):
    """input parameters user_name as string"""
    if not isinstance(user_name, str):
        print(
            "[PROTECTONCE_ERROR] protectonce.report_signup: 'user_name' should be string")
        return

    try:
        po_session_id = __get_session_id()
        signup_data = {"args": {
            "requestId": po_session_id,
            "userName": user_name
        }}
        result, out_data_type, out_data_size = invoke_core_method(
            "userMonitoring.storeSignUpData", signup_data, len(signup_data))
        blocked = common_utils.is_action_blocked(result)
    except:
        print(
            "[PROTECTONCE_ERROR] protectonce.report_signup: Error occured while handling signup data")
    if blocked:
        raise SecurityException(f'{user_name} user is blocked')


def report_login(status, user_name):
    """input parameters status and user_name as string
    status can have value either 'success' or 'failure'"""

    if not isinstance(user_name, str) or not isinstance(status, str):
        print(
            "[PROTECTONCE_ERROR] protectonce.report_login: 'user_name' and 'status' should be string")
        return
    if status.lower() not in ['success', 'failure']:
        print("[PROTECTONCE_ERROR] protectonce.report_login: 'status' should be either 'success' or 'failure'")
        return
    try:
        po_session_id = __get_session_id()
        login_data = {"args": {
            "requestId": po_session_id,
            "status": status,
            "userName": user_name
        }}
        result, out_data_type, out_data_size = invoke_core_method(
            "userMonitoring.storeLoginData", login_data, len(login_data))
    except:
        print(
            "[PROTECTONCE_ERROR] protectonce.report_login: Error occured while handling login data")
    blocked = common_utils.is_action_blocked(result)
    if blocked:
        raise SecurityException(f'{user_name} user is blocked')


def report_auth(user_name, traits=None):
    """input parameters user_name as string traits is optional"""
    if not isinstance(user_name, str):
        print(
            "[PROTECTONCE_ERROR] protectonce.report_auth: 'user_name' should be string")
        return
    try:
        po_session_id = __get_session_id()
        auth_data = {"args": {
            "requestId": po_session_id,
            "userName": user_name
        }}
        result, out_data_type, out_data_size = invoke_core_method(
            "userMonitoring.identify", auth_data, len(auth_data))

        blocked = common_utils.is_action_blocked(result)
    except:
        print(
            "[PROTECTONCE_ERROR] protectonce.report_auth: Error occured while handling authentication data")
    if blocked:
        raise SecurityException(f'{user_name} user is blocked')

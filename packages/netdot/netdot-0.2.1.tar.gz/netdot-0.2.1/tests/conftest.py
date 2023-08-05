import pytest


@pytest.fixture(scope='module')
def vcr_config():
    return {
        'before_record_request': [sanitize_NetdotLogin_path],
        'before_record_response': [ignore_redirected_html_after_login]
    }


def ignore_redirected_html_after_login(response):
    """We do not care about responses that start with <html>. 

    We are testing data APIs, and this makes the cassettes much more readable to ignore the HTML pages returned.
    """
    try:
        if response['body']['string'].strip().startswith(b'<html>'):
            response['body']['string'] = 'BLANK (see conftest.py)'
    except TypeError:
        pass
    return response


def sanitize_NetdotLogin_path(request):
    """Clear the "body" of the request if it is sent to the /NetdotLogin path.
    """
    if request.path == '/NetdotLogin':
        request.body = 'BLANK (see conftest.py)'
    return request

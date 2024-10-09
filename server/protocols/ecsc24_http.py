import requests

from server import app
from server.models import Flag_Status, SubmitResult


RESPONSES = {
    Flag_Status.QUEUED: ['timeout', 'game not started', 'retry later', 'game over', 'is not active yet', 'is not up',
                        'no such flag'],
    Flag_Status.ACCEPTED: ['accepted', 'congrat'],
    Flag_Status.REJECTED: ['bad', 'wrong', 'expired', 'denied', 'unknown', 'your own', "flag already claimed",
                          'too old', 'not in database', 'already submitted', 'invalid flag'],
}
# The RuCTF checksystem adds a signature to all correct flags. It returns
# "invalid flag" verdict if the signature is invalid and "no such flag" verdict if
# the signature is correct but the flag was not found in the checksystem database.
#
# The latter situation happens if a checker puts the flag to the service before putting it
# to the checksystem database. We should resent the flag later in this case.


TIMEOUT = 5


def submit_flags(flags, config):
    r = requests.put(config.SYSTEM_URL,
                     headers={'X-Team-Token': config.SYSTEM_TOKEN},
                     json=[item.flag for item in flags], timeout=TIMEOUT)

    unknown_responses = set()
    resp_json = r.json()
    if "message" in resp_json:
        for flag in flags:
            yield SubmitResult(flag, Flag_Status.QUEUED, "Ratelimit")
    else:
        for item in resp_json:
            response = item['msg'].strip()
            response = response.replace('[{}] '.format(item['flag']), '')

            response_lower = response.lower()
            for status, substrings in RESPONSES.items():
                if any(s in response_lower for s in substrings):
                    found_status = status
                    break
            else:
                found_status = Flag_Status.QUEUED
                if response not in unknown_responses:
                    unknown_responses.add(response)
                    app.logger.warning('Unknown checksystem response (flag will be resent): %s', response)

            yield SubmitResult(item['flag'], found_status, response)

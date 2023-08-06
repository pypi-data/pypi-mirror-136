import json
import unittest
import responses

from decisiontelecom.viber import ViberError, ViberMessageSourceType, ViberMessageStatus, ViberMessageType
from decisiontelecom.viber_plus_sms import SmsMessageStatus, ViberPlusSmsClient, ViberPlusSmsMessage


class TestViberPlusSms(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.client = ViberPlusSmsClient("api_key")

    @responses.activate
    def test_send_message_returns_message_id(self):
        expected_message_id = 429

        responses.add(responses.POST,
                      url="https://web.it-decision.com/v1/api/send-viber",
                      body="{{\"message_id\":\"{expected_message_id}\"}}".format(
                          expected_message_id=expected_message_id),
                      status=200)

        message = ViberPlusSmsMessage(
            "", "", ViberMessageType.TextOnly, "", ViberMessageSourceType.Transactional, "SMS Text")
        message_id = self.client.send_message(message)

        self.assertEqual(expected_message_id, message_id)

    @responses.activate
    def test_send_message_returns_decision_telecom_error(self):
        expected_error = ViberError(
            "Invalid Parameter: source_addr", "Empty parameter or parameter validation error", 1, 400)

        responses.add(responses.POST,
                      url="https://web.it-decision.com/v1/api/send-viber",
                      body=json.dumps(
                          expected_error, default=lambda x: x.__dict__),
                      status=200)

        try:
            message = ViberPlusSmsMessage(
                "", "", ViberMessageType.TextOnly, "", ViberMessageSourceType.Transactional, "SMS Text")
            self.client.send_message(message)
        except ViberError as error:
            self.assertTrue(isinstance(error, ViberError))
            self.assertEqual(expected_error.name, error.name)
            self.assertEqual(expected_error.message, error.message)
            self.assertEqual(expected_error.code, error.code)
            self.assertEqual(expected_error.status, error.status)

    @responses.activate
    def test_send_message_returns_unsuccessful_status_code(self):
        responses.add(responses.POST,
                      url="https://web.it-decision.com/v1/api/send-viber",
                      body="Some general error",
                      status=500)

        try:
            message = ViberPlusSmsMessage(
                "", "", ViberMessageType.TextOnly, "", ViberMessageSourceType.Transactional, "SMS Text")
            self.client.send_message(message)
        except Exception as error:
            self.assertFalse(isinstance(error, ViberError))

    @responses.activate
    def test_get_message_status_returns_status(self):
        expected_message_id = 429
        expected_status = ViberMessageStatus.Delivered
        expected_sms_message_id = 36478
        expected_sms_status = SmsMessageStatus.Delivered

        response = {"message_id": expected_message_id, "status": expected_status.value,
                    "sms_message_id": expected_sms_message_id, "sms_message_status": expected_sms_status.value}

        responses.add(responses.POST,
                      url="https://web.it-decision.com/v1/api/receive-viber",
                      body=json.dumps(response, default=lambda x: x.__dict__),
                      status=200)

        receipt = self.client.get_message_status(expected_message_id)

        self.assertIsNotNone(receipt)
        self.assertEqual(expected_message_id, receipt.message_id)
        self.assertEqual(expected_status, receipt.status.value)
        self.assertEqual(expected_sms_message_id, receipt.sms_message_id)
        self.assertEqual(expected_sms_status, receipt.sms_message_status.value)

    @responses.activate
    def test_get_message_status_returns_decision_telecom_error(self):
        expected_error = ViberError(
            "Invalid Parameter: source_addr", "Empty parameter or parameter validation error", 1, 400)

        responses.add(responses.POST,
                      url="https://web.it-decision.com/v1/api/receive-viber",
                      body=json.dumps(
                          expected_error, default=lambda x: x.__dict__),
                      status=200)

        try:
            self.client.get_message_status(234)
        except ViberError as error:
            self.assertTrue(isinstance(error, ViberError))
            self.assertEqual(expected_error.name, error.name)
            self.assertEqual(expected_error.message, error.message)
            self.assertEqual(expected_error.code, error.code)
            self.assertEqual(expected_error.status, error.status)

    @responses.activate
    def test_get_message_status_returns_unsuccessful_status_code(self):
        responses.add(responses.POST,
                      url="https://web.it-decision.com/v1/api/receive-viber",
                      body="Some general error",
                      status=500)

        try:
            self.client.get_message_status(234)
        except Exception as error:
            self.assertFalse(isinstance(error, ViberError))

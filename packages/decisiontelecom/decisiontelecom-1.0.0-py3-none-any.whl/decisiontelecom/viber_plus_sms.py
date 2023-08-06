import enum
import json
from decisiontelecom.viber import ViberMessage, ViberMessageReceipt, ViberClient


class SmsMessageStatus(enum.IntEnum):
    """Represents SMS message status"""

    Delivered = 2
    Expired = 3
    Undeliverable = 5


class ViberPlusSmsMessage(ViberMessage):
    """Represents Viber plus SMS message"""

    def __init__(self, sender, receiver, message_type, text, source_type, text_sms, image_url=None,
                 button_caption=None, button_action=None, callback_url=None, validity_period=None):
        """Initializes ViberPlusSmsMessage object

        Args:
            sender (string): Message sender (from whom message is sent)
            receiver (string): Message receiver (to whom message is sent)
            message_type (ViberMessageType): Message type
            text (string): Message content
            source_type (ViberMessageSourceType): Message sending procedure
            text_sms ([type]): SMS message content
            image_url (string, optional): Image URL for promotional message with button caption and button action. Defaults to None.
            button_caption (string, optional): Button caption. Defaults to None.
            button_action (string, optional): URL for transition when the button is pressed. Defaults to None.
            callback_url (string, optional): URL for message status callback. Defaults to None.
            validity_period (int, optional): Life time of a message (in seconds). Defaults to None.
        """
        super().__init__(sender, receiver, message_type, text, source_type,
                         image_url, button_caption, button_action, callback_url, validity_period)
        self.text_sms = text_sms


class ViberPlusSmsMessageReceipt(ViberMessageReceipt):
    """Represents Viber plus SMS message receipt (Id and status of the particular Viber and SMS message)"""

    def __init__(self, message_id, status, sms_message_id=None, sms_message_status=None) -> None:
        """Initializes ViberPlusSmsMessageReceipt object

        Args:
            message_id (int): Viber message Id
            status (ViberMessageStatus): Viber message status
            sms_message_id (int, optional): SMS message Id. Defaults to None.
            sms_message_status (SmsMessageStatus, optional): SMS message status. Defaults to None.
        """
        super().__init__(message_id, status)
        self.sms_message_id = sms_message_id
        self.sms_message_status = None if sms_message_status == None else SmsMessageStatus(
            sms_message_status)


class ViberPlusSmsClient(ViberClient):
    """Client to work with Viber plus SMS messages"""

    def __init__(self, api_key) -> None:
        """Initializes ViberPlusSmsClient object

        Args:
            api_key (string): User access key
        """
        super().__init__(api_key)

    def send_message(self, message) -> int:
        """Sends Viber plus SMS message

        Args:
            message (ViberMessage): Viber message to send

        Returns:
            int: Id of the sent Viber message

        Raises:
            ViberError: If specific Viber error occurred
        """
        return super().send_message(message)

    def get_message_status(self, message_id) -> ViberPlusSmsMessageReceipt:
        """Returns Viber message status

        Args:
            message_id (int): Id of the Viber message (sent in the last 5 days)

        Returns:
            ViberPlusSmsMessageReceipt: Viber plus SMS message receipt object

        Raises:
            ViberError: If specific Viber error occurred
        """
        def ok_response_func(response_body):
            deserialized_json = json.loads(response_body)
            return ViberPlusSmsMessageReceipt(**deserialized_json)

        request = json.dumps({"message_id": message_id})
        return self._ViberClient__make_http_request("receive-viber", request, ok_response_func)

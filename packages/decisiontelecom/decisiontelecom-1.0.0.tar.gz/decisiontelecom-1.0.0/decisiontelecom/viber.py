import base64
import enum
import json
import requests


class ViberMessageType(enum.IntEnum):
    """Represents Viber message type"""

    TextOnly = 106
    TextImageButton = 108
    TextOnly2Way = 206
    TextImageButton2Way = 208


class ViberMessageSourceType(enum.IntEnum):
    """Represents Viber message source type"""

    Promotional = 1
    Transactional = 2


class ViberMessageStatus(enum.IntEnum):
    """Represents Viber message status"""

    Sent = 0
    Delivered = 1
    Error = 2
    Rejected = 3
    Undelivered = 4
    Pending = 5
    Unknown = 20


class ViberError(Exception):
    """Represents Viber error"""

    def __init__(self, name, message, code, status) -> None:
        """Initializes ViberError object

        Args:
            name (string): Error name
            message (string): Error message
            code (int): Error code
            status (int): Error status
        """
        super().__init__()
        self.name = name
        self.message = message
        self.code = code
        self.status = status


class ViberMessage:
    """Represents Viber message"""

    def __init__(self, sender, receiver, message_type, text, source_type, image_url=None, button_caption=None, button_action=None,
                 callback_url=None, validity_period=None):
        """Initializes ViberMessage object

        Args:
            sender (string): Message sender (from whom message is sent)
            receiver (string): Message receiver (to whom message is sent)
            message_type (ViberMessageType): Message type
            text (string): Message body
            source_type (ViberMessageSourceType): Message sending procedure
            image_url (string, optional): Image URL for promotional message with button caption and button action. Defaults to None.
            button_caption (string, optional): Button caption. Defaults to None.
            button_action (string, optional): URL for transition when the button is pressed. Defaults to None.
            callback_url (string, optional): URL for message status callback. Defaults to None.
            validity_period (int, optional): Life time of a message (in seconds). Defaults to None.
        """
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.text = text
        self.image_url = image_url
        self.button_caption = button_caption
        self.button_action = button_action
        self.source_type = source_type
        self.callback_url = callback_url
        self.validity_period = validity_period

    def toJSON(self):
        # Use mapping to change names of attributes in the result json string
        mapping = {"sender": "source_addr",
                   "receiver": "destination_addr", "image_url": "image"}
        return json.dumps({mapping.get(k, k): v for k, v in self.__dict__.items()})


class ViberMessageReceipt:
    """Represents Viber message receipt (Id and status of the particular Viber message)"""

    def __init__(self, message_id, status) -> None:
        """Initializes ViberMessageReceipt object

        Args:
            message_id (int): Viber message Id
            status (ViberMessageStatus): Viber message status
        """
        self.message_id = message_id
        self.status = ViberMessageStatus(status)


class ViberClient:
    """Client to work with Viber messages"""

    def __init__(self, api_key) -> None:
        """Initializes ViberClient object

        Args:
            api_key (string): User access key
        """
        self.api_key = api_key

    def send_message(self, message) -> int:
        """Sends Viber message

        Args:
            message (ViberMessage): Viber message to send

        Returns:
            int: Id of the sent Viber message

        Raises:
            ViberError: If specific Viber error occurred
        """
        def ok_response_func(response_body):
            return int(json.loads(response_body)["message_id"])
        request = message.toJSON()
        return self.__make_http_request("send-viber", request, ok_response_func)

    def get_message_status(self, message_id) -> ViberMessageReceipt:
        """Returns Viber message status

        Args:
            message_id (int): Id of the Viber message (sent in the last 5 days)

        Returns:
            ViberMessageReceipt: Viber message receipt object

        Raises:
            ViberError: If specific Viber error occurred
        """
        def ok_response_func(response_body):
            deserialized_json = json.loads(response_body)
            return ViberMessageReceipt(**deserialized_json)

        request = json.dumps({"message_id": message_id})
        return self.__make_http_request("receive-viber", request, ok_response_func)

    def __make_http_request(self, url, request, ok_response_func):
        BASE_URL = "https://web.it-decision.com/v1/api"

        full_url = "{base_url}/{url}".format(base_url=BASE_URL, url=url)
        headers = {
            "Authorization": "Basic " + base64.b64encode(self.api_key.encode()).decode(),
            "Content-Type": "application/json",
            "Accept": "application/json"}

        response = requests.post(full_url, data=request, headers=headers)

        # Raise exception for unsuccessful response status codes
        response.raise_for_status()

        # If response contains "name", "message", "code" and "status" words, treat it as a ViberError
        if "name" in response.text and "message" in response.text and "code" in response.text and "status" in response.text:
            deserialized_json = json.loads(response.text)
            raise ViberError(**deserialized_json)

        return ok_response_func(response.text)

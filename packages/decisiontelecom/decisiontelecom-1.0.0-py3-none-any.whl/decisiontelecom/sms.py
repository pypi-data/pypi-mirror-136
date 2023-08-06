import json
import requests
import enum
import re


class SmsMessageStatus(enum.Enum):
    """Represents SMS message status"""
    Unknown = 0
    Delivered = 2
    Expired = 3
    Undeliverable = 5
    Accepted = 6


class SmsErrorCode(enum.Enum):
    """Represents SMS error code"""
    InvalidNumber = 40
    IncorrectSender = 41
    InvalidMessageId = 42
    IncorrectJson = 43
    InvalidLoginOrPassword = 44
    UserLocked = 45
    EmptyText = 46
    EmptyLogin = 47
    EmptyPassword = 48
    NotEnoughMoney = 49
    AuthorizationError = 50
    InvalidPhoneNumber = 51


class SmsError(Exception):
    """Represens SMS error

    Attributes:
        error_code (SmsErrorCode): SMS error code

    """

    def __init__(self, error_code) -> None:
        """Initializes SmsError object

        Args:
            error_code (SmsErrorCode): SMS error code
        """
        super().__init__()
        self.error_code = error_code


class SmsBalance:
    """Represents user money balance"""

    def __init__(self, balance, credit, currency) -> None:
        """Initializes SmsBalance object

        Args:
            balance (float): Current balance amount
            credit (float): Current credit line (if opened)
            currency (string): Balance currency
        """
        self.balance = balance
        self.credit = credit
        self.currency = currency


class SmsClient:
    """Client to work with SMS messages"""
    BASE_URL = "https://web.it-decision.com/ru/js"

    def __init__(self, login, password) -> None:
        """Initializes SmsClient object

        Args:
            login (string): User login in the system
            password (string): User password in the system
        """
        self.login = login
        self.password = password

    def send_message(self, receiver, sender, text, delivery):
        """Sends SMS message

        Args:
            receiver (string): Message receiver phone number (MSISDN Destination)
            sender (string): Message sender. Could be a mobile phone number (including a country code) or an alphanumeric string
            text (string): Message body
            delivery (boolean): True if a caller needs to obtain the delivery receipt in the future (by message id)

        Returns
            int: Id of the submitted SMS message

        Raises:
            SmsError: If specific SMS error occurred
        """
        def ok_response_func(response_body) -> int:
            return int(self.__get_value_from_response_content(response_body, "msgid"))

        url = "{base_url}/send?login={login}&password={password}&phone={receiver}&sender={sender}&text={text}&dlr={dlr}".format(
            base_url=self.BASE_URL, login=self.login, password=self.password, receiver=receiver, sender=sender, text=text, dlr=int(delivery))
        return self.__make_http_request(url, ok_response_func)

    def get_message_status(self, message_id) -> SmsMessageStatus:
        """Returns SMS message delivery status

        Args:
            message_id (int): Id of the submitted SMS message

        Returns:
            SmsMessageStatus: SMS message delivery status

        Raises:
            SmsError: If specific SMS error occurred
        """
        def ok_response_func(response_body):
            response_value = self.__get_value_from_response_content(
                response_body, "status")
            return SmsMessageStatus.Unknown if response_value == "" else SmsMessageStatus(int(response_value))

        url = "{base_url}/state?login={login}&password={password}&msgid={message_id}".format(
            base_url=self.BASE_URL, login=self.login, password=self.password, message_id=message_id)
        return self.__make_http_request(url, ok_response_func)

    def get_balance(self) -> SmsBalance:
        """Returns SMS balance information

        Returns:
            SmsBalance: User SMS balance information

        Raises:
            SmsError: If specific SMS error occurred
        """
        def ok_response_func(response_body):
            # Replace symbols to be able to parse response string as json
            # Regexp removes quotation marks ("") around the numbers, so they could be parsed as float
            replaced = response_body.replace("[", "{").replace("]", "}")
            replaced = re.sub(r"\"([-+]?[0-9]*.?[0-9]+)\"", r"\1", replaced)
            encoded_json = json.loads(replaced)
            return SmsBalance(**encoded_json)

        url = "{base_url}/balance?login={login}&password={password}".format(
            base_url=self.BASE_URL, login=self.login, password=self.password)
        return self.__make_http_request(url, ok_response_func)

    def __get_value_from_response_content(self, response_content, key_property_name):
        split = response_content.replace("[", "").replace("]", "").split(",")
        result = list(map(lambda s: s.strip("\""), split))

        if result[0] != key_property_name:
            raise Exception(
                "Invalid response: unknown key '{key}'".format(key=result[0]))

        return result[1]

    def __make_http_request(self, url, ok_response_func):
        response = requests.get(url)
        response_body = response.text

        # Raise exception for unsuccessful response status codes
        response.raise_for_status()

        if response_body.startswith("[\"error"):
            error_code = int(self.__get_value_from_response_content(
                response_body, "error"))
            raise SmsError(SmsErrorCode(error_code))

        return ok_response_func(response_body)

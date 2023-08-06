IT-Decision Telecom Python SDK
===============================

Convenient Python client for IT-Decision Telecom messaging API.

[![Python package](https://github.com/IT-DecisionTelecom/DecisionTelecom-Python/actions/workflows/python-package.yml/badge.svg)](https://github.com/IT-DecisionTelecom/DecisionTelecom-Python/actions/workflows/python-package.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Requirements
-----

- [Sign up](https://web.it-decision.com/site/signup) for a free IT-Decision Telecom account
- Request login and password to send SMS messages and access key to send Viber messages
- Python version 3.8 or higher installed
- You should have an application written in Python to make use of this SDK

Installation
-----

The easiest way to install the decisiontelecom package is either via pip:

```
$ pip install decisiontelecom
```

or manually by downloading the source and run the setup.py script:

```
$ python setup.py install
```

Usage
-----

We have put some self-explanatory usage examples in the [examples](https://github.com/IT-DecisionTelecom/DecisionTelecom-Python/tree/main/examples) folder,
but here is a quick reference on how IT-Decision Telecom clients work.
First, you need to import DecisionTelecom module which corresponds to your needs:

```python
from decisiontelecom.sms import SmsClient
from decisiontelecom.viber import ViberClient
from decisiontelecom.viber_plus_sms import ViberPlusSmsClient

```

Then, create an instance of a required client. Be sure to use real login, password and access key.

```python
sms_client = SmsClient("<YOUR_LOGIN>", "<YOUR_PASSWORD>")
viber_client = ViberClient("<YOUR_ACCESS_KEY>")
viber_plus_sms_client = ViberPlusSmsClient("<YOUR_ACCESS_KEY>")
```

Now you can use created client to perform needed operations. For example, this is how you can get your SMS balance:

```python
try:
    # Call client get_balance method to get SMS balance information
    balance = sms_client.get_balance()

    # get_balance method should return SMS balance information.
    print("Balance: %f, Credit: %f, Currency: %s" % (balance.balance, balance.credit, balance.currency))
except SmsError as sms_error:
    # sms_error contains specific DecisionTelecom error with the code of what went wrong during the operation
    print("Error while getting balance information. Error code: %d (%s)" % (sms_error.error_code.value, sms_error.error_code))
except Exception as error:
    # A non-DecisionTelecom error occurred during the operation (like connection error)
    print(error)
```

### Error handling
All client methods raise an exception in case if something went wrong during the operation. It might be a general exception in case of connection error or unsuccessful response status code, for example. Or it might be a specific DecisionTelecom error with some details of what went wrong. 

SMS client methods might raise `SmsError` which contains an SMS error code.
Viber and Viber plus SMS client methods might raise `ViberError` which contains some error details like name, message, status and code.

See provided examples on how to handle specific DecisionTelecom exceptions.

#### SMS errors
SMS client methods return errors in form of the error code. Here are all possible error codes:

- 40 - Invalid number
- 41 - Incorrect sender
- 42 - Invalid message ID
- 43 - Incorrect JSON
- 44 - Invalid login or password
- 45 - User locked
- 46 - Empty text
- 47 - Empty login
- 48 - Empty password
- 49 - Not enough money to send a message
- 50 - Authentication error
- 51 - Invalid phone number

#### Viber errors
Viber and Viber plus SMS client methods return errors in form of a class with the `name`, `message`, `code` and `status` properties.

Known Viber errors are:

```json
{
  "name": "Too Many Requests",
  "message": "Rate limit exceeded",
  "code": 0,
  "status": 429
}
```

```json
{
  "name": "Invalid Parameter: [param_name]",
  "message": "Empty parameter or parameter validation error",
  "code": 1,
  "status": 400
}
```

```json
{
  "name": "Internal server error",
  "message": "The server encountered an unexpected condition which prevented it from fulfilling the request",
  "code": 2,
  "status": 500
}
```

```json
{
  "name": "Topup balance is required",
  "message": "User balance is empty",
  "code": 3,
  "status": 402
}
```
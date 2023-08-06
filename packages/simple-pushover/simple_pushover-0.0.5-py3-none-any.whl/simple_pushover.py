import os
import re
import errno
import logging
from typing import Union

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="push_notification.log", encoding="utf-8", level=logging.DEBUG
)


def get_env_value(env_variable):
    try:
        return os.environ[env_variable]
    except KeyError:
        error_msg = f"Set the {env_variable} environment variable"
        logging.error(error_msg)
        raise KeyError(error_msg)


class MessageCantBeFalseyError(Exception):
    """
    Custom error for when no text is passed to send endpoint.
    """

    def __init__(
        self, message: str = "You can't push falsey values to the endpoint."
    ) -> None:
        self.message = message
        super().__init__(self.message)


class ParameterAboveMaxLength(Exception):
    """
    Custom error for when specified parameter is above the allowed length.
    """

    def __init__(
        self,
        param_name: str,
        max_length: int,
        message: str = "The given value for the parameter: {0}, is to large (max length: {1})",
    ) -> None:
        self.message = message.format(param_name, max_length)
        super().__init__(self.message)


class PushoverAPI:
    def __init__(self) -> None:
        self.push_endpoint = "https://api.pushover.net/1/messages.json"
        self.token = get_env_value("API_TOKEN")
        self.user_key = get_env_value("USER_KEY")
        self.data_template = {
            "token": self.token,
            "user": self.user_key,
            "priority": 0,
        }

    def simple_send_push(self, message: str, priority: int = 0) -> bool:
        """
        Simple send push where just a message can be sent, priority can be changed if desired.
        """
        if not message:
            logging.error(
                "[X] Your incompetence is astounding. Sending a falsey value, shame."
            )
            raise MessageCantBeFalseyError()

        if len(message) > 1024:
            logging.error("[X] Message is to long. (Above 1024 characters)")
            raise Exception("Message is above 1024 Characters.")

        data = self.data_template.copy()
        data.update(
            {
                "priority": priority,
                "message": message,
            }
        )
        response = requests.post(self.push_endpoint, data=data)
        response_json = response.json()

        # if response is OK (200) and status is 1, the push was a success!
        if response.ok and response_json.get("status") == 1:
            logging.info("[+] Push notification was sent successfully to pushover.")
            return True
        elif not response.ok and response_json.get("token") == "invalid":
            logging.error(
                f"[!] Status: {response.status_code} | Invalid application token"
            )
            return False

    def send_push(
        self,
        message: str,
        priority: int = 0,
        title: Union[str, None] = None,
        url: Union[str, None] = None,
        url_title: Union[str, None] = None,
        attachment: Union[str, None] = None,
    ) -> bool:
        if not message:
            logging.warning(
                "[X] Your incompetence is astounding. Sending a falsey value, shame."
            )
            raise MessageCantBeFalseyError()

        if len(message) > 1024:
            logging.error("[X] Message is to long. (Above 1024 characters)")
            raise Exception("Message is above 1024 Characters.")

        data = self.data_template.copy()
        # the required pieces of the POST
        data.update(
            {
                "priority": priority,
                "message": message,
            }
        )

        # titles must be limited to 250 chars.
        if title and len(title) <= 250:
            data.update(
                {
                    "title": title,
                }
            )

        if url and len(url) <= 512:
            data.update(
                {
                    "url": url,
                }
            )
        elif url and len(url) > 512:
            logging.error("[X] URL is too LONG!")
            raise ParameterAboveMaxLength(param_name="url", max_length=512)

        # check if there is a url along with url_title otherwise no point
        if url_title and url and len(url_title) <= 100:
            data.update(
                {
                    "url_title": url_title,
                }
            )
        elif url_title and len(url_title) > 100:
            logging.error("[X] URL Title is too LONG!")
            raise ParameterAboveMaxLength(param_name="url_title", max_length=100)
        elif url_title and not url:
            logging.error(
                "[X] URL Title was provided without a URL! Questioning user's sanity..."
            )
            raise Exception("url_title is provided but no url param was given!")

        supported_exts = re.compile(".+(.gif|.png|.jpg)")
        # remember that "attachment" is the path to the file
        if attachment and os.path.exists(attachment):
            if re.match(supported_exts, attachment):
                if os.stat(attachment).st_size <= 2621440:
                    response = requests.post(
                        self.push_endpoint,
                        data=data,
                        files={
                            "attachment": (
                                "image.jpg",
                                open(attachment, "rb"),
                                "image/jpeg",
                            )
                        },
                    )
                else:
                    logging.error(
                        "[X] File provided is above the 2.5MB limit for PushOver."
                    )
                    raise Exception("File is to LARGE!")
            else:
                logging.error(
                    "[X] Invalid file extention. JPG, PNG, and GIF are only supported."
                )
                raise Exception(
                    "Bad file extention. Check logs... (You got to work for this one.)"
                )
        elif attachment and not os.path.exists(attachment):
            logging.error("[X] File path to attachment is invalid. No file found.")
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), attachment)

        else:
            response = requests.post(self.push_endpoint, data=data)

        # render json into dict
        response_json = response.json()

        # if response is OK (200) and status is 1, the push was a success!
        if response.ok and response_json.get("status") == 1:
            logging.info("[+] Push notification was sent successfully to pushover.")
            return True
        elif not response.ok and response_json.get("token") == "invalid":
            logging.error(
                f"[!] Status: {response.status_code} | Invalid application token"
            )
            return False


if __name__ == "__main__":
    api = PushoverAPI()
    print(api.push_endpoint)
    print(api.token)
    # api.simple_send_push(message="Hello World")
    # api.send_push(
    #     message="Testing full push will all params!",
    #     title="Full Push Notification Test",
    #     url="https://gitlab.com/cmhedrick",
    #     url_title="Sexy GitLab User",
    # )
    api.send_push(
        message="Testing ALL THE THINGS! \n Sticker by: @gothefOOKAway",
        title="ALL THE THINGS TEST",
        url="https://gitlab.com/cmhedrick",
        url_title="Smash Your Phone! Click HERE!",
        attachment="images/smash.png",
    )

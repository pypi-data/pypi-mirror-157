import os
import logging


class Logger:
    def __init__(self):
        pass

    @classmethod
    def format_message(cls, message, owner=None, session_id=None, auth_info=None):
        formatted_message = ""
        if owner:
            formatted_message += "Owner: " + owner + " "
        if session_id:
            formatted_message += "Session ID: " + session_id + " "
        formatted_message += message
        return formatted_message

    @classmethod
    def info(cls, message, owner=None, session_id=None, auth_info=None):
        message_to_print = cls.format_message(message, owner, session_id)
        if os.getenv('IS_DEV'):
            print(message_to_print)
        else:
            logging.info(message_to_print)

    @classmethod
    def error(cls, message, owner=None, session_id=None, auth_info=None):
        message_to_print = cls.format_message(message, owner, session_id)
        if os.getenv('IS_DEV'):
            print(message_to_print)
        else:
            logging.error(message_to_print)

    @classmethod
    def warning(cls, message, owner=None, session_id=None, auth_info=None):
        message_to_print = cls.format_message(message, owner, session_id)
        if os.getenv('IS_DEV'):
            print(message_to_print)
        else:
            logging.warning(message_to_print)

import os

LOGGER_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logger.log")
JSON_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "websites.json")
DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
TOOLKIT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "toolkit")
TEMP_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
CREDENTIALS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "token.json")
MAIL_CREDENTIALS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "token_mail.json")
CLIENT_SECRET = os.path.join(os.path.dirname(os.path.realpath(__file__)), "client_secret.json")
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "template")
MAILTO = "lost.func@gmail.com" # MAIL RECEPIENTS, separated with a comma
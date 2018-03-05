from exchange_email import ExchangeEmail
from smtp_email import SmtpEmail
from utils import getProperty

def getEmail(config):

    protocol = getProperty(config, 'email-protocol')

    if 'smtp' == protocol or 'smtpssl' == protocol:
        return SmtpEmail(config)

    if 'exchange' == protocol:
        return ExchangeEmail(config)

    raise Exception('unkown email protocol: {}'.format(protocol))


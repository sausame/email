import random
import time
import traceback

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL           # this invokes the secure SMTP protocol (port 465, uses SSL)
from smtplib import SMTP               # use this for standard SMTP protocol   (port 25, no encryption)

from utils import getProperty

class SmtpEmail:

    def __init__(self, config):

        self.enabled = False

        enabled = getProperty(config, 'email-enabled')

        if None != enabled:
            enabled = enabled.upper()
            if 'Y' == enabled or 'YES' == enabled:
                self.enabled = True

        if not self.enabled: return

        self.protocol = getProperty(config, 'email-protocol')
        self.domain = getProperty(config, 'email-domain')
        self.sender = getProperty(config, 'email-sender')
        self.username = getProperty(config, 'email-username')
        self.password = getProperty(config, 'email-password')

    def send(self, subject, content, toList, ccList=None):

        if not self.enabled: return

        msg = MIMEMultipart('alternative')

        msg['Subject'] = subject
        msg['From'] = self.sender # some SMTP servers will do this automatically, not all

        emails = []

        for user, email in toList:
            emails.append(email)

        msg['To'] = ', '.join(emails)

        if ccList is not None and len(ccList) > 0:

            ccEmails = []

            for user, email in ccList:
                ccEmails.append(email)

            msg['CC'] = ', '.join(ccEmails)

            emails += ccEmails
            
        msg.attach(MIMEText(content, 'html', 'utf-8'))

        for retries in range(5):

            try:
                if 'smtp' == self.protocol:
                    conn = SMTP(self.domain)
                elif 'smtpssl' == self.protocol:
                    conn = SMTP_SSL(self.domain)

                conn.set_debuglevel(False)
                conn.login(self.username, self.password)

                try:
                    conn.sendmail(self.sender, emails, msg.as_string())
                finally:
                    conn.quit()

                print 'Send "', subject, '" to', toList, 'and', ccList, ':', len(msg.as_string()), 'bytes. Retries', retries
                break

            except Exception, e:
                errMsg = e
                print traceback.print_exc()

            if retries < 4:
                interval = 10 * (retries + 1)

                print 'Send error: "', errMsg, '". Sleep', interval, 'seconds. Retries', retries
                time.sleep(interval)

        else:
            print 'Failed to send "', subject, '" to', toList, 'and', ccList, ':', len(msg.as_string()), 'bytes. Retries', retries



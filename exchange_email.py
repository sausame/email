# Dependences: suds python-ntlm ewsclient

import datetime
import ewsclient
import os
import random
import suds.client
import sys
import time
import traceback

from utils import getProperty
from suds import WebFault
from suds.transport.https import WindowsHttpAuthenticated

class ExchangeEmail:

    def __init__(self, config):

        self.enabled = False

        enabled = getProperty(config, 'email-enabled')

        if None != enabled:
            enabled = enabled.upper()
            if 'Y' == enabled or 'YES' == enabled:
                self.enabled = True

        if not self.enabled: return

        domain = getProperty(config, 'email-domain')
        username = getProperty(config, 'email-username')
        password = getProperty(config, 'email-password')

        for retries in range(5):

            try:
                transport = WindowsHttpAuthenticated(username=username,
                        password=password)

                self.client = suds.client.Client("https://%s/EWS/Services.wsdl" % domain,
                        transport=transport,
                        plugins=[ewsclient.AddService()])

                print 'Create email client of "', domain, '". Retries:', retries
                break

            except WebFault, f:
                errMsg = f + '\n' + f.fault

            except Exception, e:
                errMsg = e
                print traceback.print_exc()

            if retries < 4:
                interval = 10 * (retries + 1)

                print 'Create email client error: "', errMsg, '". Sleep', interval, 'seconds. Retries', retries
                time.sleep(interval)

        else:
            self.client = None
            print 'Failed to create email client of "', domain, '". Retries:', retries
            return

        # Get xml template
        runningPath = os.path.dirname(os.path.realpath(__file__))

        with open('{}/templates/createitem.xml'.format(runningPath)) as fp:
            self.template = fp.read()

    def __del__(self):
        pass

    def send(self, subject, content, toList, ccList=None):

        def toMailbox(email):
            return '''  <t:Mailbox>
                            <t:EmailAddress>{}</t:EmailAddress>
                        </t:Mailbox> '''.format(email)

        if not self.enabled or None == self.client: return

        toRecipients = '<t:ToRecipients>'

        for user, email in toList:
            toRecipients += toMailbox(email)

        toRecipients += '</t:ToRecipients>'

        if None != ccList:
            ccRecipients = '<t:CcRecipients>'

            for user, email in ccList:
                ccRecipients += toMailbox(email)

            ccRecipients += '</t:CcRecipients>'
        else:
            ccRecipients = ''

        # Replace everything in the XML template shown above with the new dynamic values
        xml = self.template.format(subject, content, toRecipients, ccRecipients)

        for retries in range(5):

            try:
                # Now that the SOAP client is connected to EWS, send this XML soap message
                result = self.client.service.CreateItem(__inject={'msg':xml})

                # Result may come as a single object or a list of objects
                if type(result.CreateItemResponseMessage) is list:
                    msgs = result.CreateItemResponseMessage
                else:
                    msgs = [result.CreateItemResponseMessage]

                for msg in msgs:

                    rspclass = msg._ResponseClass
                    rspcode = msg.ResponseCode

                    if rspclass == 'Error':
                        raise Exception('Error code: %s message: %s' % \
                                        (rspcode, msg.MessageText))
                    if rspclass != 'Success':
                        raise Exception('Unknown response class: %s code: %s' % \
                                        (rspclass, rspcode))

                    if rspcode != 'NoError':
                        raise Exception('Unknown response code: %s' % rspcode)

                time.sleep(random.random()) # Sleep a while for avoiding ddos to mail server

                print 'Send "', subject, '" to', toList, 'and', ccList, ':', len(xml), 'bytes. Retries', retries
                break

            except Exception, e:
                errMsg = e

            if retries < 4:
                interval = 10 * (retries + 1)

                print 'Send error: "', errMsg, '". Sleep', interval, 'seconds. Retries', retries
                time.sleep(interval)

        else:
            print 'Failed to send "', subject, '" to', toList, 'and', ccList, ':', len(xml), 'bytes. Retries', retries


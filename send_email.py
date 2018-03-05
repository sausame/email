#! /usr/bin/python

import os
import sys

from email_factory import getEmail

def sendFileOrContent(config, filenameOrContent, toaddrs, ccaddrs=None, subject=None):

    def toEmailList(addresses):

        emails = []

        if addresses is not None:

            addrs = addresses.split(';')

            for address in addrs:
                address = address.strip()

                pos = address.find('@')
                if pos < 0: continue

                emails.append((address[:pos], address))

        return emails

    # Is file or content?
    path = os.path.realpath(filenameOrContent)
    isFile = os.path.exists(path)

    # Subject
    if subject is None:

        if isFile:

            start = filenameOrContent.rfind('/')
            end = filenameOrContent.rfind('.')

            if start > 0:
                if end > 0:
                    subject = filenameOrContent[start+1:end]
                else:
                    subject = filenameOrContent[start+1]
            else:
                subject = filenameOrContent

        else:
            subject = filenameOrContent.strip()

    # Content
    if isFile:
        with open(path) as fp:
            content = fp.read()
    else:
        content = ''' <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
           "http://www.w3.org/TR/html4/strict.dtd">
            <html>
              <head>
                <title>{0}</title>
                <meta http-equiv="content-type" content="text/html; charset=utf-8">
              </head>
              <body>
                <pre>{0}</pre>
              </body>
            </html> '''.format(filenameOrContent)

    # To list
    toList = toEmailList(toaddrs)

    # To list
    ccList = toEmailList(ccaddrs)

    email = getEmail(config)
    email.send(subject, content, toList, ccList)

'''
Main Entry
'''
if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    if len(sys.argv) < 4:
        print 'Usage:\n\t', sys.argv[0], 'config-file filename|content email-to[;email-to] [email-cc[;email-cc]] [subject]\n'
        exit()

    if len(sys.argv) > 4:
        ccaddrs = sys.argv[4];
    else:
        ccaddrs = None

    if len(sys.argv) > 5:
        subject = sys.argv[5];
    else:
        subject = None

    sendFileOrContent(sys.argv[1], sys.argv[2], sys.argv[3], ccaddrs, subject)


#!/usr/local/bin/python

import sys
import datetime
import logging
logging.basicConfig(filename='/stud/cslec/peters43/logs/anon_feedback.log', 
                    level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p',
                    format='%(asctime)s (%(levelname)s): %(message)s')

import cgi
import html
import cgitb
cgitb.enable(display=0, logdir='/stud/cslec/peters43/logs')

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


################################################################################
# Messages
THANK_YOU_MSG = '''        <html>
        <head>
        <title>Thank You</title>
        </head>

        <body bgcolor="#ffffff" text="#000000">
        <h1>Thank You</h1>
        <p>Mail has been sent from {0}.
        </p>
        <hr>
        <p>You wrote:</p>
        <blockquote><em>{1}</em></blockquote>
        </body>
        </html>'''

INVALID_ACCOUNT_MSG = '''    <html>
    <head>
    <title>Sorry!</title>
    </head>

    <body bgcolor="#ffffff" text="#000000">
    <h1>Sorry!</h1>
    <p>The anonymous feedback page you have used is not active.
    </p>
    <p>Please inform your instructor that the feedback form is inactive,
       or send an email to <a href="http://www.google.com/recaptcha/mailhide/d?k=01sjrekIlgx4_YtV4ia9VrGw==&amp;c=uGG3x473tkr4Pk3ik9I5cUso2YMW7O_UqilRByYQpio=" onclick="window.open('http://www.google.com/recaptcha/mailhide/d?k\07501sjrekIlgx4_YtV4ia9VrGw\75\75\46c\75uGG3x473tkr4Pk3ik9I5cUso2YMW7O_UqilRByYQpio\075', '', 'toolbar=0,scrollbars=0,location=0,statusbar=0,menubar=0,resizable=0,width=500,height=300');
       return false;" title="Reveal this e-mail
       address">click for email</a>@utoronto.ca that includes the name of
       the course to which you were hoping to send feedback.
    </p>
    </body>
    </html>'''

MUST_SELECT_INSTR_MSG = '''    <html>
    <head>
    <title>Sorry!</title>
    </head>

    <body bgcolor="#ffffff" text="#000000">
    <h1>Sorry!</h1>
    <p>This course has more than one instructor, so you must select an
       instructor from the pull-down menu for your message to be delivered.
       Please close this warning to return to the form.
    </p>
    </body>
    </html>'''

NO_COMMENT_MSG = '''    <html>
    <head>
    <title>Sorry!</title>
    </head>

    <body bgcolor="#ffffff" text="#000000">
    <h1>Sorry!</h1>
    <p>No feedback was detected. Make sure you put something into the message
       field.
    </p>
    </body>
    </html>'''

INVALID_FORM_MSG = '''    <html>
    <head>
    <title>Sorry!</title>
    </head>

    <body bgcolor="#ffffff" text="#000000">
    <h1>Sorry!</h1>
    <p>It looks like you are here by mistake. This script supports anonymous
       feedback and requires specific form fields. Please contact
       <a href="http://www.google.com/recaptcha/mailhide/d?k=01sjrekIlgx4_YtV4ia9VrGw==&amp;c=uGG3x473tkr4Pk3ik9I5cUso2YMW7O_UqilRByYQpio=" onclick="window.open('http://www.google.com/recaptcha/mailhide/d?k\07501sjrekIlgx4_YtV4ia9VrGw\75\75\46c\75uGG3x473tkr4Pk3ik9I5cUso2YMW7O_UqilRByYQpio\075', '', 'toolbar=0,scrollbars=0,location=0,statusbar=0,menubar=0,resizable=0,width=500,height=300');
       return false;" title="Reveal this e-mail
       address">click for email</a>@utoronto.ca if you need help setting up
       anonymous feedback.
    </p>
    </body>
    </html>'''

INVALID_EMAIL_MSG = '''    <html>
    <head>
    <title>Sorry!</title>
    </head>

    <body bgcolor="#ffffff" text="#000000">
    <h1>Sorry!</h1>
    <p>Mail (SMTP) servers will sometimes fail to send a message. In this case, the SMTP server believes you have entered a bogus email address. Please fix the email in the address field (or omit it entirely if you do not wish to enter a valid address).
    </p>
    </body>
    </html>'''

EMAIL_ERROR_MSG = '''    <html>
    <head>
    <title>Sorry!</title>
    </head>

    <body bgcolor="#ffffff" text="#000000">
    <h1>Sorry!</h1>
    <p>Mail (SMTP) servers will sometimes fail to send a message. The admins will look at the crash report and try to fix the submission.
    </p>
    </body>
    </html>'''

################################################################################
# Mail sending functionality
def send_mail(send_to, send_from, subject, text, reply_to=None, server='127.0.0.1'):
    msg = MIMEMultipart()
    msg['to'] = send_to
    msg['from'] = send_from
    msg['subject'] = subject
    if reply_to:
        msg.add_header('reply-to', reply_to)
    msg.attach(MIMEText(text))

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


################################################################################
# Part of the CGI interface: sending a response
def print_response(text):
    print("Content-Type: text/html\n\n{0}".format(text))
    sys.exit(0)


if __name__ == "__main__":
    form = cgi.FieldStorage()
    if 'class' not in form:
       print_response(INVALID_FORM_MSG)
    if form.getvalue('class') is 'no_value_selected':
       print_response(MUST_SELECT_INSTR_MSG)
    if form.getvalue('comment', '').strip() is '':
       print_response(NO_COMMENT_MSG)
    comment = html.escape(form.getvalue('comment'))
    escaped_comment = comment.encode('ascii', errors="backslashreplace").decode()


    import anonfeedback_accounts as accounts
    send_to, expiration = accounts.accounts.get(form.getvalue('class'), (None, None))
    try:
        if not send_to or \
           (expiration and datetime.datetime.strptime(expiration, '%x').date() < datetime.date.today()):
            logging.info('Invalid account: {1}\n{2}\n=========='.format(form.getvalue('class'), escaped_comment))
            print_response(INVALID_ACCOUNT_MSG)
    except ValueError:
        # Failed date translation
        logging.error("Date could not be translated: {0}".format(expiration))
        print_response(INVALID_ACCOUNT_MSG)


    username = 'Anonymous' if form.getvalue('username', '').strip() is '' else form.getvalue('username').strip()
    user_email = 'anonymous@utoronto.ca' if form.getvalue('email', '').strip() is '' else form.getvalue('email').strip()
    send_from = '{0} <{1}>'.format(username, user_email)
    subject = 'Feedback for {0} from {1}'.format(form.getvalue('class'), username)
    body = 'Comment:\n{0}\n\nSent by: {1}'.format(comment, username)

    try:
        send_mail(send_to, send_from, subject, body)
        logging.info('Sent to {0} from {1}\n{3}\n=========='\
                     .format(form.getvalue('class'), send_from, escaped_comment))
        print_response(THANK_YOU_MSG.format(username, escaped_comment))
    except smtplib.SMTPRecipientsRefused:
        logging.info('Invalid email address ({0}) entered for message intended to {1}.'.format(send_from, form.getvalue('class')))
        print_response(INVALID_EMAIL_MSG)
    except Exception as e:
        logging.error('Unknown error occurred when sending mail for {0} from {1}\n{3}\n=========='\
                      .format(form.getvalue('class'), send_from, e))
        print_response(EMAIL_ERROR_MSG)

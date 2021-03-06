from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import sqlite3
import numpy as np

action = ''
email = ''
verifyCode = ''


def getAction(userId):
    global action
    global verifyCode
    try:
        conn = sqlite3.connect('user.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user(user_id text, step text, email text, verify_code text)''')
        c.execute('SELECT step from user where user_id = ?', (userId,))
        row = c.fetchone()
        if row is None:
            verifyCode = str(np.random.random_integers(100000, 999999, size=None))
            c.execute('INSERT INTO user VALUES (?,?,?,?)', (userId, 'sendEmail', '', verifyCode))
            action = 'sendEmail'
        else:
            action = row[0]
        conn.commit()
        conn.close()
    except Exception as e:
        print('Error: ' + str(e))


def getInfo(userId):
    global email
    global verifyCode
    try:
        conn = sqlite3.connect('user.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT email, verify_code from user where user_id = ?', (userId,))
        row = c.fetchone()
        if row is not None:
            email = row[0]
            verifyCode = row[1]
        conn.close()
    except Exception as e:
        print('Error: ' + str(e))


def start(bot, update):
    global action
    try:
        getAction(update.message.from_user.id)
        bot.send_message(update.message.chat_id, "I'm a bot, Nice to meet you!")
        
        if action != 'Done':
            action = 'sendEmail'
            bot.send_message(update.message.chat_id, "Please enter your email: ")
        else:
            bot.send_message(update.message.chat_id, 'You are verified!')
    except Exception as e:
        print('Error: ' + str(e))


def doAction(bot, update):
    global action
    global email
    global verifyCode
    getAction(update.message.from_user.id)
    getInfo(update.message.from_user.id)
    try:
        text = update.message.text
        if action == 'sendEmail':
            email = text;
            sendEmail(bot, update, text, verifyCode)
        elif action == 'insertDB':
            insertDB(bot, update, text)
        elif action == 'Done':
            bot.send_message(update.message.chat_id, 'You are verified!')
    except Exception as e:
        print('Error: ' + str(e))


def sendEmail(bot, update, receiver, verifyCode):
    global action
    getAction(update.message.from_user.id)
    sender = 'Hazyflame.quilava@gmail.com'
    password = 'hoangtunai'
    subject = 'SMTP test'

    message = MIMEText(verifyCode, 'html', 'utf-8')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = Header(subject, 'utf-8')

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.connect('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        
        action = 'insertDB'
        conn = sqlite3.connect('user.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('Update user set step = ?, email = ? where user_id = ?', ('insertDB', receiver, update.message.from_user.id))
        conn.commit()
        conn.close()
        
        bot.send_message(update.message.chat_id, 'Send email success. Please enter code in email: ')
    except smtplib.SMTPException as e:
        print('Error: ' + str(e))
        bot.send_message(update.message.chat_id, 'Send email error. Please enter your email: ')


def insertDB(bot, update, text):
    global action
    global email
    global verifyCode
    getAction(update.message.from_user.id)
    getInfo(update.message.from_user.id)
    if text == verifyCode:
        try:
            conn = sqlite3.connect('telegram.db', check_same_thread=False)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS telegram(user_id text, user_name text, name text)''')
            c.execute('INSERT INTO telegram VALUES (?,?,?)',
                       (update.message.from_user.id,
                        update.message.from_user.username,
                        update.message.from_user.last_name + ' ' + update.message.from_user.first_name))
            conn.commit()
            conn.close()
            
            action = 'Done'
            conn = sqlite3.connect('user.db', check_same_thread=False)
            c = conn.cursor()
            c.execute('Update user set step = ? where user_id = ?', ('Done', update.message.from_user.id))
            conn.commit()
            conn.close()
            
            bot.send_message(update.message.chat_id, 'Insert user success')
        except Exception as e:
            print('Error: ' + str(e))
            bot.send_message(update.message.chat_id, "Insert fail")
    else:
        bot.send_message(update.message.chat_id, "Wrong code. Please enter code in email: ")


def main():
    token = '611151625:AAFt98982QlxdELv4SNJLTOYqpVWxJfTP6s'
    updater = Updater(token)
    dispatcher = updater.dispatcher
    print("Bot started")

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    mainHandler = MessageHandler(Filters.text, doAction)
    dispatcher.add_handler(mainHandler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

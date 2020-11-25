from pyrogram import Client, filters
from datetime import datetime
import sqlite3 as sql

app = Client('bot_python')

# считываем файл config.ini
with open('config.ini', 'r') as f:
    data = f.read().splitlines()
    donor = data[3].split(' = ')[1] # список доноров
    moder = data[4].split(' = ')[1] # модерация
    channel = data[5].split(' = ')[1] # канал куда пересылаются посты

@app.on_message(filters.chat(eval(donor)))
def get_post(client, message):
    username = message.chat.username
    message_id = message.message_id

    con = sql.connect('bd.db')
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS DateBase (username, message_id)""")
    con.commit()

    # проверяем есть ли в БД такой message_id
    # если есть, то добавляем в БД и отправляем на модерку
    cur.execute("""SELECT message_id FROM DateBase WHERE message_id=?""", (message_id,))
    if not cur.fetchall():
        cur.execute("""INSERT INTO DateBase VALUES (?,?)""", (username, message_id,))
        con.commit()

        # получение последнего ROWID
        for a in cur.execute("""SELECT ROWID, * FROM DateBase LIMIT 1 OFFSET (SELECT COUNT(*) FROM DateBase)-1"""):
            last_id = a[0]

        # пересылаем пост на модерку
        message.forward(eval(moder))
        client.send_message(eval(moder), last_id)
    else:
        pass

@app.on_message(filters.chat(eval(moder)))
def send_post(client, message):
    con = sql.connect('bd.db')
    cur = con.cursor()

    # получаем запись в таблице
    for _ in cur.execute(f"""SELECT * FROM DateBase WHERE ROWID = {message.text}"""):
        username = _[0]
        msg_id = _[1]

    send = app.get_messages(username, msg_id)
    send.forward(eval(channel), as_copy=True)


if __name__ == '__main__':
    print(datetime.today().strftime(f'%H:%M:%S | Bot launched.'))
    app.run()

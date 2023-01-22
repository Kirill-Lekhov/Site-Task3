from datetime import datetime

import requests
import pymongo

from vk_name_parser import VKNameParser


client = pymongo.MongoClient("localhost", 27017)


def add_coin(string, user_id):
    client.db.coins.insert_one(
        {
            "string": string,
            "time": datetime.utcnow(),
            "user": user_id,
        },
    )


def add_transaction(amount, sender_id, recipient_id):
    if not amount or not sender_id or not recipient_id:
        return "Заполните все поля ввода"

    if sender_id == recipient_id:
        return "Нет смысла в переводе денег самому себе"

    try:
        amount = int(amount)
    except ValueError:
        return "Некорректная сумма"

    if amount <= 0:
        return "Некорректная сумма"

    if client.db.coins.find({"user": {"$eq": sender_id}}).count() < amount:
        return "Недостаточно средств"

    ids = [i["_id"] for i in client.db.coins.find({"user": {"$eq": sender_id}})[:amount]]

    for i in ids:
        client.db.coins.update({"_id": i}, {"$set": {"user": recipient_id}})
        client.db.log.insert_one(
            {
                "coin": i,
                "from": sender_id,
                "to": recipient_id,
                "time": datetime.utcnow()
            })

    return "Перевод успешно выполнен"


def check_coin(string):
    if client.db.coins.find_one({"string": {"$eq": string}}) is None:
        return True

    return False


def get_vk_name(user_id):
    server = "https://vk.com/id{id}"
    parser = VKNameParser()

    try:
        response = requests.get(server.format(id=user_id))

        if response.status_code != 200: 
            raise Exception

        content = response.content.decode(encoding='utf-8')
        parser.feed(content)
        return parser.name

    except Exception as err:
        print(err)
        return "Пользователь не найден"


def get_score(user_id):
    user = get_vk_name(user_id)
    
    if user == "Пользователь не найден":
        return user

    user_id = str(user_id)
    val = client.db.coins.count_documents({"user": {"$eq": user_id}})
    return "У пользователя {} {} KCoin'ов".format(user, str(val if val else 0))


def get_top():
    sort = {'$sort': {'total': -1}}
    agr = client.db.coins.aggregate([{'$group': {'_id': '$user', 'total': {'$sum': 1}}}, sort])
    vals = list(agr)[:10]
    return [(i + 1, get_vk_name(vals[i]["_id"]), vals[i]["total"]) for i in range(len(vals))]

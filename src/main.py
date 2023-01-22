import os
from random import *
from hashlib import md5

from flask import Flask
from flask import render_template, request
from flask import send_from_directory

import pymongo_tools


app = Flask(__name__)
RULES = '00000'


def check_hashes(hashes):
    answer = []

    for i in hashes:
        vals = i.strip().split("-", maxsplit=1)

        if len(vals) == 2 and vals[0].isdigit():
            if md5(i.strip().encode('utf8')).hexdigest()[:len(RULES)] == RULES:
                if pymongo_tools.check_coin(vals[1]):
                    answer.append((i, False))
                    pymongo_tools.add_coin(vals[1], vals[0])
                    continue

        answer.append((i, True))

    return answer


@app.route("/", methods=["GET", "POST"])
def index():
    result = []

    if request.method == "POST":
        hashes = request.form["hashes"].strip().split()
        result = check_hashes(hashes)

    return render_template("index.html", res=result, rules=RULES)


@app.route("/wallet")
def wallet():
    result = None

    try:
        wallet = request.args.get("wallet").strip()
        
        if wallet:
            if wallet[0].isdigit():
                result = pymongo_tools.get_score(wallet)
            else:
                result = "Неверный тип id"
    except:
        pass

    return render_template("wallet.html", res=result)


@app.route("/send", methods=["GET", "POST"])
def send():
    result = None

    if request.method == "POST":
        sender_id = request.form["sender_id"].strip()
        amount = request.form["amount"].strip()
        recipient_id = request.form["recipient_id"].strip()
        result = pymongo_tools.add_transaction(amount, sender_id, recipient_id)

    return render_template("send.html", res=result)


@app.route("/top")
def top():
    return render_template("top.html", res=pymongo_tools.get_top())


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'images/favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')

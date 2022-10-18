from flask import Blueprint, render_template, flash, request, redirect, url_for
from dotenv import load_dotenv
import os
import requests, random, json

load_dotenv()

views = Blueprint("views", __name__)

rand_codes = {}

faucet_api_key = os.getenv("FAUCET_API_KEY")
short_api_key = os.getenv("SHORT_API_KEY")
base_url = "https://faucetpay.io/api/v1"
base_long_url = "http://192.168.1.138:5000"

@views.route("/")
def root():
    return render_template("index.html")

@views.route("/get")
def get():
    global rand_codes
    recipient = request.args.get("recipient")
    r = requests.post(f"{base_url}/checkaddress", data={"api_key": faucet_api_key, "address": recipient, "currency": "TRX"}).json()
    if r["status"] == 200:
        rand_code = ""
        while rand_code == "" or rand_code in rand_codes:
            for _ in range(7):
                rand_code = rand_code + random.choice(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"])
        rand_codes[rand_code] = recipient
        shortend_url = requests.get(f"https://cryptoads.space/api?api={short_api_key}&url={base_long_url}/get/confirm/{rand_code}").json()
        print(shortend_url)
        shortend_url = shortend_url["shortenedUrl"]
        return render_template("go_to_short.html", shortend_url=shortend_url)
    else:
        flash("Your wallet needs to be a deposit wallet from https://faucetpay.io!", category="warning")
        return render_template("index.html")

@views.route("/get/confirm/<rand_code>")
def get_confirm(rand_code):
    global rand_codes
    if rand_code in rand_codes:
        address = rand_codes[rand_code]
        del rand_codes[rand_code]
        r =requests.post(f"{base_url}/send", data={"api_key": faucet_api_key, "amount": 0.005*10**8, "currency": "TRX", "to": address}).json()
        if r["status"] == 200:
            flash("You have succesfully received 0.005 tron!", category="message")
            return render_template("index.html")
        else:
            flash("There was an error sending you your tron.", category="error")
            return render_template("index.html")
    else:
        flash("There was an error with your request.", category="error")
        return render_template("index.html")

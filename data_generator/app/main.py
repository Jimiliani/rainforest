from fastapi import FastAPI

import string

import requests
import random

word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
words = requests.get(word_site).content.splitlines()

BASE_URL = "http://main:8000/api"
ITEMS_CREATE_URL = BASE_URL + "/items/"
USERS_CREATE_URL = BASE_URL + "/auth/users/"
TOP_UP_USER_BALANCE_URL = BASE_URL + "/top-up/{id_}/"
ORDERS_CREATE_URL = BASE_URL + "/orders/"
PAY_ORDER_URL = BASE_URL + "/orders/{id_}/pay/"
RETURN_ORDER_URL = BASE_URL + "/orders/{id_}/return/"

# in real world we will get it from the database
user_ids = []
item_ids = []
order_ids = []
payed_order_ids = []


def get_random_string(length: int = 6):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


async def generate_item():
    name = str(random.choice(words)) + " " + str(random.choice(words))
    prime_cost = random.randint(1, 1000)
    cost = prime_cost + random.randint(1, 10000)
    amount = random.randint(50, 1000)
    response = requests.post(ITEMS_CREATE_URL, json={
        "name": name,
        "prime_cost": prime_cost,
        "cost": cost,
        "amount": amount
    })
    if 200 <= response.status_code <= 299:
        item_ids.append(response.json()['id'])


async def generate_user():
    email = get_random_string(6) + "@" + get_random_string(4) + random.choice([".com", ".ru", ".ua", ".edu", ".gov"])
    password = get_random_string(12)

    response = requests.post(USERS_CREATE_URL, json={
        "email": email,
        "password": password,
    })
    if 200 <= response.status_code <= 299:
        user_ids.append(response.json()['id'])


async def top_up_user():
    user_id = random.choice(user_ids)
    requests.patch(TOP_UP_USER_BALANCE_URL.format(id_=user_id), data={'balance': random.randint(1000, 100000)})


async def generate_order():
    owner = random.choice(user_ids)
    items_in_order = list(set(random.choices(item_ids, k=random.randint(1, 100))))
    response = requests.post(ORDERS_CREATE_URL, json={
        "owner": owner,
        "items_in_order": [{
            "item": item,
            "amount": random.randint(1, 20)
        } for item in items_in_order]
    })

    if 200 <= response.status_code <= 299:
        order_ids.append(response.json()['id'])


async def pay_order():
    order_id = random.choice(order_ids)
    response = requests.post(PAY_ORDER_URL.format(id_=order_id))
    if 200 <= response.status_code <= 299:
        payed_order_ids.append(order_id)


async def return_order():
    order_id = random.choice(payed_order_ids)
    requests.post(RETURN_ORDER_URL.format(id_=order_id))


app = FastAPI()


@app.get("/")
async def main():
    return {"message": "Hello"}


@app.post("/")
async def generate_everything(count: int = 200,
                              user_creation_weight: int = 1, item_creation_weight: int = 1,
                              order_creation_weight: int = 1, top_up_user_weight: int = 1,
                              pay_order_weight: int = 1, return_order_weigth: int = 1):
    """Runs realtime generation of users, items and orders.
    'count' param stands for count of total requests directed to another service before stopping of work"""
    actions = [generate_user] * user_creation_weight + \
              [generate_item] * item_creation_weight + \
              [generate_order] * order_creation_weight + \
              [top_up_user] * top_up_user_weight + \
              [pay_order] * pay_order_weight + \
              [return_order] * return_order_weigth
    for _ in range(count):
        try:
            await random.choice(actions)()
        except IndexError:
            pass
    return {"message": "OK"}

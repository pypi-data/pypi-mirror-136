import json
import requests


def get_username(id):
    return requests.get(f"https://users.roblox.com/v1/users/{id}").json()["name"]


def add_numbers(num1, num2):
    return num1 + num2


def subtract_numbers(num1, num2):
    return num1 - num2

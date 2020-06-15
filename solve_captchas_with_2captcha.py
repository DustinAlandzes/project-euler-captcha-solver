import time
from hashlib import sha1
from io import BytesIO
from string import ascii_lowercase

import requests
from twocaptchaapi import TwoCaptchaApi

API_KEY = ""
img_dir = "test_set"


def get_captcha_image():
    url = "https://projecteuler.net/captcha/show_captcha.php"
    response = requests.get(url)
    return response.content


def solve_captcha():
    # original from the ipynb
    api = TwoCaptchaApi('')
    print(f"Balance: {api.get_balance()}")

    captcha_image_as_bytes = get_captcha_image()
    print("Got image from project euler")

    captcha = api.solve(BytesIO(captcha_image_as_bytes))
    print("Captcha submitted to 2captcha")

    answer = captcha.await_result()
    print(f"Got the answer: {answer}")

    file_name = f"{img_dir}/{sha1(captcha_image_as_bytes).hexdigest()}_{answer}.jpg"
    with open(file_name, 'wb') as f:
        f.write(captcha_image_as_bytes)
    print(f"Wrote image to {file_name}")


if __name__ == "__main__":
    # this could be two separate threads and a redis queue
    # one thread adding captchas to the queue and one checking if they are solved
    api = TwoCaptchaApi(API_KEY)
    print(f"Balance: {api.get_balance()}")

    captchas = []
    for x in range(50):
        try:
            # get captcha image
            captcha_image_as_bytes = get_captcha_image()
            print("Got image from project euler")

            # submit image to 2captcha
            captcha = api.solve(BytesIO(captcha_image_as_bytes))
            print(f"Captcha submitted to 2captcha, {len(captchas) + 1} captchas submitted")

            # add to list of captchas
            captchas.append((captcha, captcha_image_as_bytes))
        except Exception as e:
            print(repr(e))

    # while there are still captchas waiting to be solved
    while captchas:
        # loop through the remaining captchas
        for captcha, image in captchas:
            try:
                # check if there's an answer
                answer = captcha.try_get_result()
                if answer:
                    if any(letter in answer for letter in ascii_lowercase):
                        print("Letter in the answer, reporting a bad captcha, removing from queue and moving on")
                        captcha.report_bad()
                        captchas.remove((captcha, image))
                        continue

                    # if there's an answer write the image to a file
                    # with the sha 1 hash and answer as the file name
                    print(f"Got the answer: {answer}")
                    file_name = f"{img_dir}/{sha1(image).hexdigest()}_{answer}.jpg"
                    with open(file_name, 'wb') as f:
                        f.write(image)
                    print(f"Wrote image to {file_name}, {len(captchas) - 1} captchas left")
                    # remove the captcha from the list
                    captchas.remove((captcha, image))

            except Exception as e:
                print(repr(e))
                captchas.remove((captcha, image))

        # if there are still captchas waiting to be solved wait 15 seconds then try again
        if captchas:
            print("Sleeping for 15 seconds")
            time.sleep(15)

    print("Solve all captcha images")

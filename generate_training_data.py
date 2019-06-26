import requests


def get_captcha_image():
  url = "https://projecteuler.net/captcha/show_captcha.php"
  response = requests.get(url)
  return response.content


def generate_captcha_images(n=100):
  for x in range(n):
    image_as_bytes = get_captcha_image()
    path = f"new_captcha_images/{x}.jpg"
    with open(path, "wb+") as file:
        file.write(image_as_bytes)


generate_captcha_images()
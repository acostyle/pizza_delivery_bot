<p align="center">
  <a href="https://github.com/acostyle/fish_shop_bot">
    <img src="http://www.vectorico.com/download/social_media/Telegram-Icon.png" alt="Logo" width="80" height="80">
  </a>
</p>

<h3 align="center">Pizza delivery bot</h3>

<p align="center">
  <a href="https://github.com/acostyle/fish_shop_bot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/acostyle/fish_shop_bot?style=for-the-badge" alt="MIT License"></a>
</p>

## Table of content

- [About the project](#about-the-project)
- [Installation](#installation)
- [How to run](#how-to-run)
- [License](#license)


## About the project

Bot for pizzeria. You can buy pizza and pizzeria will deliver it to you.

#### Demonstration of the bot

![](https://media.giphy.com/media/vLtbRSm63yKwtSvbVV/giphy.gif)

## Installation

* Create your CMS [here](https://www.elasticpath.com)
* Clone github repository:
```bash
git clone git@github.com:acostyle/pizza_delivery_bot.git
```
* Go to folder with project:
```bash
cd pizza_delivery_bot
```
* Install dependencies:
```bash
pip install -r requirements.txt
```
* Create a bot in Telegram via [BotFather](https://t.me/BotFather), and get it API token;
* Create a `.env` file with the following content:
```.env
CLIENT_ID=<CLIENT ID>
CLIENT_SECRET=<CLIENT SECRET>
TELEGRAM_BOT_TOKEN=<TELEGRAM BOT TOKEN>
REDIS_PASSWORD=<REDIS DB PASSWORD>
REDIS_HOST=<REDIS DB HOST>
REDIS_PORT=<REDIS DB PORT>
YA_API_KEY=<YANDEX GEOCODER TOKEN>
TRANZZO_PAYMENT=<TRANZZO PAYMENT TOKEN FROM BOTFATHER>
```

## How to run

```bash
python telegram_bot.py
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/acostyle/pizza_delivery_bot/blob/main/LICENSE) file for details.

# KeywordScrapeBot

This is a simple Telegram bot I built for fun and personal use. It allows users to register for updates about a web
page's content. More precisely, it monitors the appearance of new links, eventually filtering on some keywords.

```gitignore
# Check "https://www.awesome-blog.com" every 60 minutes
# for links containing "interesting", and write me back if you find one.
/add https://www.awesome-blog.com 60 interesting
```

This is not designed to support large traffic, and again, it is for personal use. There is no guarantee the bot will
be actually running at any given time under this name. I allow and actually encourage you to use this code for
yourself. Maybe host the bot under another name, maybe improve the code before doing so, your choice.

## Setup

### Dependencies

This bot has a few external dependencies, found in `requirements.txt`:

- [Selenium](https://pypi.org/project/selenium/): the biggest one. Used to render Javascript in web pages.
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): used for scraping (needless, will remove).
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot): duh.

Due to Selenium needing to interface with an actual browser, you will need a driver. For instance, in case you use
Firefox, you will need [geckodriver](https://github.com/mozilla/geckodriver). Just put it anywhere in your path (e.g.
the bot directory). If you wish to use another browser, just snoop around in `utils.py`:

```python
def get_firefox():
    options = Options()
    options.headless = True
    return webdriver.Firefox(options=options)  # <- Just change this (browser options may vary).
```

### Config

Add a configuration file `config.json` in your working directory:

```json
{
  "bot_token": "your bot token, see: https://core.telegram.org/bots",
  "database_file": "whateveryouwant.db"
}
```

That's it, you should be good to go.

## Improvements

In case you want to improve this bot for your own use, I suggest looking into the following:

- Selenium alternative: this package is really slow because it requires an entire browser to run. Definitely not
efficient. I was using [requests-html](https://pypi.org/project/requests-html/) but dropped it due to issues with
multithreading and coroutines.
- Storage: the storage mechanism is just some hardcoded queries to an SQLite database. I did it mainly out of
personal spite towards JSON-based solutions, you may as well tweak this into something more of your liking.
- Scheduling: job scheduling is handled by the Telegram bot api. You may want to implement your own mechanism.
- There are no tests because this took me a few days to stitch together. Do not misinterpret this: if you plan on
turning this into something bigger, write some tests.

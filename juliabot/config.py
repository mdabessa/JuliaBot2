from environs import Env
from os import environ
import time


env = Env()
env.read_env()

DATABASE_URL = environ["DATABASE_URL"]
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")


try:
    DISCORD_TOKEN = environ["DISCORD_TOKEN"]
except KeyError:
    DISCORD_TOKEN = ""

try:
    PREFIX = environ["PREFIX"]
except KeyError:
    PREFIX = "!"

try:
    ANIME_SCRAP_TIME = int(environ["ANIME_SCRAP_TIME"])
except KeyError:
    ANIME_SCRAP_TIME = 3600

try:
    TZ = environ["TZ"]
except KeyError:
    TZ = "UTC"


# Jikan's rate limit is per IP, so the default limit (60 requests per minute) should be split across all services (DiscordBot and Scraper)
try:
    BOT_JIKAN_RATE_LIMIT = int(environ["BOT_JIKAN_RATE_LIMIT"])
except KeyError:
    BOT_JIKAN_RATE_LIMIT = 50

try:
    SCRAP_JIKAN_RATE_LIMIT = int(environ["SCRAP_JIKAN_RATE_LIMIT"])
except KeyError:
    SCRAP_JIKAN_RATE_LIMIT = 10


try:
    time.tzset()
except AttributeError:
    print("tzset() not available on Windows")

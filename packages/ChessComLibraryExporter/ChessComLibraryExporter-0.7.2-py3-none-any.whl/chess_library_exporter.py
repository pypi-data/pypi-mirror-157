from __future__ import annotations

import os
import time
import argparse

from pathlib import Path
from getpass import getpass
from dataclasses import dataclass, field

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from dotenv import load_dotenv
from pathvalidate import sanitize_filename


__version__ = "0.7.2"


@dataclass
class Game:
    title: str
    link: str
    pgn: str


@dataclass
class Collection:
    title: str
    link: str
    games: list[Game] = field(default_factory=list)


def _safe_find(driver, *args, method: str = "find_elements", timeout: int = 20):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located(args))
    return getattr(driver, method)(*args)


def find_game_title(game: WebElement) -> str:
    try:
        _title = game.find_element(By.CLASS_NAME, "game-item-title")
        title = _title.text
    except NoSuchElementException:
        _usernames = game.find_elements(By.CLASS_NAME, "game-item-username")
        title = " - ".join(u.text for u in _usernames)
    return title


def find_game_pgn(driver: WebDriver, game_details_box: WebElement) -> str:
    share_button = game_details_box.find_element(By.CSS_SELECTOR, '[aria-label="Share"]')
    share_button.click()
    embed_component = _safe_find(
        driver, By.CLASS_NAME, "share-menu-tab-embed-component", method="find_element"
    )
    pgn = embed_component.get_attribute("pgn")
    close_share_modal = _safe_find(
        driver, By.CLASS_NAME, "ui_outside-close-component", method="find_element"
    )
    close_share_modal.click()
    return pgn


def load_games_from_page(driver: WebDriver, games: list[WebElement]) -> list[Game]:
    game_objects = []
    for game in games:
        toggle = game.find_elements(By.TAG_NAME, "td")[0]
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(toggle)
        ).click()  # Expands _game_details_box
        _game_details_box = game.parent.find_element(By.CLASS_NAME, "game-details-more")
        link = _game_details_box.find_element(By.CSS_SELECTOR, "a.game-details-btn-component")
        obj = Game(
            title=find_game_title(game),
            link=link.get_attribute("href"),
            pgn=find_game_pgn(driver, _game_details_box),
        )
        game_objects.append(obj)
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(toggle)
        ).click()  # Collapses _game_details_box
        print(f"\t- {obj.title} ({obj.link})")

    return game_objects


def get_next_page_button(driver: WebDriver) -> None | WebElement:
    try:
        _next_page_button = driver.find_element(
            By.CSS_SELECTOR, '.ui_pagination-item-component[aria-label="Next Page"]'
        )
        if not _next_page_button.get_attribute("disabled"):
            return _next_page_button
    except NoSuchElementException:
        return None
    return None


def wait_next_page_load():
    # FIXME: Instead of sleeping an arbitrary ammount, some kind of check should be performed on the UI.
    # maybe tracking the current page and checking the specific page selector styling.
    time.sleep(1)


class Scrapper:
    def __init__(self, driver: WebDriver):
        self.driver: WebDriver = driver
        self.collections: list[Collection] = []

    def scrape(self, username: str, password: str):
        self._login(username, password)
        self._retrieve_collections_lazy()
        self._populate_games_into_collections()
        self._end()

    def _login(self, username: str, password: str):
        self.driver.get("https://www.chess.com/home")
        username_input = self.driver.find_element(By.ID, "username")
        username_input.send_keys(username)
        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 20).until_not(
            EC.presence_of_element_located((By.ID, "password"))
        )

    def _retrieve_collections_lazy(self):
        self.driver.get("https://www.chess.com/library")
        self._retrieve_collections_in_page()
        next_page_button = get_next_page_button(self.driver)
        while next_page_button:
            next_page_button.click()
            wait_next_page_load()
            self._retrieve_collections_in_page()
            next_page_button = get_next_page_button(self.driver)

    def _retrieve_collections_in_page(self):
        collections = _safe_find(
            self.driver, By.CLASS_NAME, "library-collection-item-component"
        )
        for collection in collections:
            title = collection.find_element(By.CLASS_NAME, "library-collection-item-link")
            obj = Collection(title=title.text, link=title.get_attribute("href"))
            self.collections.append(obj)
            print(f"Found collection: '{obj.title}' ({obj.link})")

    def _populate_games_into_collections(self):
        for collection in self.collections:
            self._populate_games_into_collection(collection)

    def _populate_games_into_collection(self, collection: Collection):
        print(f"Retrieving games from: '{collection.title}' ({collection.link})")
        self.driver.get(collection.link)
        self._populate_page_into_collection(collection)
        next_page_button = get_next_page_button(self.driver)
        while next_page_button:
            next_page_button.click()
            wait_next_page_load()
            self._populate_page_into_collection(collection)
            next_page_button = get_next_page_button(self.driver)

    def _populate_page_into_collection(self, collection: Collection):
        try:
            self.driver.find_element(By.CLASS_NAME, "collection-games-wrapper-no-games")
            return
        except NoSuchElementException:
            pass
        games = _safe_find(self.driver, By.CLASS_NAME, "game-item-component")
        game_objects = load_games_from_page(self.driver, games)
        collection.games.extend(game_objects)

    def _end(self):
        self.driver.close()


def _get_next_filename(file: Path):
    i = 1
    base, ext = os.path.splitext(file)
    while file.exists():
        file = Path(f"{base}_({i}){ext}")
        i += 1
    return file


class ScrapperAutoSaver(Scrapper):
    def __init__(self, driver: WebDriver, output: Path):
        super().__init__(driver)
        self.outdir = output

    def _retrieve_collections_lazy(self):
        super()._retrieve_collections_lazy()
        for collection in self.collections:
            directory = self.outdir / sanitize_filename(collection.title)
            directory = _get_next_filename(directory)
            directory.mkdir()

    def _populate_games_into_collection(self, collection: Collection):
        super()._populate_games_into_collection(collection)
        for game in collection.games:
            file = self.outdir / sanitize_filename(collection.title)
            file /= sanitize_filename(f"{game.title}.pgn")
            file = _get_next_filename(file)
            file.write_text(game.pgn, encoding="utf-8")


def _chrome_driver(headless: bool = False) -> webdriver.Chrome:
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    opts = Options()
    if headless:
        print("WARNING: Headless mode on Chrome might break. Turn off with -H parameter.")
        opts.headless = True
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def _firefox_driver(headless: bool = False) -> webdriver.Firefox:
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options
    from webdriver_manager.firefox import GeckoDriverManager

    service = FirefoxService(GeckoDriverManager().install())
    opts = Options()
    if headless:
        opts.headless = True
    return webdriver.Firefox(service=service, options=opts)


DRIVERS = {
    "chrome": _chrome_driver,
    "firefox": _firefox_driver,
}


def parser() -> argparse.ArgumentParser:
    def dir_type(value):
        path = Path(value)
        if not path.exists():
            path.mkdir(exist_ok=True)
        if not path.is_dir():
            print(f"ERROR!\n'{path}' is not a directory.")
            raise ValueError(f"'{path}' is not a directory")
        if len(list(path.glob("*"))) > 0:
            print(f"ERROR!\nDirectory '{path}' not empty.")
            raise ValueError(f"Directory {path} not empty")
        return path

    parser = argparse.ArgumentParser(
        description="Download your whole Chess.com Library (chess.com/library)"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Directory where your library will be exported",
        type=dir_type,
        default="library",
    )
    parser.add_argument(
        "-b",
        "--browser",
        help="Browser driver to be used",
        type=str,
        required=False,
        choices=DRIVERS.keys(),
        default="firefox",
    )
    parser.add_argument(
        "-H",
        "--headless",
        help="Disable headless mode (show browser GUI)",
        action="store_false",
    )
    return parser


def _get_credentials() -> tuple[str, str]:
    load_dotenv()
    username = os.environ.get("CHESS_COM_LIBRARY_EXPORTER_USER", "")
    password = os.environ.get("CHESS_COM_LIBRARY_EXPORTER_PASS", "")
    if username == "" or password == "":
        username = input("Username: ")
        password = getpass()
    return username, password


def main():
    args = parser().parse_args()
    username, password = _get_credentials()
    driver_factory = DRIVERS[args.browser]
    driver = driver_factory(args.headless)
    scrapper = ScrapperAutoSaver(driver, args.output)
    scrapper.scrape(username, password)


if __name__ == "__main__":
    main()

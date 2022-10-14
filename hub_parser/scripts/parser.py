import requests
import time
import datetime
from bs4 import BeautifulSoup as Bs
import aiohttp
import asyncio
from config import host, user, password, db_name, port_id
import argparse

import postgreDB


class Article:
    """
    Article constractor
    """

    def __init__(self, title, date, author, author_link, post_link, hubs, content):
        """Initialization.

        :param title: Title of article
        :type title: str
        :param date: Date of posting
        :type date: str
        :param post_link: Link to article
        :type post_link: str
        :param author: Author of the article
        :type author: str
        :param author_link: Link to author's page
        :type author_link: str
        :param hubs: Hubs of article
        :type hubs: list[str]
        :param content: Content from the page
        :type content: str
        """
        self.title = title
        self.date = date
        self.author = author
        self.authorLink = author_link
        self.postLink = post_link
        self.hubs = hubs
        self.content = content


async def get_page_data(session, page, page_count, articles_list):
    """
    Fills articleObject with data from page.
    articleObject = Article(title, date, author, author_link, postLink, hubs, content)

    :param articles_list: new article
    :param session: aiohttp.client.ClientSession()
    :param page: Article page
    :type page: (str,int)
    :param page_count: Amount of pages
    :type page_count: int

    :return: articlesList.append(articleObject)
    :rtype: list[articleObject]
    """
    async with session.get(page[0]) as response:
        response_text = await response.text()
        article = Bs(response_text, "html.parser").find("article")
        title = article.find("h1").text
        date = article.find("span", class_="tm-article-snippet__datetime-published").find("time").get("title")
        post_link = page[0]
        author = article.find("a", class_="tm-user-info__username").get_text(strip=True)
        author_link = "https://habr.com" + article.find("a", class_="tm-user-info__username").get("href")
        hubs = parse_habs(article)
        content = str(article.find("div", xmlns="http://www.w3.org/1999/xhtml"))
        data = Article(title, date, author, author_link, post_link, hubs, content)
        articles_list.append(data)
        print(f"Обработана ссылка: {page[1]}/{page_count}")
        print(time.time())
        print("________________________________________________________________")


async def gather_data(pages, articles_list):
    """ Simultaneous execution of several tasks.

    :param articles_list: Result articles
    :param pages: New article pages
    :type pages: list[tuple]

    :return: list of ready-made results
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in pages:
            task = asyncio.create_task(get_page_data(session, page, len(pages), articles_list))
            tasks.append(task)
        await asyncio.gather(*tasks)
        await asyncio.sleep(.25)


def parse_habs(article):
    """ Parse habs on page to list of habs.

    :param article: Article page

    :return: hubs with hrefs separated by comma
    :rtype: list of str
    """
    span_habs = article.find_all("span", class_="tm-article-snippet__hubs-item")
    hubs = []
    for span_hub in span_habs:
        hub = span_hub.find("a", class_="tm-article-snippet__hubs-item-link").text
        link = span_hub.find("a", class_="tm-article-snippet__hubs-item-link").get("href")
        hubs.append(hub + ": https://habr.com" + link)
    return ', '.join(hubs)


def get_pages(request):
    """Parse main page and gets article links

    :return: article links from main page
    :rtype: list[tuple[str, int]]
    """
    articles = Bs(request.text, "html.parser").find_all("article")
    pages = []
    num_of_page = 0
    for article in articles:
        num_of_page += 1
        page = (
            "https://habr.com" + article.find("a", class_="tm-article-snippet__title-link").get("href"), num_of_page)
        pages.append(page)
    return pages


def print_results(articles):
    """Console articles info.

    :param articles: Article objects to print
    :type articles: list of Article
    """
    for article_info in articles:
        print(f"Название: {article_info.title}")
        print(f"Дата: {article_info.date}")
        print(f"Автор: {article_info.author}")
        print(f"Ссылка на автора: {article_info.authorLink}")
        print(f"Ссылка на статью: {article_info.postLink}")
        print(f"Содержание статьи: {article_info.content}")
        print(f"Хабы: {article_info.hubs}")
        print("________________________________________________________________")


def check_pages_in_db(pages, db_links):
    """Сhecks if there is a link in the database.

    :param pages: list of links from page ("link", id)
    :type pages: list of tuple
    :param db_links: list of links from database
    :type db_links: list of str

    :return: list of unique pages
    :rtype: list[tuple]
    """
    pages_without_duplicates = []
    for page in pages:
        if page[0] not in db_links:
            pages_without_duplicates.append(page)
    return pages_without_duplicates


def parser():
    """
    Adds new articles to database.
    """
    articles_list = []
    request = requests.get("https://habr.com/ru/all/")
    print(f"Request code: {request.status_code}")
    pages = get_pages(request)
    connection = postgreDB.create_connection(
        host, user, password, db_name, port_id
    )
    db_links = postgreDB.get_links(connection)
    pages_without_duplicates = check_pages_in_db(pages, db_links)
    if len(pages_without_duplicates) != 0:
        print(f"Found new articles: {len(pages_without_duplicates)}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(gather_data(pages_without_duplicates, articles_list))
        print_results(articles_list)
        postgreDB.add_data_to_table(articles_list)
    else:
        print(f"No new articles: {datetime.datetime.now()}")


def start_parser(crawl_time):
    """Starts parsing every crawl_time seconds.

    :param crawl_time: hab crawl time in seconds
    """
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        while True:
            start_time = time.time()
            parser()
            finish_time = time.time() - start_time
            print(f"Parser finished in {finish_time}")
            time.sleep(crawl_time - round(finish_time))
    except KeyboardInterrupt:
        print("Parser stopped")


if __name__ == '__main__':
    argsParser = argparse.ArgumentParser(description="Parse habs")
    argsParser.add_argument(
        '-t',
        '--crawl_time',
        type=int,
        default=600,
        help='hab crawl time in seconds(default 600)'
    )
    arg = argsParser.parse_args()
    start_parser(arg.crawl_time)

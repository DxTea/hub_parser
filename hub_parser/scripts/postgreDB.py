import psycopg2
from psycopg2 import OperationalError
from config import host, user, password, db_name, port_id


def create_connection(_host, _user, _password, _db_name, _port_id):
    """Connecting to database.

    :param _host: host name
    :type _host: str
    :param _user: user name
    :type _user: str
    :param _password: password
    :type _password: str
    :param _db_name: database name
    :type _db_name: str
    :param _port_id: port id
    :type _port_id: str

    :return: connection to database
    """
    connection = None
    try:
        connection = psycopg2.connect(
            host=_host,
            user=_user,
            password=_password,
            dbname=_db_name,
            port=_port_id
        )
        connection.autocommit = True
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection


def create_query(connection, query):
    """Creating query to database

    :param connection: connection to database
    :param query: query to database
    :type query: str
    """
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")

    except OperationalError as e:
        print(f"The error '{e}' occurred")


def prepare_data(articles_list):
    """Preparing articles to be added
    
    :param articles_list: new articles
    
    :return: articles
    :rtype: list of tuple
    """
    articles = []
    for article in articles_list:
        articles.append((
                        article.title, article.date, article.author, article.authorLink, article.postLink, article.hubs,
                        article.content))
    return articles


def get_links(connection):
    """Get links from database.

    :param connection: connection to database

    :return: links from database
    :rtype: list[str]
    """
    connection.autocommit = True
    cursor = connection.cursor()
    query = "SELECT postLink FROM articles"
    cursor.execute(query)
    all_post_links = cursor.fetchall()
    list_of_links = []
    for link in all_post_links:
        link = link[0]
        list_of_links.append(link)
    return list_of_links


def create_table():
    """
    Creating table
    """
    connection = create_connection(
        host, user, password, db_name, port_id
    )
    create_table_query = '''CREATE TABLE articles(
                    id serial PRIMARY KEY,
                    title varchar(255) NOT NULL,
                    date timestamp NOT NULL,
                    author varchar(255) NOT NULL,
                    authorLink varchar(255) NOT NULL,
                    postLink varchar(255) NOT NULL,
                    hubs text,
                    content text )'''
    create_query(connection, create_table_query)
    print("Database created")


def drop_table():
    """
    Deleting table
    """
    connection = create_connection(
        host, user, password, db_name, port_id
    )
    create_table_query = 'DROP TABLE articles'
    create_query(connection, create_table_query)
    print("Database deleted")


def add_data_to_table(data):
    """Adding data to table

    :param data: new articles
    :type data: list
    """
    connection = create_connection(
        host, user, password, db_name, port_id
    )
    articles_data = prepare_data(data)
    articles_query = ", ".join(["%s"] * len(articles_data))
    insert_query = (
        f"INSERT INTO articles(title, date, author, authorLink, postLink, hubs, content) VALUES{articles_query}"
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(insert_query, articles_data)
    get_links(connection)
    print("Data added to database")

# create_table()
# drop_table()

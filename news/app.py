from flask import Flask

from news.news_api.route_news import main

app = Flask(__name__)
app.register_blueprint()





if __name__ == '__main__':
    main()

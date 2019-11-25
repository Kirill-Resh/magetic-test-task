from flask import Flask
from main import PrintGames

app = Flask(__name__)


@app.route('/TEST/test.html')
def print_games():
    table = PrintGames(mode='server').print()
    return table


if __name__ == '__main__':
    app.run()

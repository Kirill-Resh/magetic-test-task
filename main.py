import requests
from bs4 import BeautifulSoup
import re
from functools import reduce
import os


class GoogleGameParser:
    def __init__(self):
        self.domain = 'https://play.google.com'

    def parse_category_page(self, category_soup, category_name):
        # best option that i find to get all games on page
        game_pattern = '^/store/apps/details?'
        raw_games = category_soup.find_all('a', href=re.compile(game_pattern))
        # filter trash links where have no game name
        games = list(filter(lambda game: True if len(game.text) > 0 else False, raw_games))
        games_data = [{'game_name': game.text.strip(),
                       'game_link': f'{self.domain}{game["href"]}',
                       'game_category': category_name} for game in games]
        return games_data

    def get_category_games(self, category_path, category_name):
        category_response = requests.get('{domain}{category_path}'.format(domain=self.domain,
                                                                          category_path=category_path))
        category_soup = BeautifulSoup(category_response.text, 'lxml')
        games_data = self.parse_category_page(category_soup, category_name)
        return games_data

    def get_games(self):
        # remove text which is always present
        category_trash_text = 'Check out more content from '
        categories_path = '/store/apps/category/GAME'
        categories_response = requests.get('{domain}{categories_path}'.format(domain=self.domain,
                                                                              categories_path=categories_path))
        categories_soup = BeautifulSoup(categories_response.text, 'lxml')
        # find 'See more' buttons which have links to category page
        categories = categories_soup.find_all('a', text='See more')
        categories_data = list(map(lambda category: self.get_category_games(category['href'],
                                                                       category['aria-label'].replace(
                                                                           category_trash_text, '')), categories))
        # just sum all list in one
        categories_data_flat = reduce(lambda first, second: first+second, categories_data)
        return categories_data_flat

    def parse(self):
        all_games = self.get_games()
        return all_games


class PrintGames:
    def __init__(self, mode='local'):
        self.games_data = GoogleGameParser().parse()
        self.mode = mode

    def local_print(self):
        for game in self.games_data:
            # create category directory if not exists
            if not os.path.exists(game['game_category']):
                os.makedirs(game['game_category'])
            game_id = game['game_link'].split('id=')[1]
            # create empty file with game_name as file name
            open('{category_name}/{game_id}'.format(category_name=game['game_category'],
                                                    game_id=game_id), 'w').close()
        print('\n, '.join([game['game_name'] for game in self.games_data]))

    def server_print(self):
        # i'm not a web dew so use only 1 way i know to create templates
        table_template = """
        <table border="1">
           <caption>Games Table</caption>
           <tr>
            <th>Game Name</th>
            <th>Game Link</th>
            <th>Game Category</th>
           </tr>
            {rows}
          </table>
        """
        # row template
        row_template = '<tr><td><a href="{game_link}">{game_name}</a></td><td>{game_link}</td><td>{' \
                       'game_category}</td></tr> '
        html_rows = [row_template.format(game_name=game['game_name'],
                                         game_link=game['game_link'],
                                         game_category=game['game_category']) for game in self.games_data]
        table = table_template.format(rows='\n'.join(html_rows))
        return table

    def print(self):
        if self.mode == 'local':
            self.local_print()
        elif self.mode == 'server':
            return self.server_print()


if __name__ == '__main__':
    PrintGames(mode='local').print()
import requests
import os

from bs4 import BeautifulSoup


URL_REPEC_MAIN_PAGE = 'https://genealogy.repec.org/'
URL_REPEC_GENEALOGY_LIST = URL_REPEC_MAIN_PAGE + 'list.html'
URL_ECONPAPERS_MAIN_PAGE = 'http://econpapers.repec.org/RAS/'  # Completar com código de autor (e.g. paa6.html)
URL_IDEAS_MAIN_PAGE = 'http://ideas.repec.org/e/'  # Completar com código de autor (e.g. paa6.html)


def get_authors_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    links = soup.find_all('a')

    tuple_list_author_link = []

    for a in links:
        if isinstance(a.contents, list) and len(a.contents) == 1 and isinstance(a.contents[0], str):
            a_name = a.contents[0].strip()
            a_link = a.attrs.get('href', '').strip()
            if ',' in a_name:
                tuple_list_author_link.append((a_name, a_link))

    return tuple_list_author_link


def get_page(url):
    r = requests.get(url)
    return r.content.decode()


def save_page(data, author_code, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(folder + '/' + author_code, 'w') as f:
        f.write(data)


def load_state():
    existing_files = set()

    try:
        with open('done.txt') as fi:
            for l in fi:
                existing_files.add(l.strip())
    except FileNotFoundError as e:
        pass

    retry_list_genealogy = check_files('genealogy', 250)
    retry_list_ideas = check_files('ideas', 250)
    retry_list_econpapers = check_files('econpapers', 250)

    retry_list = retry_list_ideas.union(retry_list_genealogy.union(retry_list_econpapers))

    return existing_files.difference(retry_list)


def check_files(path, file_size_limit):
    retry_list_author_code = set()

    for f in os.listdir(path):
        if os.stat(os.path.join(path, f)).st_size < file_size_limit:
            retry_list_author_code.add(f)
    return retry_list_author_code


def save_state(author_code):
    with open('done.txt', 'a') as fi:
        fi.write(author_code + '\n')


if __name__ == '__main__':
    print('Obtendo links de autores')
    authors_links = get_authors_links(URL_REPEC_GENEALOGY_LIST)

    state_set = load_state()
    if state_set:
        print('Reiniciando com %d já coletados' % len(state_set))

    for al in authors_links:
        a_name, a_page = al
        a_code = a_page.split('/')[-1]
        a_code_adapted = a_code.replace('.html', '.htm')

        if a_code not in state_set:
            print('Coletando (%s, %s)' % (a_name, a_code))

            a_profile_page = get_page(URL_REPEC_MAIN_PAGE + a_page)
            print('\tGenealogia')
            save_page(a_profile_page, a_code, 'genealogy')

            a_econpaper_page = get_page(URL_ECONPAPERS_MAIN_PAGE + a_code_adapted)
            print('\tEconpapers')
            save_page(a_econpaper_page, a_code, 'econpapers')

            a_ideas_page = get_page(URL_IDEAS_MAIN_PAGE + a_code)
            print('\tIdeas')
            save_page(a_ideas_page, a_code, 'ideas')

            save_state(a_code)

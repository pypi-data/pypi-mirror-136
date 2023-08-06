import requests


def buscar_avatar(usuario):
    """
    Busca uma usuario de um avatar no github
    :param usuario: str com o nome de usuario no github
    :return: str com o link do avatar
    """
    url = f'http://api.github.com/users/{usuario}'
    resp = requests.get(url)
    return resp.json()['avatar_url']


if __name__ == '__main__':
    print(buscar_avatar('FlavioANS'))

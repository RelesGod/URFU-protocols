import sys

from requests import get as GET

token = "vk1.a.iqd2ivck62mQpSblBV10AcHi1Ltxojlr9vd9Q6DqjUpCfiMz1NpA1LdbSGEIQyzyDB9g9Pv74OwC1KWAuTwUUkCtVq_CcfAuW_oiSGb-EwMV47zuParq93pVSQDL6bf1ch4Y5p7J6u2rhI6WMwO3GB3pHx7FeTIbEGxjel5xG2Gt5_00Us4hWqr-aO851K4_B3_rElFizUr0P_LfJpat0A&expires_in=86400"


class User:
    def __init__(self, user_id, count_f, count_p, is_deleted=False):
        self.id = user_id
        self.is_deleted = is_deleted
        self.count_f = count_f
        self.count_p = count_p

    def get_req(self, method):
        return f'https://api.vk.com/method/{method}?user_id={self.id}&v=5.131&access_token={token}'

    def get_user(self):
        req = self.get_req("users.get") + "&fields=bdate"
        try:

            get = GET(req).json()["response"][0]
        except IndexError:
            print("Некорректный  айди")
            sys.exit(0)
        try:
            if get["deactivated"] is not None:
                print("Пользователь удален или забанен")
                sys.exit(0)
        except KeyError:
            pass
        if get["id"] != self.id:
            self.id = get["id"]
        if get['is_closed'] is True:
            print(f"{get['first_name']} {get['last_name']}\n")
            print("Профиль скрыт")
            sys.exit(0)
        return f"{get['first_name']} {get['last_name']} Дата рождения: {get['bdate']}"

    @property
    def get_status(self):
        req = self.get_req("status.get")
        response = GET(req).json()
        return response['response']['text'] or "У пользователя статус пуст"

    def get_user_friends(self):
        friends = []
        req = f"{self.get_req('friends.get')}&order=hints&count={self.count_f}&fields=sex"
        response = GET(req).json()['response']['items']
        for friend in response:
            sex = "ее" if friend['sex'] == 1 else "его"
            friends.append(f"{friend['first_name']} {friend['last_name']} и {sex} айди {friend['id']}")
        return list(map(lambda x: "".join(x), friends))

    def get_user_posts(self):
        req = f'https://api.vk.com/method/wall.get?owner_id={self.id}&v=5.131&access_token={token}&count={self.count_p}'
        response = GET(req).json()["response"]["items"]
        return response


if __name__ == '__main__':
    id = input("Введите айди или ник пользователя :")
    count_friends = input("Введите количество друзей,которых отобразить :")
    count_post = input("Введите кол-во отображаемых постов :")
    user = User(id, count_friends, count_post)

    print(f"{user.get_user()}\n")
    print(f"Статус: {user.get_status}\n")
    print("Друзья:")
    for f in user.get_user_friends():
        print(f)
    print("")
    for post in user.get_user_posts():
        print(f"Пост:\n{post['text']}")
        print("\n")

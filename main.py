import requests
import os

host = os.getenv('KC_USER_REMOVER_HOST')
realm_name = os.getenv("KC_USER_REMOVER_REALM_NAME")
client_id = os.getenv("KC_USER_REMOVER_CLIENT_ID")
client_secret = os.getenv("KC_USER_REMOVER_CLIENT_SECRET")


def get_access_token():
    access_token_url = host + "/realms/" + realm_name + "/protocol/openid-connect/token"

    r = requests.post(url=access_token_url,
                      data={
                          "grant_type": "client_credentials",
                          "client_id": client_id,
                          "client_secret": client_secret
                      })
    data = r.json()
    access_token = data['access_token']
    return access_token


def get_users_from_keycloak(access_token):
    get_users_url = host + "/admin/realms/" + realm_name + "/users"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
    r = requests.get(url=get_users_url, headers=headers)
    user_list = r.json()
    return user_list


def filter_user_list(user_list, filter_file):
    filtered_emails = []
    with open(filter_file, "r") as file:
        for line in file:
            filtered_emails.append(line.strip())

    users_to_delete = []
    for user in user_list:
        if user['email'] not in filtered_emails:
            users_to_delete.append(user)
        else:
            print("Ignoring user: " + user['email'])

    return users_to_delete


def delete_users_from_keycloak(access_token, user_list):
    for user in user_list:
        delete_users_url = host + "/admin/realms/" + realm_name + "/users/" + user['id']
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
        r = requests.delete(url=delete_users_url, headers=headers)
        if r.status_code == 204:
            print("Removed user: " + user['email'])


if __name__ == '__main__':
    access_token = get_access_token()
    users = get_users_from_keycloak(access_token)
    users_to_delete = filter_user_list(users, "./filtered.txt")
    delete_users_from_keycloak(access_token, users_to_delete)

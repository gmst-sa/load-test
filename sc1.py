import requests
import time
import threading
import signal
import sys
import json
import os
import concurrent.futures
import base64
import random

users = {}

requests_processed_healthz = 0
requests_failed_healthz = 0
requests_timed_out_healthz = 0

requests_processed_user = 0
requests_failed_user = 0
requests_timed_out_user = 0


get_requests_processed_user = 0
get_requests_failed_user = 0
get_requests_timed_out_user = 0

post_requests_processed_user = 0
post_requests_failed_user = 0
post_requests_timed_out_user = 0

# GitHub settings
GITHUB_REPO = "gmst-sa/load-test"
GITHUB_API_URL = f"https://api.github.com/repos/gmst-sa/load-test/contents/sc1.md"
GITHUB_ACCESS_TOKEN = ""

# Function to update README.md on GitHub
def update_github_readme(content):
    headers = {
        "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # Get the current file content
    response = requests.get(GITHUB_API_URL, headers=headers)
    response_json = response.json()

    if response.status_code != 200:
        print("Failed to fetch current README.md content from GitHub")
        print("Error response content:", response.text)
        return

    # Update the content with new results
    new_content = """
    -----healthz-----
    전체 /healthz 요청 수: {}
    처리된 /healthz 요청 수: {}
    타임아웃 된 /healthz 요청 수: {}
    처리되지 않은 /healthz 요청 수: {}
    ----- user -----
    전체 /user 요청 수: {}
    처리된 /user 요청 수 (GET): {}
    처리된 /user 요청 수 (POST): {}
    
    처리되지 않은 /user 요청 수 (GET): {}
    처리되지 않은 /user 요청 수 (POST): {}
    타임아웃 된 /user 요청 수: {}
    """.format(
        requests_processed_healthz + requests_failed_healthz + requests_timed_out_healthz,
        requests_processed_healthz,
        requests_timed_out_healthz,
        requests_failed_healthz,
        get_requests_processed_user + get_requests_failed_user + get_requests_timed_out_user + post_requests_processed_user + post_requests_failed_user + post_requests_timed_out_user,
        get_requests_processed_user,
        post_requests_processed_user,
        get_requests_failed_user,
        post_requests_failed_user,
        get_requests_timed_out_user + post_requests_timed_out_user,
    )

    # Encode the new content
    encoded_content = new_content.encode("utf-8")
    encoded_content_b64 = base64.b64encode(encoded_content).decode("utf-8")

    # Update the content with base64 encoded data
    update_data = {
        "message": "Update README.md",
        "content": encoded_content_b64,
        "sha": response_json["sha"],
    }

    # PUT request to update the file
    response = requests.put(GITHUB_API_URL, headers=headers, json=update_data)
    if response.status_code == 200:
        print("Updated README.md on GitHub")
    else:
        print("Failed to update README.md on GitHub")

def format_results():
    results = """
    -----healthz-----
    전체 /healthz 요청 수: {}
    처리된 /healthz 요청 수: {}
    타임아웃 된 /healthz 요청 수: {}
    처리되지 않은 /healthz 요청 수: {}
    ----- user -----
    전체 /user 요청 수: {}
    처리된 /user 요청 수 (GET): {}
    처리된 /user 요청 수 (POST): {}
    
    처리되지 않은 /user 요청 수 (GET): {}
    처리되지 않은 /user 요청 수 (POST): {}
    타임아웃 된 /user 요청 수: {}
    """.format(
        requests_processed_healthz + requests_failed_healthz + requests_timed_out_healthz,
        requests_processed_healthz,
        requests_timed_out_healthz,
        requests_failed_healthz,
        get_requests_processed_user + get_requests_failed_user + get_requests_timed_out_user + post_requests_processed_user + post_requests_failed_user + post_requests_timed_out_user,
        get_requests_processed_user,
        post_requests_processed_user,
        get_requests_failed_user,
        post_requests_failed_user,
        get_requests_timed_out_user + post_requests_timed_out_user,
    )
    return results

def update_github_readme_periodically():
    while True:
        content = format_results()
        update_github_readme(content)
        time.sleep(10 * 60)  # Update every 10 minutes


def create_user():
    user_id = len(users) + 1
    username = f"user_{user_id}"
    password = f"password_{user_id}"
    users[username] = password

    with open('user.json', 'a') as json_file:
        json.dump({"username": username, "password": password}, json_file)
        json_file.write('\n')

    return username, password


def send_healthz_request():
    global requests_processed_healthz
    global requests_failed_healthz
    global requests_timed_out_healthz
    try:
        response = requests.get("https://d20thgadgszlri.cloudfront.net/healthz", timeout=2)
        if response.status_code != 200:
            requests_failed_healthz += 1
        else:
            requests_processed_healthz += 1
    except requests.Timeout:
        requests_timed_out_healthz += 1

def send_user_post_request(name, password):
    global post_requests_processed_user
    global post_requests_failed_user
    global post_requests_timed_out_user
    try:
        data = {"name": name, "password": password}
        response = requests.post("https://d20thgadgszlri.cloudfront.net/user", json=data, timeout=2)
        if response.status_code in [200, 400]:
            post_requests_processed_user += 1
            # Write user information to user.json only for successful POST requests
            with open('user.json', 'a') as json_file:
                json.dump({"username": name, "password": password}, json_file)
                json_file.write('\n')
        else:
            post_requests_failed_user += 1
    except requests.Timeout:
        post_requests_timed_out_user += 1

# def send_user_post_request(name, password):
#     global post_requests_processed_user
#     global post_requests_failed_user
#     global post_requests_timed_out_user
#     try:
#         data = {"name": name, "password": password}
#         response = requests.post("https://d20thgadgszlri.cloudfront.net/user", json=data, timeout=2)
#         if response.status_code != 200:
#             post_requests_failed_user += 1
#         else:
#             post_requests_processed_user += 1
#     except requests.Timeout:
#         post_requests_timed_out_user += 1


def send_user_get_request(name):
    global get_requests_processed_user
    global get_requests_failed_user
    global get_requests_timed_out_user
    try:
        # Read the user.json file and extract usernames
        with open('user.json', 'r') as json_file:
            user_data = json.load(json_file)
            usernames = [entry["username"] for entry in user_data]

        # Select a random username
        random_username = random.choice(usernames)

        # Send GET request using the selected username
        response = requests.get(f"https://d20thgadgszlri.cloudfront.net/user?name={random_username}", timeout=2)
        if response.status_code != 200:
            get_requests_failed_user += 1
        else:
            get_requests_processed_user += 1
    except requests.Timeout:
        get_requests_timed_out_user += 1

def scenario1_random(num_users_low, num_users_high, num_users_large, large_influx_chance, duration_minutes):
    def create_and_send_request(user_id):
        username, password = create_user()
        send_user_post_request(username, password)

    while True:
        num_users = random.randint(num_users_low, num_users_high)
        if random.random() < large_influx_chance:
            num_users = num_users_large

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            for i in range(1, num_users + 1):
                executor.submit(create_and_send_request, i)
                time.sleep(0.1)  # A small delay between submitting requests

        print(f"총 /user POST 요청 수: {post_requests_processed_user + post_requests_failed_user + post_requests_timed_out_user}")

        time.sleep(5 * 60)  # Sleep for 5 minutes before the next influx



def scenario1(num_users, duration_minutes):
    def create_and_send_request(user_id):
        username, password = create_user()
        send_user_post_request(username, password)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        for i in range(1, num_users + 1):
            executor.submit(create_and_send_request, i)
            time.sleep(0.1)  # A small delay between submitting requests

    print(f"시나리오 1 완료 - 총 /user POST 요청 수: {post_requests_processed_user + post_requests_failed_user + post_requests_timed_out_user}")


def scenario2(num_requests, duration_minutes):
    for i in range(num_requests):
        # username, _ = create_user()
        send_user_get_request()
        time.sleep(1)
    print(f"시나리오 2 완료 - 총 /user GET 요청 수: {get_requests_processed_user + get_requests_failed_user + get_requests_timed_out_user}")


def scenario0(duration_minutes):
    while True:
        send_healthz_request()
        time.sleep(1)  


def show_results():
    while True:
        # 스크롤되지 않고 업데이트하는 방식으로 출력
        os.system("cls")
        print("-----healthz-----")
        print("전체 /healthz 요청 수:", requests_processed_healthz + requests_failed_healthz + requests_timed_out_healthz)
        print("처리된 /healthz 요청 수:", requests_processed_healthz)
        print("타임아웃 된 /healthz 요청 수:", requests_timed_out_healthz)
        print("처리되지 않은 /healthz 요청 수:", requests_failed_healthz)

        print("----- user -----")
        print("전체 /user 요청 수:", get_requests_processed_user + get_requests_failed_user + get_requests_timed_out_user + post_requests_processed_user + post_requests_failed_user + post_requests_timed_out_user)
        print("처리된 /user 요청 수 (GET):", get_requests_processed_user)
        print("처리된 /user 요청 수 (POST):", post_requests_processed_user)
        print("")
        print("처리되지 않은 /user 요청 수 (GET):", get_requests_failed_user)
        print("처리되지 않은 /user 요청 수 (POST):", post_requests_failed_user)
        print("타임아웃 된 /user 요청 수:", get_requests_timed_out_user + post_requests_timed_out_user)
        time.sleep(1)


def signal_handler(sig, frame):
    print("Ctrl+C를 눌렀습니다. 현재까지의 결과를 출력합니다.")
    print_results()
    sys.exit(0)


def print_results():
    print("최종 결과:")
    print("처리된 /healthz 요청 수:", requests_processed_healthz)
    print("처리되지 않은 /healthz 요청 수:", requests_failed_healthz)
    print("타임아웃 된 /healthz 요청 수:", requests_timed_out_healthz)
    print("전체 /healthz 요청 수:", requests_processed_healthz + requests_failed_healthz + requests_timed_out_healthz)
    print("처리된 /user 요청 수 (GET):", get_requests_processed_user)
    print("처리되지 않은 /user 요청 수 (GET):", get_requests_failed_user)
    print("타임아웃 된 /user 요청 수 (GET):", get_requests_timed_out_user)
    print("처리된 /user 요청 수 (POST):", post_requests_processed_user)
    print("처리되지 않은 /user 요청 수 (POST):", post_requests_failed_user)
    print("타임아웃 된 /user 요청 수 (POST):", post_requests_timed_out_user)
    print("전체 /user 요청 수 (GET + POST):", get_requests_processed_user + get_requests_failed_user + get_requests_timed_out_user + post_requests_processed_user + post_requests_failed_user + post_requests_timed_out_user)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    print("시나리오 0 실행")
    t0 = threading.Thread(target=scenario0, args=(180*60,))  
    t0.start()

    print("시나리오 1 실행 (랜덤 인플럭스 포함)")
    t1 = threading.Thread(target=scenario1_random, args=(100, 150, 1000, 0.05, 30))
    t1.start()

    print("시나리오 2 실행")
    t2 = threading.Thread(target=scenario2, args=(600, 10))
    t2.start()

    print("실시간 결과 표시 시작")
    t3 = threading.Thread(target=show_results)
    t3.start()

    print("주기적으로 README.md 업데이트 시작")
    t4 = threading.Thread(target=update_github_readme_periodically)
    t4.start()

    t0.join()
    t1.join()
    t2.join()
    t3.join()
    t4.join()


if __name__ == "__main__":
    main()
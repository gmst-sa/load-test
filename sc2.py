import json
import random
import requests
import os
import time


user_data = []
with open('user.json') as json_file:
    for line in json_file:
        user_data.append(json.loads(line))


total_requests = 0
get_requests = 0
unprocessed_get_requests = 0
timeout_requests = 0

while True:
    
    num_users = random.randint(10, 50)

    for _ in range(num_users):
        
        random_user = random.choice(user_data)

        
        url = f"https://d20thgadgszlri.cloudfront.net/user?name={random_user['username']}"
        try:
            response = requests.get(url, timeout=2)
            total_requests += 1
            if response.status_code == 200:
                get_requests += 1
            else:
                unprocessed_get_requests += 1
        except requests.Timeout:
            total_requests += 1
            timeout_requests += 1

    
    if random.randint(1, 10) == 1:
        num_high_traffic = random.randint(1000, 1500)
        for _ in range(num_high_traffic):
            
            random_user = random.choice(user_data)

            
            url = f"https://d20thgadgszlri.cloudfront.net/user?name={random_user['username']}"
            try:
                response = requests.get(url, timeout=2)
                total_requests += 1
                if response.status_code == 200:
                    get_requests += 1
                else:
                    unprocessed_get_requests += 1
            except requests.Timeout:
                total_requests += 1
                timeout_requests += 1

    os.system("cls")
    
    print("----- user -----")
    print(f"전체 /user 요청 수: {total_requests}")
    print(f"처리된 /user 요청 수 (GET): {get_requests}")
    print(f"처리되지 않은 /user 요청 수 (GET): {unprocessed_get_requests}")
    print(f"타임아웃 된 /user 요청 수: {timeout_requests}")
    print("")

    
    
    time.sleep(3)

import asyncio, requests
import time
from datetime import datetime
from aiohttp import ClientSession, ClientResponseError

def sendMsg(msg, chat_id=515513632, TOKEN="1618076368:AAE6ACvsCs_1b8dpK4VGS-iopGpWqc5M8f4"):
    res = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=markdown")

    return res.json()["ok"]

async def get_rank(session, count, punks):
    res = ''
    id = punks[count]["id"]
    price = punks[count]["price"]
    
    try:
        url = 'https://npunks.io/punk/' + id
        async with session.get(url, timeout=60) as response:
            res = await response.read()
            rank = res.decode("utf-8").split("Rank #")[1].split(" </span>.")[0]
            punks[count]["rank"]= rank
            log = "R: " + rank + " | " + str(id) + " | $: " + str(price) + " | https://paras.id/token/near-punks.near::" + str(id) + " | " + datetime.now().strftime("%H:%M:%S")
            
            if int(rank) < 400:
                sendMsg(log)
                time.sleep(1800)
                        
    except Exception as e:
        print(e)
    else:
        return res
    return

async def fetch_async(punks):
    tasks = [] 
    async with ClientSession() as session:
        for count in range(len(punks)):
            task = asyncio.ensure_future(get_rank(session, count, punks))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses

def get_punks_info(times=1):
    skip = 0
    limit = 30
    
    punks_info = []
    for i in range(times):
        res = requests.get(f'https://api-v2-mainnet.paras.id/token-series?collection_id=near-punks.near&exclude_total_burn=true&__skip={skip}&__limit={limit}&__sort=lowest_price::1&min_price=0')
        punks_info = punks_info + res.json()["data"]["results"]
        skip += limit
        
    punks = []
    for punk_info in punks_info:
        punks.append({'id': punk_info["token_series_id"], 'price': int(punk_info["lowest_price"]) / 10 ** 24, 'rank': None})

    return punks

def low_price_check(first_punk, second_punk):
    spread = second_punk - first_punk
    if spread > 1.5:
        sendMsg(f'{punks[0]["price"]} more than {spread}')
    
def logs(log):
    print(log)
    f = open("punks.txt", "a")
    f.write(log + "\n")
    f.close()

if __name__ == "__main__":
    print("Start!!!")
    while True:
        punks = get_punks_info(25)
        low_price_check(punks[0]["price"], punks[1]["price"])
            
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_async(punks))
        loop.run_until_complete(future)

        responses = future.result()
        print("Pass loop")
        time.sleep(30)

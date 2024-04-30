#!/usr/bin/env python3

from datetime import datetime, timedelta
import asyncio
import aiohttp

bearer_token = "0cafeae91b00147004b0feaa2fb9496d49ffe6b6144c952a72060ce4046fc2d8"
endpoint = 'https://api.kanpla.dk/api/v1/modules/TEZBaxqzvLMQId4NigWh/menu'
headers = {'Authorization': 'Bearer ' + bearer_token}

async def fetch(session, url):
    async with session.get(url, headers=headers, ssl=False) as response:
        return await response.json()
        
def getWeekDaysGPT():
    # Get today's date
    today = datetime.today()

    # Check if today is a weekend (Saturday or Sunday)
    if today.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
        # If it's a weekend, get the date for the next Monday
        days_until_next_monday = 7 - today.weekday()
        next_monday = today + timedelta(days=days_until_next_monday)
    else:
         # If it's a weekday, get the date for today (Monday)
        days_until_monday = today.weekday()
        next_monday = today - timedelta(days=days_until_monday)

    # Calculate the dates for the rest of the week (excluding the weekend)
    dates_this_week = [next_monday + timedelta(days=i) for i in range(5)]

    return dates_this_week


async def whole_week_personalized():
    async with aiohttp.ClientSession() as session:
        payloads = [
            {'date': day.strftime("%d-%m-%G")}
            for day in getWeekDaysGPT()
        ]

        tasks = [fetch(session, f'{endpoint}?date={payload["date"]}') for payload in payloads]
        results = await asyncio.gather(*tasks)

        for day, result in zip(getWeekDaysGPT(), results):
            menus = result["response"]["menus"]
            filtered_menus = [menu for menu in menus if menu["productName"] == "Den Varierende (lilla)" or menu["productName"] == "Den Klassiske (orange)"]
            print(day.strftime("%A"))
            for filtered_menu in filtered_menus:
                productName = filtered_menu["productName"]
                menuDescription = filtered_menu["description"].strip('\n')
                menuName = filtered_menu["name"].strip('\n')

                print(f'{productName} - {menuName}')
                print(menuDescription)
                print('')
            print('')

async def get_menu_for_today():
    today = datetime.today()
    async with aiohttp.ClientSession() as session:
        payload = {'date': today.strftime("%d-%m-%G")}

        task = fetch(session, f'{endpoint}?date={payload["date"]}')
        res = await asyncio.gather(task)
        response = res[0]['response']
        
        products = response['products']
        menus = response['menus']
        filtered_products = [product for product in products if product['category'] != 'til tørsten' and product['category'] != 'andet']
        # Extract the IDs of the filtered products
        filtered_product_ids = {product['id'] for product in filtered_products}

        menus_from_filtered_products = [menu_item for menu_item in menus if menu_item['productId'] in filtered_product_ids]

        output = ""
        output += '*' + today.strftime('%A %d. %B') + '*\n\n'
        
        for filtered_menu in menus_from_filtered_products:
            productName = filtered_menu["productName"]
            menuDescription = filtered_menu["description"].strip('\n')
            menuName = filtered_menu["name"].strip('\n')

            output += '*' + productName + ' - ' + menuName + '*\n'
            output += menuDescription + '\n\n'
        print(output)

def main():
    asyncio.run(get_menu_for_today())

if __name__=="__main__":
    main()
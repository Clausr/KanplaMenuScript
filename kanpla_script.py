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
        
async def get_menu_for_today(date_to_look_for):
    async with aiohttp.ClientSession() as session:
        payload = {'date': date_to_look_for.strftime("%d-%m-%G")}

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
        output += '*' + date_to_look_for.strftime('%A %d. %B') + '*\n\n'
        
        for filtered_menu in menus_from_filtered_products:
            productName = filtered_menu["productName"]
            menuDescription = filtered_menu["description"].strip('\n')
            menuName = filtered_menu["name"].strip('\n')

            output += '*' + productName + ' - ' + menuName + '*\n'
            output += menuDescription + '\n\n'
        print(output)

def main():
    asyncio.run(get_menu_for_today(datetime.today()))

if __name__=="__main__":
    main()
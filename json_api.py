import asyncio
import json


async def save(data):
    with open('user_info.json', 'w') as f:
        json.dump(data, f)


async def read():
    with open('user_info.json', 'r', encoding='utf8') as f:
        return json.load(f)


async def create_user(id_: str):
    data = await read()
    user = await get_user(id_)
    if not user:
        data['users'][id_] = {
                    "aim": 0,
                    'total_scores': 0,
                    "today_scores": 0,
                    'time_table': [],
                    "time_end": None,
                }
        await save(data)


async def get_user(id_: str):
    data = await read()
    try:
        return data['users'][f'{id_}']
    except KeyError:
        return []


async def get_item(id_: str, item_name: str):
    data = await read()
    try:
        return data['users'][f'{id_}'][f'{item_name}']
    except KeyError:
        return []


async def update_user(id_: str, dict_: dict):
    data = await read()
    for key in dict_.keys():
        data['users'][f'{id_}'][f'{key}'] = dict_[key]
        await save(data)


async def update_day_scores(id_: str, dict_:dict):
    data = await read()
    for key in dict_.keys():
        for index, data_item in enumerate(data['users'][f'{id_}']['time_table']):
            if data_item['date'] == key:
                data['users'][f'{id_}']['time_table'][index]['push-ups'] = dict_[key]
                await save(data)
                return
        data['users'][f'{id_}']['time_table'].append({
            'date': f'{key}', 'push-ups': f'{dict_[key]}'
        })
        await save(data)

if __name__ == '__main__':
    asyncio.run(read())

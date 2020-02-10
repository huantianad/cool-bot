import random
import aiohttp

headers = {"FA_COOKIE": "b=c11442dd-56d1-4f7f-bee7-a80ad08e3255; a=87ca8992-168b-4739-851a-7c0c8f118612"}


async def check_api(url: str):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as r:
            return await r.json()


async def reload_data(name: str):
    i = 1
    subs = []

    try:
        with open(f'saved/{name}.txt', 'r+') as file:
            saved = [current_place.rstrip() for current_place in file.readlines()]
            saved = set(saved)
    except FileNotFoundError:
        saved = set()

    while True:
        gallery = await check_api(f"http://localhost:9292/user/{name}/gallery.json?page={i}")
        if not gallery:
            break
        else:
            for sub in gallery:
                subs.append(sub)
        i += 1

    subs = set(subs)

    for sub in subs:
        if sub not in saved:
            with open(f'saved/{name}.txt', 'a+') as file:
                file.write(f'{sub}\n')


# Check if there are new notifications
async def check_notif():
    notif = await check_api("http://localhost:9292/notifications/submissions.json")
    output = []
    if notif['new_submissions']:
        # Set subs to new submissions
        subs = notif['new_submissions']
        ids = set()

        # Add subs to ids set
        for sub in subs:
            id = sub['id']
            ids.add(id)

        # Get saved ids and put in set saved
        with open('saved/notifs.txt', 'r') as file:
            saved = [current_place.rstrip() for current_place in file.readlines()]
            saved = set(saved)

        # Loop through ids
        for id in ids:
            # Check if id has been saved
            if id not in saved:
                data = await check_api(f"http://localhost:9292/submission/{id}.json")
                # Save new id to file
                output.append(data)
                with open('saved/notifs.txt', 'a') as file:
                    file.write(f'{id}\n')
    return output


async def random_submission(name: str):
    with open(f'saved/{name}.txt', 'r+') as file:
        saved = [current_place.rstrip() for current_place in file.readlines()]
    randoms = random.choice(saved)
    return await check_api(f"http://localhost:9292/submission/{randoms}.json")

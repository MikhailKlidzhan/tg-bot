import httpx

async def get_bible_verse():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://bible-api.com/?random=verse")
        data = res.json()
        return f"{data['verses'][0]['book_name']} {data['verses'][0]['chapter']}:{data['verses'][0]['verse']} - {data['verses'][0]['text']}"


async def get_quran_verse():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.quranhub.com/v1/ayah/random")
        data = res.json()
        return f"{data['data']['surah']['englishName']}: {data['data']['number']} - {data['data']['text']}"
import httpx
from loguru import logger


async def get_bible_verse():
    logger.debug(f"Fetching for a bible verse.")
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get("https://bible-api.com/?random=verse")
            res.raise_for_status()
            data = res.json()
            logger.info("Successfully fetched for a bible verse.")
            return f"{data['verses'][0]['book_name']} {data['verses'][0]['chapter']}:{data['verses'][0]['verse']} - {data['verses'][0]['text']}"
        except Exception as e:
            logger.error(f"Failed to fetch for a bible verse: {e}")


async def get_quran_verse():
    logger.debug(f"Fetching for a quran ayah.")
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get("https://api.quranhub.com/v1/ayah/random")
            res.raise_for_status()
            data = res.json()
            logger.info("Successfully fetched for a quran ayah.")
            return f"{data['data']['surah']['englishName']}: {data['data']['number']} - {data['data']['text']}"
        except Exception as e:
            logger.error(f"Failed to fetch for a quran ayah: {e}")

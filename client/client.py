import asyncio
import io
import json
from base64 import b64decode

import httpx
from PIL import Image
from websockets import connect, ConnectionClosed, Origin

from printer import OwnPrinter
from secret import token

local_test = False

if local_test:
    http_host = "http://localhost:8000"
    ws_host = "ws://localhost:8000"
else:
    http_host = "https://notes.lw1.at"
    ws_host = "wss://notes.lw1.at"

headers = {"Authorization": f"Token {token}"}

uri = ws_host + "/ws/printer/"
origin = Origin(http_host)
http_client = httpx.AsyncClient()
printer = OwnPrinter()


async def print_note(note_id: int):
    r = await http_client.get(f"{http_host}/note/{note_id}", headers=headers)
    r.raise_for_status()
    data = r.json()
    print(data)
    if data["printed_at"] is not None:
        print("already printed")
        return
    image = Image.open(io.BytesIO(b64decode(data["image"])))
    # await asyncio.sleep(10)
    printer.print_note(image)
    r = await http_client.post(f"{http_host}/note/{note_id}/printed", data={"printed": True}, headers=headers)
    r.raise_for_status()


async def consume(message):
    print(message)
    note_id = message["note_id"]
    await print_note(note_id)


async def get_unprinted() -> list[int]:
    r = await http_client.get(f"{http_host}/unprinted", headers=headers)
    r.raise_for_status()
    data = r.json()
    note_ids=data["note_ids"]
    print(note_ids)
    return note_ids


async def main():
    async for websocket in connect(uri, origin=origin, additional_headers=headers):
        print(websocket.request.headers)
        print(websocket.response.headers)
        print("catching up with unprinted notes")
        for note_id in await get_unprinted():
            await print_note(note_id)
        print("caught up")
        try:
            async for message in websocket:
                await consume(json.loads(message))
        except ConnectionClosed:
            continue
    await http_client.aclose()


if __name__ == '__main__':
    asyncio.run(main(), debug=True)

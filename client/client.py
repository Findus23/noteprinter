import asyncio
import io
import json
from base64 import b64decode

import httpx
from PIL import Image
from websockets import connect, ConnectionClosed, Origin

from printer import OwnPrinter

uri = "ws://127.0.0.1:8000/ws/printer/"
origin = Origin("http://127.0.0.1:8000")
http_client = httpx.AsyncClient()
printer=OwnPrinter()

async def consume(message):
    print(message)
    note_id = message["note_id"]
    r = await http_client.get(f"http://127.0.0.1:8000/note/{note_id}")
    r.raise_for_status()
    data = r.json()
    print(data)
    if data["printed_at"] is not None:
        print("already printed")
    image = Image.open(io.BytesIO(b64decode(data["image"])))
    # await asyncio.sleep(10)
    printer.print_note(image)
    r = await http_client.post(f"http://127.0.0.1:8000/note/{note_id}/printed", data={"printed": True})
    r.raise_for_status()
    print("finished", message)


async def main():
    async for websocket in connect(uri, origin=origin):
        print(websocket.request.headers)
        print(websocket.response.headers)
        try:
            async for message in websocket:
                await consume(json.loads(message))
        except ConnectionClosed:
            continue
    await http_client.aclose()


if __name__ == '__main__':
    asyncio.run(main(), debug=True)

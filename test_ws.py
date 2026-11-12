import asyncio
import websockets

async def test_ws():
    uri = "ws://localhost:8000/ws/chat"
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri, origin="http://localhost:5173") as websocket:
            print("Connected!")
            await websocket.send('{"messages": [{"role": "user", "content": "hello"}]}')
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test_ws())
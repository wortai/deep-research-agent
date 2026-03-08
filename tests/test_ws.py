import asyncio
import json
import websockets
import uuid
import subprocess
import time
import sys
import os
import signal

SERVER_PORT = 8000
SERVER_HOST = "127.0.0.1"

async def run_client():
    thread_id = str(uuid.uuid4())
    uri = f"ws://{SERVER_HOST}:{SERVER_PORT}/ws/chat/{thread_id}"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send a test message
            message = {
                "content": "Hello, this is a test.",
                "user_id": "test_user",
                "mode": "websearch"
            }
            print(f"Sending: {json.dumps(message)}")
            await websocket.send(json.dumps(message))
            
            # Listen for responses with timeout
            print("Listening for responses (timeout 10s)...")
            start_time = time.time()
            
            while time.time() - start_time < 10:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    print(f"Received ({data.get('type')}): {str(data)[:100]}...")
                    
                    if data.get("type") == "error":
                        print(f"Error: {data.get('message')}")
                        break
                    if data.get("type") == "done":
                        print("Stream finished.")
                        break
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for message chunk.")
                    # Keep waiting a bit longer
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break
                    
    except Exception as e:
        print(f"Client error: {e}")

def main():
    # Start server
    print("Starting server...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(os.getcwd(), "deep-research-agent")
    
    server_process = subprocess.Popen(
        [sys.executable, "server/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Wait for server to be ready (simple sleep)
    time.sleep(5)
    
    if server_process.poll() is not None:
        print("Server failed to start.")
        stdout, stderr = server_process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)
        
    try:
        # Run client using existing event loop
        asyncio.run(run_client())
    finally:
        print("Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    main()

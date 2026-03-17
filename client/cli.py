import asyncio
import getpass
import json
import os
import sys

import aioconsole
import requests
import websockets

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

# ANSI
RESET  = "\033[0m"
RED    = "\033[31m"
GREEN  = "\033[92m"

def username_color(username: str) -> str:
    h = hash(username) & 0xFFFFFF
    r = max((h >> 16) & 0xFF, 30)
    g = max((h >> 8)  & 0xFF, 30)
    b = max(h & 0xFF,          30)
    return f"\033[38;2;{r};{g};{b}m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if os.name == 'nt':
    os.system('')

def print_banner():
    banner = r"""
  _____ _               _    _____ _           _   
 / ____| |             | |  / ____| |         | |  
| |  __| |__   ___  ___| |_| |    | |__   __ _| |_ 
| | |_ | '_ \ / _ \/ __| __| |    | '_ \ / _` | __|
| |__| | | | | (_) \__ \ |_| |____| | | | (_| | |_ 
 \_____|_| |_|\___/|___/\__|\_____|_| |_|\__,_|\__|
    """
    print(f"\033[96m{banner}\033[0m")

def get_auth_token():
    print_banner()
    print(f"{GREEN}Welcome to Ghost IRC chat!{RESET}")
    while True:
        choice = input(f"{GREEN}1. Login\n2. Register\nChoose (1/2): {RESET}").strip()

        if choice == '2':
            username = input(f"{GREEN}Enter new username: {RESET}").strip()
            password = getpass.getpass(f"{GREEN}Enter new password: {RESET}").strip()
            try:
                response = requests.post(
                    f"{API_URL}/auth/register",
                    json={"username": username, "password": password}, timeout=5
                )
                if response.status_code == 200:
                    print(f"{GREEN}Registration successful! Please login.{RESET}")
                else:
                    print(f"{RED}Error: {response.json().get('detail', 'Registration failed')}{RESET}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print(f"{RED}Error: Could not connect to server. Is it running?{RESET}")
                return None

        elif choice == '1':
            username = input(f"{GREEN}Username: {RESET}").strip()
            password = getpass.getpass(f"{GREEN}Password: {RESET}").strip()
            try:
                response = requests.post(
                    f"{API_URL}/auth/token",
                    data={"username": username, "password": password}
                )
                if response.status_code == 200:
                    token_data = response.json()
                    return token_data["access_token"], username
                else:
                    print(f"{RED}Login failed: Invalid credentials{RESET}")
            except requests.exceptions.ConnectionError:
                print(f"{RED}Error: Could not connect to server. Is it running?{RESET}")
                return None
        else:
            print(f"{RED}Invalid choice.{RESET}")

async def receive_messages(websocket, username):
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "message":
                sender = data.get("username", "Unknown")
                content = data.get("content", "")
                timestamp = data.get("timestamp", "")

                try:
                    date = timestamp.split("T")[0]
                    time = timestamp.split("T")[1][:5]
                    day, month, year = date.split("-")
                    ts = f"{day}/{month}/{year[2:]} {time}"
                except Exception:
                    ts = timestamp

                color = username_color(sender)
                if sender == username:
                    print(f"[{ts}] {color}You:{RESET} {content}")
                else:
                    print(f"[{ts}] {color}{sender}:{RESET} {content}")

            elif msg_type == "system":
                content = data.get("content", "")
                #colored system messages
                if " joined the chat." in content:
                    name = content.replace(" joined the chat.", "")
                    print(f"{RED}[SYSTEM] {username_color(name)}{name}{RED} joined the chat.{RESET}")
                elif " left the chat." in content:
                    name = content.replace(" left the chat.", "")
                    print(f"{RED}[SYSTEM] {username_color(name)}{name}{RED} left the chat.{RESET}")
                elif "Online users: " in content:
                    users = content.replace("Online users: ", "").split(", ")
                    colored = ", ".join(f"{username_color(u)}{u}{RESET}" for u in users)
                    print(f"{RED}[SYSTEM] Online users: {colored}{RESET}")
                else:
                    print(f"{RED}[SYSTEM] {content}{RESET}")

    except websockets.exceptions.ConnectionClosed:
        print(f"\n{RED}Connection closed by server.{RESET}")

async def send_messages(websocket):
    while True:
        try:
            message = await aioconsole.ainput("")
            if not message.strip():
                continue

            if message.strip() == "/exit":
                print(f"{GREEN}Exiting...{RESET}")
                await websocket.close()
                break

            if message.strip() == "/online":
                await websocket.send(json.dumps({"command": "online"}))
                continue

            terminal_width = os.get_terminal_size().columns
            lines_used = (len(message) + terminal_width - 1) // terminal_width

            for _ in range(lines_used):
                sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()

            await websocket.send(json.dumps({"content": message}))
        except (EOFError, KeyboardInterrupt):
            await websocket.close()
            break

async def start_chat(token, username):
    print(f"\n{GREEN}Connecting as {username}...{RESET}")    
    try:
        async with websockets.connect(WS_URL) as websocket:
            await websocket.send(json.dumps({"token": token}))
            print(f"{GREEN}Commands: /online, /exit{RESET}")
            print(f"{GREEN} --- Chat history --- {RESET}")

            receive_task = asyncio.create_task(receive_messages(websocket, username))
            send_task = asyncio.create_task(send_messages(websocket))

            done, pending = await asyncio.wait(
                [receive_task, send_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            await asyncio.gather(*pending, return_exceptions=True)

    except Exception as e:
        print(f"{RED}Connection failed: {e}{RESET}")

def main():
    auth_result = get_auth_token()
    if auth_result:
        token, username = auth_result
        try:
            print(f"{GREEN}Starting chat client...{RESET}")
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(start_chat(token, username))
        except KeyboardInterrupt:
            print(f"\n{GREEN}See ya champ{RESET}")

if __name__ == "__main__":
    main()
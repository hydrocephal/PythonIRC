from app.schemas.auth import UserCreate
from app.services.chat import ConnectionManager, get_user_from_token, websocket_connection_logic
from app.models.models import User, Message
from app.services.auth import create_user, create_access_token
from app.services.chat import manager


async def test_user_from_token(db):
    user_data = UserCreate(username="GenaPupkin", password="secretpass")
    create_user(user_data, db)

    token = create_access_token(data={"sub": "GenaPupkin"})
    result = await get_user_from_token(token, db)
    assert result is not None
    assert result.username == "GenaPupkin"

async def test_websocket_connect(client):
    client.post("/auth/register", json={
        "username": "GenaPupkin",
        "password": "secretpass"
    })
    response = client.post("/auth/token", data={
        "username": "GenaPupkin",
        "password": "secretpass"
    })

    token = response.json()["access_token"] 

    with client.websocket_connect("/ws") as ws:
        ws.send_json({"token": token})
        data = ws.receive_json()
        print(f"{data}")
        assert data["type"] == "system"
        assert "GenaPupkin" in data["content"]

async def test_websocket_online(client):
    client.post("/auth/register", json={
        "username": "GenaPupkin",
        "password": "secretpass"
    })
    response = client.post("/auth/token", data={
        "username": "GenaPupkin",
        "password": "secretpass"
    })

    token = response.json()["access_token"] 

    with client.websocket_connect("/ws") as ws:
        ws.send_json({"token": token})
        ws.receive_json()

        ws.send_json({"command": "online"})
        data = ws.receive_json()
    print(data)
    assert data["type"] == "system"
    assert "GenaPupkin" in data["content"]

async def test_message(client):
    client.post("/auth/register", json={
        "username": "GenaPupkin",
        "password": "secretpass"
    })
    response = client.post("/auth/token", data={
        "username": "GenaPupkin",
        "password": "secretpass"
    })

    token1 = response.json()["access_token"]

    client.post("/auth/register", json={
        "username": "Eblan",
        "password": "Eblan"
    })
    response = client.post("/auth/token", data={
        "username": "Eblan",
        "password": "Eblan"
    })

    token2 = response.json()["access_token"] 
    
    with client.websocket_connect("/ws") as ws1:
        ws1.send_json({"token": token1})
        ws1.receive_json()
        ws1.send_json({"content": "See ya champ"})        

    with client.websocket_connect("/ws") as ws2:
        ws2.send_json({"token": token2})
        ws2.receive_json()

        message = ws2.receive_json()
        print(message)
    assert "See ya champ" in message["content"]

async def test_disconnect_reconnect_history(client):
    client.post("/auth/register", json={
        "username": "GenaPupkin",
        "password": "secretpass"
    })
    response = client.post("/auth/token", data={
        "username": "GenaPupkin",
        "password": "secretpass"
    })

    token1 = response.json()["access_token"]

    client.post("/auth/register", json={
        "username": "Eblan",
        "password": "Eblan"
    })
    response = client.post("/auth/token", data={
        "username": "Eblan",
        "password": "Eblan"
    })

    token2 = response.json()["access_token"] 
    
    with client.websocket_connect("/ws") as ws1, \
        client.websocket_connect("/ws") as ws2:
        ws1.send_json({"token": token1})
        ws1.receive_json()
        ws1.send_json({"content": "See ya champ"})

        ws2.send_json({"token": token2})
        ws2.receive_json()
        ws1.receive_json()
        ws2.receive_json()

        ws1.close()
        left = ws2.receive_json()
        print(left)
    assert "GenaPupkin left the chat" in left["content"]
    
    with client.websocket_connect("/ws") as ws1:
        ws1.send_json({"token": token1})
        ws1.receive_json()
        history = ws1.receive_json()
        print(history)
    assert "See ya champ" in history["content"]

from fastapi import FastAPI
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import os

app = FastAPI()

class ScrapeRequest(BaseModel):
    api_id: int
    api_hash: str
    group_link: str
    keywords: list[str] = []  # Optional list of keywords to filter results

@app.post("/scrape")
async def scrape_telegram(data: ScrapeRequest):
    client = TelegramClient('session', data.api_id, data.api_hash)

    await client.start()
    results = []

    try:
        channel = await client.get_entity(data.group_link)
        participants = await client.get_participants(channel)

        for user in participants:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = user.username or "No username"
            user_handle = f"@{username}" if username != "No username" else "No handle"

            try:
                full_user = await client(GetFullUserRequest(user.id))
                bio = full_user.full_user.about if full_user.full_user.about else "No bio"
            except:
                bio = "Error fetching bio"

            # Filter by keywords if provided
            if data.keywords:
                bio_lower = bio.lower()
                if not any(keyword.lower() in bio_lower for keyword in data.keywords):
                    continue  # Skip this user if no keyword matches

            results.append({
                "Full Name": full_name,
                "Username": username,
                "Bio": bio,
                "User Handle": user_handle
            })

        await client.disconnect()
        return {"status": "success", "data": results}

    except Exception as e:
        await client.disconnect()
        return {"status": "error", "message": str(e)}

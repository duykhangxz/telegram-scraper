from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import os
import time
import csv

# Fetch API credentials from environment variables
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

# Initialize the Telegram client
client = TelegramClient('session_name', int(api_id), api_hash)

# Target channel link (use the full t.me link for public channels)
channel_link = 'https://t.me/ABGAFriends'  # Replace with your channel's link

# CSV File setup
csv_file = 'telegram_users.csv'
fieldnames = ['Full Name', 'Username', 'Bio', 'User Handle']

# Create CSV file and write headers if it doesn't exist
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

async def scrape_channel_members():
    # Connect to the client
    await client.start()

    try:
        # Fetch the channel entity by link
        channel = await client.get_entity(channel_link)

        # Fetch participants of the channel (works for supergroups or admins)
        participants = await client.get_participants(channel)

        # Iterate over each participant
        for user in participants:
            # Fetch the user's full name
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            full_name = f"{first_name} {last_name}".strip()

            # Fetch the username (if available)
            username = user.username
            user_handle = f"@{username}" if username else "No handle"

            # Fetch user bio
            try:
                full_user = await client(GetFullUserRequest(user.id))  # Get full user details
                bio = full_user.full_user.about if full_user.full_user.about else "No bio"
            except Exception as e:
                bio = "Error fetching bio"
                print(f"Error fetching bio for {user.username}: {e}")

            # Print fetched information to the terminal
            print(f"Full Name: {full_name}")
            print(f"Username: {username}")
            print(f"Bio: {bio}")
            print(f"User Handle: {user_handle}")
            print('-' * 40)

            # Save the data to the CSV file
            try:
                with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writerow({
                        'Full Name': full_name,
                        'Username': username,
                        'Bio': bio,
                        'User Handle': user_handle
                    })
            except PermissionError as e:
                print(f"Unable to write to file {csv_file}: {e}")

            # Add a sleep time of 1 second between requests
            time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

async def main():
    await scrape_channel_members()

# Running the client
with client:
    client.loop.run_until_complete(main())

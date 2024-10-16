import json


async def get_auto_mod_data():
    try:
        with open("auto_mod.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"automodservers": []}
        try:
            write_auto_mod_data(data)  # Create a new file with default data
        except Exception as e:
            print(f"Error writing auto_mod.json: {e}")
    return data

async def write_auto_mod_data(data):
    with open("auto_mod.json", "w") as f:
        json.dump(data, f, indent=4)

async def write_auto_mod_data(data):
    with open("auto_mod.json", "w") as f:
        json.dump(data, f, indent=4)

async def add_auto_mod_server(server_id):
    data = await get_auto_mod_data()
    if server_id not in data["automodservers"]:
        data["automodservers"].append(server_id)
        await write_auto_mod_data(data)

async def remove_auto_mod_server(server_id):
    data = await get_auto_mod_data()
    if server_id in data["automodservers"]:
        data["automodservers"].remove(server_id)
        await write_auto_mod_data(data)

async def is_auto_mod_active(server_id):
    data = await get_auto_mod_data()
    return server_id in data["automodservers"]

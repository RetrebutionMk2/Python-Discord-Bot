import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random

class oilcommandslash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'oil_usage.json'
        self.load_data()

        # Define conversion rates and store items
        self.conversions = {
            'can': 1,
            'drum': 1000,
            'barrel': 1000**2,
            'tanker': 1000**3,
            'big tanker': 1000**4,
            'large tanker': 1000**5,
            'extra large tanker': 1000**6,
            'mega tanker': 1000**7,
            'legendary tanker': 1000**8
        }

        self.store_items = {
            "Hand Pumps": {
                "Basic Manual Hand Pump": {"price": 100, "extraction_rate": 5},
                "Advanced Manual Hand Pump": {"price": 250, "extraction_rate": 25},
                "Elite Manual Hand Pump": {"price": 500, "extraction_rate": 100},
                "Ultra Manual Hand Pump": {"price": 1000, "extraction_rate": 300},
            },
            "Pumpjacks": {
                "Basic Pumpjack": {"price": 5000, "extraction_rate": 1000},
                "Advanced Pumpjack": {"price": 10000, "extraction_rate": 3000},
                "Elite Pumpjack": {"price": 12500, "extraction_rate": 3500},
                "Ultra Pumpjack": {"price": 15000, "extraction_rate": 5000},
            },
            "Storage": {
                "drum": {"price": 1000, "capacity": 1000},
                "barrel": {"price": 10000, "capacity": 1000**2},
                "tanker": {"price": 50000, "capacity": 1000**3},
                "big tanker": {"price": 125000, "capacity": 1000**4},
                "large tanker": {"price": 200000, "capacity": 1000**5},
                "extra large tanker": {"price": 300000, "capacity": 1000**6},
                "mega tanker": {"price": 450000, "capacity": 1000**7},
                "legendary tanker": {"price": 1000000, "capacity": 1000**8},
            }
        }
        
        self.item_inventory = {}
        self.load_inventory()

    def load_data(self):
        # Create the file if it doesn't exist
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({}, f)
        
        # Load data from the JSON file
        with open(self.data_file, 'r') as f:
            self.oil_usage = json.load(f)

    def save_data(self):
        # Save data to the JSON file
        with open(self.data_file, 'w') as f:
            json.dump(self.oil_usage, f, indent=4)

    def load_inventory(self):
        # Create the file if it doesn't exist
        if not os.path.exists('inventory.json'):
            with open('inventory.json', 'w') as f:
                json.dump({}, f)
        
        # Load data from the JSON file
        with open('inventory.json', 'r') as f:
            self.item_inventory = json.load(f)

    def save_inventory(self):
        # Save data to the JSON file
        with open('inventory.json', 'w') as f:
            json.dump(self.item_inventory, f, indent=4)
            
    async def initialize_user_data(self, user_id):
        if user_id not in self.oil_usage:
            self.oil_usage[user_id] = {
                "balance": 100,
                "oil": 0,
                "storage": {
                    "limit": 1000,
                    "drum": 0,
                    "barrel": 0,
                    "tanker": 0,
                    "big tanker": 0,
                    "large tanker": 0,
                    "extra large tanker": 0,
                    "mega tanker": 0,
                    "legendary tanker": 0
                }
            }
            self.save_data()
        
        if user_id not in self.item_inventory:
            self.item_inventory[user_id] = {
                "Hand Pumps": {
                    "basic manual hand pump": 0,
                    "advanced manual hand pump": 0,
                    "elite manual hand pump": 0,
                    "ultra manual hand pump": 0
                },
                "Pumpjacks": {
                    "basic pumpjack": 0,
                    "advanced pumpjack": 0,
                    "elite pumpjack": 0,
                    "ultra pumpjack": 0
                },
                "Storage": {
                    "drum": 1,  # Default starting value for new users
                    "barrel": 0,
                    "tanker": 0,
                    "big tanker": 0,
                    "large tanker": 0,
                    "extra large tanker": 0,
                    "mega tanker": 0,
                    "legendary tanker": 0
                }
            }
            self.save_inventory()

        # Optional: Debug print statements to verify data initialization
        print(f"Initialized user {user_id} with data: {self.oil_usage[user_id]}")
        print(f"Initialized user {user_id} with inventory: {self.item_inventory[user_id]}")

    
    @app_commands.command(name="initialize", description="Initialize your oil account.")
    async def initialize(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        await self.initialize_user_data(user_id)
        await interaction.response.send_message("Initialized!")

    # Shows all the iems the user owns currently
    async def item_autocomplete(self, interaction: discord.Interaction, current: str):
        user_id = str(interaction.user.id)
        
        
        # Get the items and store them in a list
        user_inventory = self.item_inventory.get(user_id, {})
        items = []
        
        for category, item_dict in user_inventory.items():
            if category.lower() == "Storage":
                continue    # Skip the storage category
            
            for item_name, count in item_dict.items():
                if count > 0:
                    items.append(app_commands.Choice(name=item_name, value=item_name))
        
        # Return items that match the current input
        return [item for item in items if current.lower() in item.name.lower()]
      
        
    @app_commands.command(name="work", description="Work using a specified item to extract oil.")
    @app_commands.autocomplete(item_name = item_autocomplete)
    @app_commands.checks.cooldown(1, 20, key=lambda i: (i.user.id))
    async def work_slash(self, interaction: discord.Interaction, item_name: str):
        user_id = str(interaction.user.id)   

        try:
            # Check if item exists in the store and get the extraction rate
            extraction_rate = None
            for category in ["Hand Pumps", "Pumpjacks"]:
                for store_item_name, item_details in self.store_items.get(category, {}).items():
                    if store_item_name.lower() == item_name.lower():
                        extraction_rate = item_details.get("extraction_rate")
                        break
                if extraction_rate:
                    break

            if extraction_rate:
                current_oil = self.oil_usage[user_id]["oil"]
                storage_limit = self.oil_usage[user_id]["storage"]["limit"]
                new_oil_amount = current_oil + extraction_rate

                if new_oil_amount > storage_limit:
                    excess_oil = new_oil_amount - storage_limit
                    self.oil_usage[user_id]["oil"] = storage_limit
                    await interaction.response.send_message(
                        f"Your storage is full. You could only store {extraction_rate - excess_oil} cans of oil. Consider buying a larger storage or selling your oil.", 
                        ephemeral=True
                    )
                else:
                    self.oil_usage[user_id]["oil"] = new_oil_amount
                    await interaction.response.send_message(
                        f"Used {item_name}. You have gained {extraction_rate} cans of oil. Your total is now {self.oil_usage[user_id]['oil']} cans."
                    )

                self.save_data()
                self.save_inventory()

            else:
                await interaction.response.send_message(f"Item {item_name} not found in the store.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"An error occurred while using {item_name}: {str(e)}. Please contact the bot owner(retrebutionmk2), feel free to ping or DM him.", ephemeral=True)


    # Catch cooldown error and send an ephemeral message to the user
    @work_slash.error
    async def work_slash_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"You are on cooldown! Try again in {round(error.retry_after)} seconds.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"An unexpected error occurred: {str(error)}", ephemeral=True)
        
    
    # Get the number of categories in the store
    async def category_autocomplete(self, interaction: discord.Interaction, current_cat: str):
        categories = list(self.store_items.keys())
        return [app_commands.Choice(name=cat, value=cat) for cat in categories if current_cat.lower() in cat.lower()]


    @app_commands.command(name="store", description="View the store")
    @app_commands.autocomplete(category=category_autocomplete)
    async def store_slash(self, interaction: discord.Interaction, category: str):
        user_id = str(interaction.user.id)
        

        items = self.store_items.get(category, {})
        embed = discord.Embed(title=f"{category} Store", description="Available items for purchase", color=discord.Color.blue())
        for item, details in items.items():
            embed.add_field(name=item, value=f"Price: ${details['price']} - Extraction Rate: {details.get('extraction_rate', 'N/A')}", inline=False)

        await interaction.response.send_message(embed=embed)
        
    
    # Get all the items in the store
    async def store_items_autocomplete(self, interaction: discord.Interaction, current_store: str):
        store_items = []
        for category, items_dict in self.store_items.items():
            for item in items_dict.keys():
                if current_store.lower() in item.lower():
                    store_items.append(app_commands.Choice(name=item, value=item))
        return store_items
    
    @app_commands.command(name="buy", description="Buy an item from the store.")
    @app_commands.autocomplete(item=store_items_autocomplete)
    async def buy_slash(self, interaction: discord.Interaction, item: str):
        user_id = str(interaction.user.id)
        
        
        if item is None:
            await interaction.response.send_message("You need to specify an item to buy. Usage: `/buy [item]`", ephemeral=True)
            return
       
        

        item = item.lower()
        item_found = False

        for category, items in self.store_items.items():
            items_lower = {k.lower(): v for k, v in items.items()}

            if item in items_lower:
                item_details = items_lower[item]
                item_found = True

                if category != "Storage":
                    if self.item_inventory[user_id].get(category, {}).get(item, 0) > 0:
                        await interaction.response.send_message(f"You already own {item}. You can't buy the same item again.", ephemeral=True)
                        return

                if self.oil_usage[user_id]["balance"] < item_details["price"]:
                    await interaction.response.send_message(f"You don't have enough balance to buy {item}.", ephemeral=True)
                    return

                if category == "Storage":
                    additional_capacity = item_details["capacity"]
                    self.item_inventory[user_id][category][item] = self.item_inventory[user_id].get(category, {}).get(item, 0) + 1
                    self.oil_usage[user_id]["storage"][item] = self.oil_usage[user_id]["storage"].get(item, 0) + 1
                    self.oil_usage[user_id]["storage"]["limit"] = self.oil_usage[user_id]["storage"]["limit"] + additional_capacity
                    self.oil_usage[user_id]["balance"] -= item_details["price"]
                    self.save_data()
                    self.save_inventory()
                    await interaction.response.send_message(f"Bought {item}. Your storage capacity has increased by {additional_capacity} cans. Use `/storage` to know your total capacity.")
                else:
                    self.oil_usage[user_id]["balance"] -= item_details["price"]
                    self.item_inventory[user_id].setdefault(category, {})[item] = 1
                    self.save_data()
                    self.save_inventory()
                    await interaction.response.send_message(f"Bought {item} from category {category}. Your balance is now ${self.oil_usage[user_id]['balance']}.")
                break

        if not item_found:
            await interaction.response.send_message(f"Item {item} not found in the store.", ephemeral=True)
        
   
    @app_commands.command(name='inventory', description="Show your inventory of items from the store")
    async def inventory_slash(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        
        user_inventory = self.item_inventory.get(user_id, {})
        
        embed = discord.Embed(title="Your Inventory", color=discord.Color.blue())

        # Loop through categories in the store and check if the user owns any items from each category
        for category, items in self.store_items.items():
            owned_items = {item_name: quantity for item_name, quantity in user_inventory.get(category, {}).items() if quantity > 0}
            
            if owned_items:
                # Add category as a field only if there are owned items
                item_list = "\n".join([f"{item}: {quantity}" for item, quantity in owned_items.items()])
                embed.add_field(name=category, value=item_list, inline=False)
        
        if not embed.fields:
            embed.description = "You don't own any items from the store."
        
        await interaction.response.send_message(embed=embed)


    # Get all the storage amount the user has
    async def get_storage_choices(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        user_id = str(interaction.user.id)
        user_storage = self.item_inventory.get(user_id, {}).get("Storage", {})

        choices = []
        for storage_type, quantity in user_storage.items():
            if quantity > 0 and storage_type.lower().startswith(current.lower()):
                choices.append(app_commands.Choice(name=storage_type, value=storage_type))
        
        if "all".startswith(current.lower()):
            choices.append(app_commands.Choice(name="all", value="all"))
        
        return choices


    @app_commands.command(name="sell", description="Sell oil to make money. Usage: /sell [amount] [storage type] or /sell all [storage type]")
    @app_commands.describe(amount="The amount of storage items to sell or 'all' to sell everything", storage_type="The type of storage to sell from")
    @app_commands.autocomplete(storage_type=get_storage_choices)
    async def sell_slash(self, interaction: discord.Interaction, amount: str, storage_type: str):
        user_id = str(interaction.user.id)
        
        
        
        if storage_type not in self.store_items.get("Storage", {}):
            await interaction.response.send_message(f"Invalid storage type. Available types: {', '.join(self.store_items.get('Storage', {}).keys())}.", ephemeral=True)
            return
    
        storage_item = self.store_items["Storage"][storage_type]
        storage_capacity = storage_item["capacity"]

        if amount.lower() == 'all':
            # Sell all oil in the specified storage type
            amount = self.oil_usage[user_id]["storage"].get(storage_type, 0)
        else:
            # Convert amount to integer and check validity
            try:
                amount = int(amount)
            except ValueError:
                await interaction.response.send_message("Invalid amount. Please specify a valid number or use 'all'.", ephemeral=True)
                return
            
        can_amount = amount * storage_capacity

        if self.oil_usage[user_id]["oil"] >= can_amount:
            self.oil_usage[user_id]["oil"] -= can_amount
            price_per_can = self.get_sell_price()
            total_price = can_amount * price_per_can
            self.oil_usage[user_id]["balance"] += total_price  # Add money to balance
            self.save_data()
            await interaction.response.send_message(f"Sold {amount} {storage_type}. Received ${total_price:.2f}.")
        else:
            await interaction.response.send_message("You don't have enough oil to sell.", ephemeral=True)

    def get_sell_price(self):
        # Define selling price chances
        prices = [0.50] * 50 + [0.35] * 20 + [0.20] * 5 + [0.65] * 19 + [0.80] * 4 + [1] * 2
        return random.choice(prices)
    
    
    @app_commands.command(name="balance", description="Check your balance and oil amount")
    async def balance_slash(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        
        
        embed = discord.Embed(title="Balance", color=discord.Color.gold())
        embed.add_field(name="Money", value=f"${self.oil_usage[user_id]['balance']:.2f}", inline=False)
        embed.add_field(name="Oil", value=f"{self.oil_usage[user_id]['oil']} cans", inline=False)
        embed.add_field(name="Storage Limit", value=f"{self.oil_usage[user_id]['storage']['limit']} cans", inline=False)

        await interaction.response.send_message(embed=embed)
        
    
    @app_commands.command(name="storage", description="Check your storage")
    async def storage_slash(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        

        current_storage = self.oil_usage[user_id]["oil"]
        storage_limit = self.oil_usage[user_id]["storage"]["limit"]

        units = [
            ('Can', 1),
            ('Drum', 1_000),
            ('Barrel', 1_000_000),
            ('Tanker', 1_000_000_000),
            ('Big Tanker', 1_000_000_000_000),
            ('Large Tanker', 1_000_000_000_000_000),
            ('Extra Large Tanker', 1_000_000_000_000_000_000),
            ('Mega Tanker', 1_000_000_000_000_000_000_000),
            ('Legendary Tanker', 1_000_000_000_000_000_000_000_000)
        ]

        def convert_units(amount):
            result = []
            for unit_name, unit_value in reversed(units):
                if amount >= unit_value:
                    result.append(f"{amount // unit_value} {unit_name}(s)")
                    amount %= unit_value
            return result

        current_storage_units = convert_units(current_storage)
        storage_limit_units = convert_units(storage_limit)

        embed = discord.Embed(title="Storage Information", color=discord.Color.blue())
        embed.add_field(name="Current Storage", value="\n".join(current_storage_units) if current_storage_units else "0 Cans", inline=False)
        embed.add_field(name="Storage Limit", value="\n".join(storage_limit_units) if storage_limit_units else "0 Cans", inline=False)
        embed.add_field(name="Total", value=f"\n {current_storage} out of {storage_limit}")
        embed.set_footer(text="Use the $store command to view or modify your storage.")

        await interaction.response.send_message(embed=embed)
        
        
    @app_commands.command(name='storage_units', description="Show the storage units and their conversions")
    async def storage_units_slash(self, interaction: discord.Interaction):
        # Define the storage units and their conversions
        storage_units_info = {
            "1 Can": "1 can",
            "1 Drum": "1,000 cans",
            "1 Barrel": "1,000 drums",
            "1 Tanker": "1,000 barrels",
            "1 Big Tanker": "1,000 tankers",
            "1 Large Tanker": "1,000 big tankers",
            "1 Extra Large Tanker": "1,000 large tankers",
            "1 Mega Tanker": "1,000 extra large tankers",
            "1 Legendary Tanker": "1,000 mega tankers"
        }

        embed = discord.Embed(title="Storage Units and Conversions", color=discord.Color.blue())
        
        for unit, conversion in storage_units_info.items():
            embed.add_field(name=unit, value=f"is {conversion}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    
async def setup(bot):
    await bot.add_cog(oilcommandslash(bot))

import discord
from discord.ext import commands
import json
import os
import random

class oilcommand(commands.Cog):
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
                "Drum": {"price": 1000, "capacity": 1000},
                "Barrel": {"price": 10000, "capacity": 1000**2},
                "Tanker": {"price": 50000, "capacity": 1000**3},
                "Big Tanker": {"price": 125000, "capacity": 1000**4},
                "Large Tanker": {"price": 200000, "capacity": 1000**5},
                "Extra Large Tanker": {"price": 300000, "capacity": 1000**6},
                "Mega Tanker": {"price": 450000, "capacity": 1000**7},
                "Legendary Tanker": {"price": 1000000, "capacity": 1000**8},
            }
        }

        self.cooldowns = {
            "Hand Pumps": 300,  # 5 minutes
            "Pumpjacks": 600    # 10 minutes
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

    
    @commands.command(name="initialize", help="Initialize your oil account.")
    async def initialize(self, ctx):
        user_id = str(ctx.author.id)
        await self.initialize_user_data(user_id)
        await ctx.send("Initialized!")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(name='work', help="Work using a specified item to extract oil. Usage: $work [item name]")
    async def work(self, ctx, *, item_name: str = None):
        if item_name is None:
            await ctx.send("You need to specify an item to use. Usage: `$work [item name]` Use $inv to check what items you have to work with. Did you buy a Hand pump from the store?")
            return

        user_id = str(ctx.author.id)

        # Convert item_name to lowercase for case-insensitive matching
        item_name_lower = item_name.lower()

        # Check if the item is in the user's inventory and if at least one is available
        user_inventory = self.item_inventory.get(user_id, {})
        item_found = False

        for category, items in user_inventory.items():
            if isinstance(items, dict):
                # Convert keys to lowercase for case-insensitive matching
                items_lower = {k.lower(): v for k, v in items.items()}
                if item_name_lower in items_lower and items_lower[item_name_lower] > 0:  # Check if at least one item is available
                    item_found = True
                    break

        if not item_found:
            await ctx.send(f"You do not have any of the item {item_name}. Please check your inventory.")
            return


        try:
            # Check if item exists in the store and get the extraction rate
            extraction_rate = None
            for category in ["Hand Pumps", "Pumpjacks"]:
                for store_item_name, item_details in self.store_items.get(category, {}).items():
                    if store_item_name.lower() == item_name_lower:
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
                    await ctx.send(f"Your storage is full. You could only store {extraction_rate - excess_oil} cans of oil. Consider buying a larger storage or selling your oil.")
                else:
                    self.oil_usage[user_id]["oil"] = new_oil_amount
                    await ctx.send(f"Used {item_name}. You have gained {extraction_rate} cans of oil. Your total is now {self.oil_usage[user_id]['oil']} cans.")

                self.save_data()
                self.save_inventory()
            else:
                await ctx.send(f"Item {item_name} not found in the store.")
        except Exception as e:
            await ctx.send(f"An error occurred while using {item_name}: {str(e)}")
    
    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are on cooldown! Try again in {round(error.retry_after)} seconds.")
        else:
            await ctx.send(f"An unexpected error occurred: {str(error)}")

    @commands.command(name='store', help="View the store")
    async def store(self, ctx, page: int = 1):
        if page == 1:
            category = "Hand Pumps"
        elif page == 2:
            category = "Pumpjacks"
        elif page == 3:
            category = "Storage"
        else:
            await ctx.send("Invalid page number.")
            return

        items = self.store_items.get(category, {})
        embed = discord.Embed(title=f"{category} Store", description="Available items for purchase", color=discord.Color.blue())
        for item, details in items.items():
            embed.add_field(name=item, value=f"Price: ${details['price']} - Extraction Rate: {details.get('extraction_rate', 'N/A')}", inline=False)

        if category == "Hand Pumps":
            embed.set_footer(text= "Page 1 of 3")
        elif category == "Pumpjacks":
            embed.set_footer(text= "Page 2 of 3")
        elif category == "Storage":
            embed.set_footer(text= "Page 3 of 3")
        
        await ctx.send(embed=embed)

    @commands.command(name='buy', help="Buy an item from the store. Usage: $buy [item]")
    async def buy(self, ctx, *, item: str = None):
        if item is None:
            await ctx.send("You need to specify an item to buy. Usage: `$buy [item]`")
            return

        user_id = str(ctx.author.id)

        # Convert item to lowercase for case-insensitive matching
        item = item.lower()
        item_found = False

        for category, items in self.store_items.items():
            # Convert item names in the store to lowercase for case-insensitive matching
            items_lower = {k.lower(): v for k, v in items.items()}

            if item in items_lower:
                item_details = items_lower[item]
                item_found = True

                # Check if the item is already owned
                if category != "Storage":  # Storage items can be purchased multiple times
                    if self.item_inventory[user_id].get(category, {}).get(item, 0) > 0:
                        await ctx.send(f"You already own {item}. You can't buy the same item again.")
                        return

                if self.oil_usage[user_id]["balance"] < item_details["price"]:
                    await ctx.send(f"You don't have enough balance to buy {item}.")
                    return

                if category == "Storage":
                    # Handle storage upgrades
                    additional_capacity = item_details["capacity"]

                    # Reflect the item bought in inventory.json
                    self.item_inventory[user_id][category][item] = self.item_inventory[user_id].get(category, {}).get(item, 0) + 1
                    
                    # Increase storage capacity
                    self.oil_usage[user_id]["storage"][item] = self.oil_usage[user_id]["storage"].get(item, 0) + 1
                    self.oil_usage[user_id]["storage"]["limit"] = self.oil_usage[user_id]["storage"]["limit"] + additional_capacity

                    # Deduct balance and save
                    self.oil_usage[user_id]["balance"] -= item_details["price"]
                    self.save_data()
                    self.save_inventory()

                    await ctx.send(f"Bought {item}. Your storage capacity has increased by {additional_capacity} cans. Use $storage to know your total capacity.")
                else:
                    # Handle hand pumps and pumpjacks
                    self.oil_usage[user_id]["balance"] -= item_details["price"]
                    self.item_inventory[user_id].setdefault(category, {})[item] = 1  # Ensure item count starts at 1
                    self.save_data()
                    self.save_inventory()

                    await ctx.send(f"Bought {item} from category {category}. Your balance is now ${self.oil_usage[user_id]['balance']}.")
                break

        if not item_found:
            await ctx.send(f"Item {item} not found in the store.")

               
    @commands.command(name='inventory', aliases=['inv'], help="Show your inventory of items from the store")
    async def inventory(self, ctx):
        user_id = str(ctx.author.id)
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
        
        await ctx.send(embed=embed)

        
    @commands.command(name='sell', help="Sell oil to make money. Usage: $sell [amount] [storage type] or $sell all [storage type]")
    async def sell(self, ctx, amount: str, storage_type: str):
        user_id = str(ctx.author.id)


        if storage_type not in self.store_items.get("Storage", {}):
            await ctx.send(f"Invalid storage type. Available types: {', '.join(self.store_items.get('Storage', {}).keys())}.")
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
                await ctx.send("Invalid amount. Please specify a valid number or use 'all'.")
                return
        
        can_amount = amount * storage_capacity

        if self.oil_usage[user_id]["oil"] >= can_amount:
            self.oil_usage[user_id]["oil"] -= can_amount
            price_per_can = self.get_sell_price()
            total_price = can_amount * price_per_can
            self.oil_usage[user_id]["balance"] += total_price  # Add money to balance
            self.save_data()
            await ctx.send(f"Sold {amount} {storage_type}. Received ${total_price:.2f}.")
        else:
            await ctx.send("You don't have enough oil to sell.")

    def get_sell_price(self):
        # Define selling price chances
        prices = [0.50] * 50 + [0.35] * 20 + [0.20] * 5 + [0.65] * 19 + [0.80] * 4 + [1] * 2
        return random.choice(prices)

    @commands.command(name='balance', aliases=['bal'], help="Check your balance and oil amount")
    async def balance(self, ctx):
        user_id = str(ctx.author.id)
        
        embed = discord.Embed(title="Balance", color=discord.Color.gold())
        embed.add_field(name="Money", value=f"${self.oil_usage[user_id]['balance']:.2f}", inline=False)
        embed.add_field(name="Oil", value=f"{self.oil_usage[user_id]['oil']} cans", inline=False)
        embed.add_field(name="Storage Limit", value=f"{self.oil_usage[user_id]['storage']['limit']} cans", inline=False)

        await ctx.send(embed=embed)
        

    @commands.command(name='storage', help="Check your storage")
    async def storage(self, ctx):
        user_id = str(ctx.author.id)

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

        await ctx.send(embed=embed)

    @commands.command(name='storage_units', help="Show the storage units and their conversions")
    async def storage_units(self, ctx):
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
        
        await ctx.send(embed=embed)


# Setup function to add this cog to the bot
async def setup(bot):
    await bot.add_cog(oilcommand(bot))
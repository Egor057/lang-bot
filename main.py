import asyncio
import logging
import sys
import json
import os
import random
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# ==============================================================================
# SECTION 0: SYSTEM LOGGING SETUP (CRITICAL: MUST BE AT THE VERY TOP)
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("LanguageBotCore")


# ==============================================================================
# SECTION 1: RENDER 24/7 HTTP KEEPALIVE WEB SERVER (BACKGROUND THREAD)
# ==============================================================================
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class RenderKeepAliveHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler designed to satisfy Render's web service port binding requirement.
    Responds with HTTP 200 OK to any incoming health-check requests to prevent spin-down.
    """
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"LanguageBotCore Web Service is active and operational 24/7!")
        except Exception as e:
            logger.error(f"Error handling HTTP keep-alive GET request: {e}")

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress standard HTTP server access logs to keep terminal output clean
        pass

def start_web_server_daemon() -> None:
    """
    Spawns the HTTP server in a separate background daemon thread.
    Reads PORT from environment variables (defaults to 10000 for Render).
    """
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), RenderKeepAliveHandler)
        logger.info(f"HTTP Keep-Alive server successfully bound to port {port}")
        server.serve_forever()
    except Exception as ex:
        logger.critical(f"Failed to start background HTTP server: {ex}")

# Initialize and start the background web server thread immediately
threading.Thread(target=start_web_server_daemon, daemon=True).start()


# ==============================================================================
# SECTION 2: IMPORTS OF AIOGRAM AND CUSTOM MODULES
# ==============================================================================
from vocabulary_detective import DETECTIVE_SCENARIOS
from vocabulary_adventure import ADVENTURE_SCENARIOS
from vocabulary_chat_sim import CHAT_SCENARIOS, FAIL_SCENARIOS, VICTORY_SCENARIOS
from vocabulary_homework import get_random_homework_task

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    PreCheckoutQuery,
    LabeledPrice,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.exceptions import TelegramAPIError

# Core router instantiation
router = Router()


# ==============================================================================
# SECTION 3: ROBUST DATABASE MANAGEMENT SYSTEM
# ==============================================================================
BOT_TOKEN = "9084719584:AAGuBzbaD9qtOEoR4Hw4Ok_eL9Miic35Nb4"
ADMIN_TELEGRAM_ID = 9136166835

DB_FILENAME = "users_database.json"
DB_BACKUP_FILENAME = "users_database_backup.json"

def initialize_database() -> None:
    """Ensures the primary JSON database file exists on disk."""
    if not os.path.exists(DB_FILENAME):
        logger.info("Initializing new persistent user database file...")
        try:
            with open(DB_FILENAME, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.critical(f"Failed to create database file: {e}")

def load_db() -> Dict[str, Any]:
    """Loads user records from JSON database with automatic backup recovery."""
    initialize_database()
    try:
        with open(DB_FILENAME, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as jde:
        logger.error(f"Database JSON corruption detected ({jde}). Restoring from backup...")
        if os.path.exists(DB_BACKUP_FILENAME):
            try:
                with open(DB_BACKUP_FILENAME, "r", encoding="utf-8") as bf:
                    data = json.load(bf)
                logger.info("Successfully restored user database from backup file.")
                return data
            except Exception as be:
                logger.error(f"Backup restoration failed: {be}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading database: {e}")
        return {}

def save_db(data: Dict[str, Any]) -> None:
    """Saves user records to JSON database with pre-save backup creation."""
    try:
        if os.path.exists(DB_FILENAME):
            shutil.copy(DB_FILENAME, DB_BACKUP_FILENAME)
        with open(DB_FILENAME, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Critical error saving database state: {e}")

# Perform initial database setup
initialize_database()


# ==============================================================================
# SECTION 4: FINITE STATE MACHINE (FSM) STATES
# ==============================================================================
class BotStates(StatesGroup):
    selecting_vocabulary_level = State()
    active_learning_session = State()
    quiz_question_active = State()
    admin_broadcast_state = State()


# ==============================================================================
# SECTION 5: VOCABULARY DATASETS & EXTENDED GRAMMAR DIRECTORY
# ==============================================================================
try:
    from vocabulary_a1 import WORDS_A1
except ImportError:
    WORDS_A1 = [{"word": "Hello", "trans": "[həˈloʊ]", "ru": "Привет", "ex": "Hello world."}]

try:
    from vocabulary_a2 import WORDS_A2
except ImportError:
    WORDS_A2 = [{"word": "Example", "trans": "[ɪɡˈzɑːm.pəl]", "ru": "Пример", "ex": "This is an example."}]

try:
    from vocabulary_b1 import WORDS_B1
except ImportError:
    WORDS_B1 = [{"word": "Access", "trans": "[ˈæk.ses]", "ru": "Доступ", "ex": "Get access."}]

try:
    from vocabulary_b2 import WORDS_B2
except ImportError:
    WORDS_B2 = [{"word": "Ability", "trans": "[əˈbɪl.ə.ti]", "ru": "Способность", "ex": "Natural ability."}]

try:
    from vocabulary_c1 import WORDS_C1
except ImportError:
    WORDS_C1 = [{"word": "Abundant", "trans": "[əˈbʌn.dənt]", "ru": "Изобильный", "ex": "Abundant resources."}]

EXTENDED_GRAMMAR_DATABASE = {
    "nominatiivi": {
        "title": "Nominatiivi (Именительный падеж)",
        "questions": "Kuka? Mikä? (Кто? Что?)",
        "purpose": "Словарная форма слова в финском языке.",
        "rules": "Нулевое окончание в единственном числе.",
        "examples": ["Tämä on auto. (Это машина.)", "Koira nukkuu. (Собака спит.)"],
        "tips": "Используется для подлежащего в предложении."
    },
    "genetiivi": {
        "title": "Genetiivi (Родительный падеж)",
        "questions": "Kenen? Minkä? (Кого? Чего?)",
        "purpose": "Обозначает принадлежность или обладателя.",
        "rules": "Окончание: -n.",
        "examples": ["Tämä on isän auto. (Это машина отца.)"],
        "tips": "Следите за сильной и слабой ступенью согласных."
    },
    "partitiivi": {
        "title": "Partitiivi (Партитив)",
        "questions": "Ketä? Mitä? (Кого? Что?)",
        "purpose": "Выражает частичность, неопределенное количество или используется при отрицании.",
        "rules": "Окончания: -a, -ä, -ta, -tä.",
        "examples": ["Minä syön leipää. (Я ем хлеб.)", "En ymmärrä. (Я не понимаю.)"],
        "tips": "Самый часто используемый падеж в повседневной финской речи."
    }
}


# ==============================================================================
# SECTION 6: UI KEYBOARDS BUILDERS (REPLY & INLINE)
# ==============================================================================
def build_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Constructs the primary persistent reply keyboard layout."""
    rows = [
        [KeyboardButton(text="📚 Учить слова"), KeyboardButton(text="🎯 Режим тестов")],
        [KeyboardButton(text="🎮 Игры и квесты ⭐"), KeyboardButton(text="📚 Домашнее задание")],
        [KeyboardButton(text="👤 Профиль и Статистика"), KeyboardButton(text="📖 Справочник падежей")],
        [KeyboardButton(text="⭐ Купить Премиум"), KeyboardButton(text="⚙️ Настройки")]
    ]
    if is_admin:
        rows.append([KeyboardButton(text="👑 Панель администратора")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, persistent=True)

def build_games_menu_keyboard() -> InlineKeyboardMarkup:
    """Constructs the interactive inline keyboard for games selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Детективный квест ⭐", callback_data="start_game_detective")],
            [InlineKeyboardButton(text="💬 Чат-симулятор ⭐", callback_data="start_game_chatsim")],
            [InlineKeyboardButton(text="🗺️ Квест в Лондоне (Путешествие) ⭐", callback_data="start_game_adventure")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")]
        ]
    )

def build_levels_selection_keyboard() -> InlineKeyboardMarkup:
    """Constructs vocabulary level selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Уровень A1", callback_data="setlevel_a1")],
            [InlineKeyboardButton(text="🟢 Уровень A2", callback_data="setlevel_a2")],
            [InlineKeyboardButton(text="🟡 Уровень B1", callback_data="setlevel_b1")],
            [InlineKeyboardButton(text="🟠 Уровень B2", callback_data="setlevel_b2")],
            [InlineKeyboardButton(text="🔴 Уровень C1 (Премиум ⭐)", callback_data="setlevel_c1")],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="action_main_menu")]
        ]
    )

def build_learning_actions_keyboard() -> InlineKeyboardMarkup:
    """Constructs inline buttons for active vocabulary sessions."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Следующее слово", callback_data="action_next_word")],
            [InlineKeyboardButton(text="🔤 Изменить уровень", callback_data="action_change_level")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")]
        ]
    )

def build_grammar_directory_keyboard() -> InlineKeyboardMarkup:
    """Constructs inline keyboard for grammar case directory."""
    rows = []
    for code, info in EXTENDED_GRAMMAR_DATABASE.items():
        short_title = info["title"].split(" ")[0]
        rows.append([InlineKeyboardButton(text=f"📌 {short_title}", callback_data=f"grammar_info_{code}")])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ==============================================================================
# SECTION 7: CORE HANDLERS (/start, PROFILE, GRAMMAR)
# ==============================================================================
@router.message(CommandStart())
async def handle_start_command(message: Message, state: FSMContext) -> None:
    """Handles the /start command, registers new users, and displays welcome UI."""
    await state.clear()
    uid_str = str(message.from_user.id)
    database = load_db()
    
    if uid_str not in database:
        database[uid_str] = {
            "first_name": message.from_user.first_name or "Ученик",
            "level": "a1",
            "words_learned": 0,
            "correct_answers": 0,
            "quiz_score": 0,
            "is_premium": False,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_db(database)
        logger.info(f"Registered new user: {message.from_user.id} ({message.from_user.first_name})")

    is_admin = message.from_user.id == ADMIN_TELEGRAM_ID
    
    # User's requested detailed welcome message structure
    welcome_message = (
        f"👋 Здравствуй, **{html.quote(message.from_user.first_name)}**!\n\n"
        "Добро пожаловать в систему изучения языковой лексики и премиум-квестов.\n"
        "Выбирай нужный раздел в меню ниже 👇"
    )
    
    await message.answer(
        welcome_message,
        parse_mode="Markdown",
        reply_markup=build_main_menu_keyboard(is_administrator=is_admin)
    )

@router.message(F.text == "👤 Профиль и Статистика")
async def handle_profile_request(message: Message) -> None:
    """Displays detailed user profile and performance statistics."""
    uid_str = str(message.from_user.id)
    db = load_db()
    info = db.get(uid_str, {
        "level": "a1", "words_learned": 0, "correct_answers": 0,
        "quiz_score": 0, "is_premium": False, "joined_date": "Неизвестно"
    })
    sub_status = "🟢 Активна (Премиум ⭐)" if info.get("is_premium") else "⚪️ Базовый"
    
    profile_text = (
        f"📊 **Твой персональный профиль:**\n\n"
        f"👤 Имя: {html.quote(message.from_user.first_name)}\n"
        f"🆔 ID: `{message.from_user.id}`\n"
        f"📈 Уровень: `{info.get('level').upper()}`\n"
        f"🧠 Просмотрено слов: `{info.get('words_learned', 0)}`\n"
        f"✨ Правильных ответов: `{info.get('correct_answers', 0)}`\n"
        f"🏆 Очки: `{info.get('quiz_score', 0)}`\n"
        f"💎 Подписка: {sub_status}\n"
        f"📅 Дата регистрации: `{info.get('joined_date', 'Неизвестно')}`"
    )
    await message.answer(profile_text, parse_mode="Markdown")

@router.message(F.text == "📖 Справочник падежей")
async def handle_grammar_menu(message: Message) -> None:
    """Opens the grammar reference directory."""
    await message.answer(
        "📚 **Интерактивный справочник грамматики:**\nВыберите интересующий вас падеж:",
        parse_mode="Markdown",
        reply_markup=build_grammar_directory_keyboard()
    )

@router.callback_query(F.data.startswith("grammar_info_"))
async def process_grammar_card(callback: CallbackQuery) -> None:
    """Displays detailed grammar card info based on user selection."""
    code = callback.data.split("_")[2]
    data = EXTENDED_GRAMMAR_DATABASE.get(code)
    if not data:
        await callback.answer("⚠️ Информация не найдена.", show_alert=True)
        return
    exs = "\n".join([f"• {ex}" for ex in data["examples"]])
    text = (
        f"📖 **{data['title']}**\n\n"
        f"❓ Вопросы: `{data['questions']}`\n\n"
        f"🎯 Назначение: {data['purpose']}\n"
        f"⚙️ Правило: {data['rules']}\n\n"
        f"💡 Примеры:\n{exs}\n\n"
        f"📌 Совет: *{data['tips']}*"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=build_grammar_directory_keyboard())
    await callback.answer()

@router.callback_query(F.data == "action_main_menu")
async def return_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Returns the user safely to the main menu."""
    await state.clear()
    is_admin = callback.from_user.id == ADMIN_TELEGRAM_ID
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("🏠 Главное меню:", reply_markup=build_main_menu_keyboard(is_administrator=is_admin))
    await callback.answer()


# ==============================================================================
# SECTION 8: HOMEWORK MODULE
# ==============================================================================
@router.message(F.text.in_(["📚 Домашнее задание", "/homework", "📝 ДЗ"]))
async def handle_homework_request(message: Message) -> None:
    """Provides a random interactive homework task."""
    task_key, hw = get_random_homework_task()
    keyboard_buttons = []
    for opt in hw["options"]:
        marker = "1" if opt["correct"] else "0"
        keyboard_buttons.append([InlineKeyboardButton(text=opt["text"], callback_data=f"hw_ans:{marker}")])
    keyboard_buttons.append([InlineKeyboardButton(text="🔄 Другое ДЗ", callback_data="hw_reload")])
    keyboard_buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")])

    hw_text = f"🎯 **{hw['title']}**\n\n💡 _{hw['description']}_\n\n❓ **Задание:**\n{hw['task_text']}"
    await message.answer(hw_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons), parse_mode="Markdown")

@router.callback_query(F.data == "hw_reload")
async def reload_homework_callback(callback: CallbackQuery) -> None:
    """Generates a new homework task on callback."""
    task_key, hw = get_random_homework_task()
    keyboard_buttons = []
    for opt in hw["options"]:
        marker = "1" if opt["correct"] else "0"
        keyboard_buttons.append([InlineKeyboardButton(text=opt["text"], callback_data=f"hw_ans:{marker}")])
    keyboard_buttons.append([InlineKeyboardButton(text="🔄 Другое ДЗ", callback_data="hw_reload")])
    keyboard_buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")])

    await callback.message.edit_text(
        f"🎯 **{hw['title']}**\n\n💡 _{hw['description']}_\n\n❓ **Задание:**\n{hw['task_text']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("hw_ans:"))
async def process_homework_answer(callback: CallbackQuery) -> None:
    """Evaluates homework answer."""
    is_correct = callback.data.split(":")[1] == "1"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Другое ДЗ", callback_data="hw_reload")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")]
    ])
    if is_correct:
        await callback.message.edit_text("✅ **Правильно! Отличная работа!** 🎉", parse_mode="Markdown", reply_markup=markup)
    else:
        await callback.message.edit_text("❌ **Неверно.** Попробуй другое задание или повтори теорию.", parse_mode="Markdown", reply_markup=markup)
    await callback.answer()


# ==============================================================================
# SECTION 9: GAMES & PREMIUM QUESTS (DETECTIVE, CHAT SIMULATOR, LONDON ADVENTURE)
# ==============================================================================
@router.message(F.text == "🎮 Игры и квесты ⭐")
async def handle_games_menu(message: Message) -> None:
    """Displays the games and quests selection menu."""
    await message.answer(
        "🎮 **Интерактивные игры и квесты (Премиум ⭐):**\n\n"
        "Выбирай захватывающее приключение или симуляцию из списка ниже:",
        parse_mode="Markdown",
        reply_markup=build_games_menu_keyboard()
    )

@router.callback_query(F.data == "open_games_menu")
async def cb_open_games_menu(callback: CallbackQuery) -> None:
    """Opens games menu via callback query."""
    await callback.message.edit_text(
        "🎮 **Интерактивные игры и квесты (Премиум ⭐):**\n\n"
        "Выбирай захватывающее приключение или симуляцию из списка ниже:",
        parse_mode="Markdown",
        reply_markup=build_games_menu_keyboard()
    )
    await callback.answer()

# --- 9.1 Detective Quest ---
@router.callback_query(F.data == "start_game_detective")
async def cb_start_detective(callback: CallbackQuery) -> None:
    """Starts the Detective Quest if premium is active."""
    user_id = callback.from_user.id
    db = load_db()
    if not db.get(str(user_id), {}).get("is_premium", False):
        await callback.message.edit_text(
            "🔒 **Детективный квест доступен по Премиум-подписке!**\nСтоимость: **50 Telegram Stars (⭐)**.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⭐ Купить Премиум за 50 Звезд", callback_data="buy_premium_trigger")],
                [InlineKeyboardButton(text="◀️ Назад к играм", callback_data="open_games_menu")]
            ]),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    money, energy, rep, clues = 50, 100, 10, 0
    scene = DETECTIVE_SCENARIOS["start"]
    btns = []
    for btn in scene["buttons"]:
        cb = f"det:{btn['next']}:{money + btn.get('money', 0)}:{energy + btn.get('energy', 0)}:{rep + btn.get('rep', 0)}:{clues + btn.get('clues', 0)}"
        btns.append([InlineKeyboardButton(text=btn["text"], callback_data=cb)])
    btns.append([InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")])

    await callback.message.edit_text(
        f"💷 £{money} | ⚡ {energy}% | 🔥 Реп: {rep} | 🔎 Улики: {clues}\n━━━━━━━━━━━━━━━━━━━\n\n*{scene['title']}*\n\n{scene['text']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("det:"))
async def process_detective_choice(callback: CallbackQuery) -> None:
    """Processes player choices in the Detective Quest."""
    parts = callback.data.split(":")
    next_key, m, e, r, c = parts[1], int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
    scene = DETECTIVE_SCENARIOS.get(next_key, DETECTIVE_SCENARIOS["start"])

    btns = []
    for btn in scene.get("buttons", []):
        cb = f"det:{btn['next']}:{m + btn.get('money', 0)}:{e + btn.get('energy', 0)}:{r + btn.get('rep', 0)}:{c + btn.get('clues', 0)}"
        btns.append([InlineKeyboardButton(text=btn["text"], callback_data=cb)])
    btns.append([InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")])

    await callback.message.edit_text(
        f"💷 £{m} | ⚡ {e}% | 🔥 Реп: {r} | 🔎 Улики: {c}\n━━━━━━━━━━━━━━━━━━━\n\n*{scene['title']}*\n\n{scene['text']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns),
        parse_mode="Markdown"
    )
    await callback.answer()

# --- 9.2 Chat Simulator ---
@router.callback_query(F.data == "start_game_chatsim")
async def cb_start_chatsim(callback: CallbackQuery) -> None:
    """Starts the Chat Simulator if premium is active."""
    user_id = callback.from_user.id
    db = load_db()
    if not db.get(str(user_id), {}).get("is_premium", False):
        await callback.message.edit_text(
            "🔒 **Чат-симулятор доступен по Премиум-подписке!**\nСтоимость: **50 Telegram Stars (⭐)**.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⭐ Купить Премиум за 50 Звезд", callback_data="buy_premium_trigger")],
                [InlineKeyboardButton(text="◀️ Назад к играм", callback_data="open_games_menu")]
            ]),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    scene = CHAT_SCENARIOS["start"]
    btns = []
    for opt in scene["options"]:
        marker = "1" if opt["correct"] else "0"
        btns.append([InlineKeyboardButton(text=opt["text"], callback_data=f"chatsim:{opt['next']}:{marker}")])
    btns.append([InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")])

    await callback.message.edit_text(
        f"💬 **{scene['character']}**\n━━━━━━━━━━━━━━━━━━━\n\n📱 *{scene['dialogue']}*",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("chatsim:"))
async def process_chatsim_choice(callback: CallbackQuery) -> None:
    """Processes player responses in the Chat Simulator."""
    parts = callback.data.split(":")
    next_key, is_correct = parts[1], parts[2] == "1"

    if next_key.startswith("victory_"):
        scen = CHAT_SCENARIOS[next_key]
        await callback.message.edit_text(
            f"🎉 **{scen['title']}**\n\n{scen['text']}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Заново", callback_data="start_game_chatsim")],
                [InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")]
            ]),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    if not is_correct or next_key.startswith("fail_"):
        scen = CHAT_SCENARIOS.get(next_key, {"title": "💀 Game Over", "text": "Ошибка в диалоге."})
        await callback.message.edit_text(
            f"❌ **{scen['title']}**\n\n{scen['text']}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Повторить", callback_data="start_game_chatsim")],
                [InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")]
            ]),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    scene = CHAT_SCENARIOS.get(next_key, CHAT_SCENARIOS["start"])
    btns = []
    for opt in scene["options"]:
        marker = "1" if opt["correct"] else "0"
        btns.append([InlineKeyboardButton(text=opt["text"], callback_data=f"chatsim:{opt['next']}:{marker}")])
    btns.append([InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")])

    await callback.message.edit_text(
        f"💬 **Собеседник: {scene['character']}**\n━━━━━━━━━━━━━━━━━━━\n\n✅ *{scene.get('feedback', 'Ответ принят.')}*\n\n📱 *{scene['dialogue']}*",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns),
        parse_mode="Markdown"
    )
    await callback.answer()

# --- 9.3 London Adventure Quest ---
@router.callback_query(F.data == "start_game_adventure")
async def cb_start_adventure(callback: CallbackQuery) -> None:
    """Starts the London Adventure Quest if premium is active."""
    user_id = callback.from_user.id
    db = load_db()
    if not db.get(str(user_id), {}).get("is_premium", False):
        await callback.message.edit_text(
            "🔒 **Квест в Лондоне (Путешествие) доступен по Премиум-подписке!**\nСтоимость: **50 Telegram Stars (⭐)**.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⭐ Купить Премиум за 50 Звезд", callback_data="buy_premium_trigger")],
                [InlineKeyboardButton(text="◀️ Назад к играм", callback_data="open_games_menu")]
            ]),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    money, energy, rep = 40, 100, 10
    scene = ADVENTURE_SCENARIOS["start"]
    btns = []
    for btn in scene["buttons"]:
        cb = f"adv:{btn['next']}:{money + btn.get('money', 0)}:{energy + btn.get('energy', 0)}:{rep + btn.get('rep', 0)}"
        btns.append([InlineKeyboardButton(text=btn["text"], callback_data=cb)])
    btns.append([InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")])

    await callback.message.edit_text(
        f"💷 £{money} | ⚡ {energy}% | 🔥 Реп: {rep}\n━━━━━━━━━━━━━━━━━━━\n\n*{scene['title']}*\n\n{scene['text']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("adv:"))
async def process_adventure_choice(callback: CallbackQuery) -> None:
    """Processes choices in London Adventure Quest."""
    parts = callback.data.split(":")
    next_key, m, e, r = parts[1], int(parts[2]), int(parts[3]), int(parts[4])
    scene = ADVENTURE_SCENARIOS.get(next_key, ADVENTURE_SCENARIOS["start"])

    btns = []
    for btn in scene.get("buttons", []):
        cb = f"adv:{btn['next']}:{m + btn.get('money', 0)}:{e + btn.get('energy', 0)}:{r + btn.get('rep', 0)}"
        btns.append([InlineKeyboardButton(text=btn["text"], callback_data=cb)])
    btns.append([InlineKeyboardButton(text="◀️ К играм", callback_data="open_games_menu")])

    await callback.message.edit_text(
        f"💷 £{m} | ⚡ {e}% | 🔥 Реп: {r}\n━━━━━━━━━━━━━━━━━━━\n\n*{scene['title']}*\n\n{scene['text']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns),
        parse_mode="Markdown"
    )
    await callback.answer()


# ==============================================================================
# SECTION 10: VOCABULARY LEARNING & QUIZ MODULES (A1 - C1)
# ==============================================================================
@router.message(F.text == "📚 Учить слова")
async def entry_vocab(message: Message, state: FSMContext) -> None:
    """Initiates vocabulary level selection."""
    await message.answer("🔤 **Выбери языковой уровень:**", parse_mode="Markdown", reply_markup=build_levels_selection_keyboard())
    await state.set_state(BotStates.selecting_vocabulary_level)

@router.callback_query(F.data.startswith("setlevel_"), StateFilter(BotStates.selecting_vocabulary_level, BotStates.active_learning_session))
async def set_vocab_level(callback: CallbackQuery, state: FSMContext) -> None:
    """Sets the chosen vocabulary level, gating C1 behind Premium."""
    lvl = callback.data.split("_")[1]
    uid_str = str(callback.from_user.id)
    if lvl == "c1":
        db = load_db()
        if not db.get(uid_str, {}).get("is_premium", False):
            await callback.answer("⚠️ Уровень C1 доступен только по Премиум-подписке ⭐!", show_alert=True)
            return
    db = load_db()
    if uid_str in db:
        db[uid_str]["level"] = lvl
        save_db(db)
    await state.update_data(active_vocab_level=lvl)
    await state.set_state(BotStates.active_learning_session)
    await callback.message.edit_text(f"✅ Уровень изменен на **{lvl.upper()}**.", parse_mode="Markdown")
    await dispatch_card(callback.message, lvl, replace=True)
    await callback.answer()

async def dispatch_card(message: Message, level_code: str, replace: bool = False) -> None:
    """Dispatches a random vocabulary learning card."""
    maps = {"a1": WORDS_A1, "a2": WORDS_A2, "b1": WORDS_B1, "b2": WORDS_B2, "c1": WORDS_C1}
    word = random.choice(maps.get(level_code, WORDS_A1))
    card = (
        f"📖 **Карточка ({level_code.upper()})**\n\n"
        f"🔤 **{html.quote(word.get('word', ''))}**\n"
        f"🔊 `{html.quote(word.get('trans', ''))}`\n"
        f"🇷🇺 **{html.quote(word.get('ru', ''))}**\n\n"
        f"💡 *{html.quote(word.get('ex', ''))}*"
    )
    
    uid_str = str(message.chat.id)
    db = load_db()
    if uid_str in db:
        db[uid_str]["words_learned"] = db[uid_str].get("words_learned", 0) + 1
        save_db(db)

    if replace:
        try:
            await message.edit_text(card, parse_mode="Markdown", reply_markup=build_learning_actions_keyboard())
        except Exception:
            await message.answer(card, parse_mode="Markdown", reply_markup=build_learning_actions_keyboard())
    else:
        await message.answer(card, parse_mode="Markdown", reply_markup=build_learning_actions_keyboard())

@router.callback_query(F.data == "action_next_word", StateFilter(BotStates.active_learning_session))
async def next_word(callback: CallbackQuery, state: FSMContext) -> None:
    """Shows the next vocabulary word card."""
    data = await state.get_data()
    await dispatch_card(callback.message, data.get("active_vocab_level", "a1"), replace=True)
    await callback.answer()

@router.callback_query(F.data == "action_change_level")
async def change_level(callback: CallbackQuery, state: FSMContext) -> None:
    """Allows changing vocabulary level during learning session."""
    await callback.message.edit_text("🔤 Выбери уровень:", parse_mode="Markdown", reply_markup=build_levels_selection_keyboard())
    await state.set_state(BotStates.selecting_vocabulary_level)
    await callback.answer()

@router.message(F.text == "🎯 Режим тестов")
async def entry_quiz(message: Message, state: FSMContext) -> None:
    """Initiates an interactive multiple-choice quiz question."""
    uid_str = str(message.from_user.id)
    db = load_db()
    lvl = db.get(uid_str, {}).get("level", "a1")
    maps = {"a1": WORDS_A1, "a2": WORDS_A2, "b1": WORDS_B1, "b2": WORDS_B2, "c1": WORDS_C1}
    pool = maps.get(lvl, WORDS_A1)
    
    correct = random.choice(pool)
    distractors = random.sample([i for i in pool if i["word"] != correct["word"]], min(3, len(pool) - 1))
    options = distractors + [correct]
    random.shuffle(options)
    
    await state.update_data(quiz_correct_ru=correct["ru"])
    await state.set_state(BotStates.quiz_question_active)
    
    btns = [[InlineKeyboardButton(text=opt["ru"], callback_data=f"quizanswer_{opt['ru']}")] for opt in options]
    btns.append([InlineKeyboardButton(text="❌ Выход", callback_data="action_main_menu")])
    
    await message.answer(f"🎯 **Тест ({lvl.upper()})**\n\nКак переводится: **{html.quote(correct['word'])}**?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

@router.callback_query(F.data.startswith("quizanswer_"), StateFilter(BotStates.quiz_question_active))
async def eval_quiz(callback: CallbackQuery, state: FSMContext) -> None:
    """Evaluates user's quiz answer and awards scores."""
    chosen = callback.data.split("_", 1)[1]
    data = await state.get_data()
    correct = data.get("quiz_correct_ru")
    uid_str = str(callback.from_user.id)
    db = load_db()
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Следующий", callback_data="action_next_quiz")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="action_main_menu")]
    ])
    
    if chosen == correct:
        if uid_str in db:
            db[uid_str]["correct_answers"] = db[uid_str].get("correct_answers", 0) + 1
            db[uid_str]["quiz_score"] = db[uid_str].get("quiz_score", 0) + 15
            save_db(db)
        await callback.message.edit_text("✅ **Верно! (+15 очков)** 🎉", parse_mode="Markdown", reply_markup=markup)
    else:
        await callback.message.edit_text(f"❌ **Ошибка.** Правильно: *{correct}*.", parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data == "action_next_quiz")
async def next_quiz(callback: CallbackQuery, state: FSMContext) -> None:
    """Proceeds to the next quiz question."""
    await entry_quiz(callback.message, state)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()


# ==============================================================================
# SECTION 11: SETTINGS & TELEGRAM STARS PAYMENTS
# ==============================================================================
@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message) -> None:
    """Opens user settings menu."""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сбросить статистику", callback_data="settings_reset_stats")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")]
    ])
    await message.answer("⚙️ **Настройки бота:**", parse_mode="Markdown", reply_markup=markup)

@router.callback_query(F.data == "settings_reset_stats")
async def reset_stats(callback: CallbackQuery) -> None:
    """Resets user statistics."""
    uid_str = str(callback.from_user.id)
    db = load_db()
    if uid_str in db:
        db[uid_str]["words_learned"] = 0
        db[uid_str]["correct_answers"] = 0
        db[uid_str]["quiz_score"] = 0
        save_db(db)
    await callback.answer("🔄 Статистика сброшена!", show_alert=True)
    await callback.message.edit_text("✅ Твоя статистика обнулена.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Главное меню", callback_data="action_main_menu")]]))

@router.message(Command("buy"))
@router.message(F.text.in_(["⭐ Купить Премиум", "buy_premium_trigger"]))
async def buy_premium(message: Message) -> None:
    """Sends Telegram Stars invoice for Premium subscription."""
    prices = [LabeledPrice(label="Премиум доступ ко всем играм и C1", amount=50)]
    await message.answer_invoice(
        title="⭐ Премиум-подписка",
        description="Открывает детектив, чат-симулятор, квест в Лондоне (путешествие) и уровень C1!",
        prices=prices,
        payload="premium_sub_payload",
        currency="XTR",
        provider_token=""
    )

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    """Validates pre-checkout queries for Telegram Stars."""
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    """Activates premium status upon successful payment."""
    uid_str = str(message.from_user.id)
    db = load_db()
    if uid_str in db:
        db[uid_str]["is_premium"] = True
        save_db(db)
    
    is_admin = message.from_user.id == ADMIN_TELEGRAM_ID
    await message.answer("🎉 **Оплата прошла успешно! Премиум активирован!** ⭐\nВсе игры, квесты и уровень C1 теперь полностью разблокированы.", parse_mode="Markdown", reply_markup=build_main_menu_keyboard(is_admin))


# ==============================================================================
# SECTION 12: ADMINISTRATOR MANAGEMENT PANEL
# ==============================================================================
@router.message(F.text == "👑 Панель администратора")
async def admin_panel_handler(message: Message) -> None:
    """Displays admin analytics and server status."""
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        await message.answer("⛔ У тебя нет доступа к этой панели.")
        return
    db = load_db()
    total_users = len(db)
    premium_users = sum(1 for u in db.values() if u.get("is_premium"))
    
    text = (
        f"👑 **Панель администратора:**\n\n"
        f"👥 Всего пользователей в базе: `{total_users}`\n"
        f"💎 Премиум пользователей: `{premium_users}`\n"
        f"🟢 Статус сервера: `Работает 24/7 (Render Keep-Alive)`"
    )
    await message.answer(text, parse_mode="Markdown")


# ==============================================================================
# SECTION 13: MAIN POLLING & BOT EXECUTION ENTRYPOINT
# ==============================================================================
async def main() -> None:
    """Main asynchronous entrypoint for running the aiogram polling dispatcher."""
    logger.info("Starting LanguageBotCore polling engine...")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook successfully dropped, initiating start_polling()...")
        await dp.start_polling(bot)
    except TelegramAPIError as e:
        logger.critical(f"Critical Telegram API error encountered: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot session closed gracefully.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot execution terminated by user or system signal.")
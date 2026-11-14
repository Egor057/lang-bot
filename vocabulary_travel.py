import random

# ==========================================
# 1. МАСШТАБНЫЙ СЛОВАРЬ TRAVEL (База слов)
# ==========================================
TRAVEL_WORDS = [
    # Аэропорт и самолет
    {"word": "Luggage / Baggage", "trans": "[ˈlʌɡɪdʒ]", "translation": "Багаж, чемодан"},
    {"word": "Boarding pass", "trans": "[ˈbɔːrdɪŋ pæs]", "translation": "Посадочный талон"},
    {"word": "Customs", "trans": "[ˈkʌstəmz]", "translation": "Таможня"},
    {"word": "Delay", "trans": "[dɪˈleɪ]", "translation": "Задержка рейса"},
    {"word": "Gate", "trans": "[ɡeɪt]", "translation": "Выход на посадку"},
    {"word": "Passport control", "trans": "[ˈpæspɔːrt kənˈtroʊl]", "translation": "Паспортный контроль"},
    {"word": "Security check", "trans": "[sɪˈkjʊrəti tʃek]", "translation": "Досмотр безопасности"},
    {"word": "Overweight baggage", "trans": "[ˌoʊvərweɪt ˈbæɡɪdʒ]", "translation": "Перевес багажа"},
    {"word": "Connecting flight", "trans": "[kəˈnektɪŋ flaɪt]", "translation": "Сстыковочный рейс"},
    {"word": "Direct flight", "trans": "[daɪˈrekt flaɪt]", "translation": "Прямой рейс"},
    
    # Отель и проживание
    {"word": "Reservation", "trans": "[ˌrezərˈveɪʃn]", "translation": "Бронирование"},
    {"word": "Air conditioning", "trans": "[ˈer kəndɪʃənɪŋ]", "translation": "Кондиционер"},
    {"word": "Reception / Front desk", "trans": "[rɪˈsepʃn]", "translation": "Ресепшн, стойка регистрации"},
    {"word": "Single / Double room", "trans": "[ˈsɪŋɡl / ˈdʌbl ruːm]", "translation": "Одноместный / двухместный номер"},
    {"word": "Check-in / Check-out", "trans": "[tʃek ɪn / tʃek aʊt]", "translation": "Заселение / выселение"},
    {"word": "Breakfast included", "trans": "[ˈbrekfəst ɪnˈkluːdɪd]", "translation": "Завтрак включен"},
    {"word": "Wi-Fi password", "trans": "[ˈwaɪfaɪ ˈpɑːswərd]", "translation": "Пароль от вай-фая"},
    {"word": "Elevator / Lift", "trans": "[ˈeləveɪtər / lɪft]", "translation": "Лифт"},
    {"word": "Key card", "trans": "[kiː kɑːrd]", "translation": "Карта-ключ от номера"},
    {"word": "Room service", "trans": "[ruːm ˈsɜːrvɪs]", "translation": "Обслуживание номеров"},

    # Город и транспорт
    {"word": "Subway / Underground", "trans": "[ˈsʌbweɪ]", "translation": "Метро"},
    {"word": "Railway station", "trans": "[ˈreɪlweɪ ˈsteɪʃn]", "translation": "Железнодорожный вокзал"},
    {"word": "Ticket machine", "trans": "[ˈtɪkɪt məˈʃiːn]", "translation": "Билетный автомат"},
    {"word": "Single ticket", "trans": "[ˈsɪŋɡl ˈtɪkɪt]", "translation": "Билет в один конец"},
    {"word": "Return ticket", "trans": "[rɪˈtɜːrn ˈtɪkɪt]", "translation": "Билет туда и обратно"},
    {"word": "Bus stop", "trans": "[bʌs stɑːp]", "translation": "Автобусная остановка"},
    {"word": "Map", "trans": "[mæp]", "translation": "Карта"},
    {"word": "Directions", "trans": "[dəˈrekʃnz]", "translation": "Направления / маршрут"},
    {"word": "Car rental", "trans": "[kɑːr ˈrentl]", "translation": "Аренда автомобилей"},
    {"word": "Gas station", "trans": "[ɡæs ˈsteɪʃn]", "translation": "Заправка"},

    # Ресторан и еда
    {"word": "Menu", "trans": "[ˈmenjuː]", "translation": "Меню"},
    {"word": "Check / Bill", "trans": "[tʃek / bɪl]", "translation": "Счет"},
    {"word": "Waiter / Waitress", "trans": "[ˈweɪtər / ˈweɪtrəs]", "translation": "Официант / официантка"},
    {"word": "Tip", "trans": "[tɪp]", "translation": "Чаевые"},
    {"word": "Pay by card", "trans": "[peɪ baɪ kɑːrd]", "translation": "Платить картой"},
    {"word": "Cash", "trans": "[kæʃ]", "translation": "Наличные"},
    {"word": "Starter", "trans": "[ˈstɑːrtər]", "translation": "Закуска"},
    {"word": "Main course", "trans": "[meɪn kɔːrs]", "translation": "Основное блюдо"},
    {"word": "Allergy", "trans": "[ˈælərdʒi]", "translation": "Аллергия"},
    {"word": "Tap water", "trans": "[tæp ˈwɔːtər]", "translation": "Вода из-под крана (бесплатная)"},

    # Экстренные ситуации
    {"word": "Emergency", "trans": "[ɪˈmɜːrdʒənsi]", "translation": "Чрезвычайная ситуация"},
    {"word": "Police station", "trans": "[pəˈliːs ˈsteɪʃn]", "translation": "Полицейский участок"},
    {"word": "Pharmacy", "trans": "[ˈfɑːrməsi]", "translation": "Аптека"},
    {"word": "Hospital", "trans": "[ˈhɑːspɪtl]", "translation": "Больница"},
    {"word": "Stolen", "trans": "[ˈstoʊlən]", "translation": "Украденный"},
    {"word": "Help", "trans": "[help]", "translation": "Помощь"},
    {"word": "Lost", "trans": "[lɔːst]", "translation": "Потерянный / заблудившийся"}
]

# ==========================================
# 2. БОЛЬШАЯ БАЗА ПОЛЕЗНЫХ ФРАЗ
# ==========================================
TRAVEL_PHRASES = [
    # Ориентация
    {"phrase": "Could you help me, please?", "translation": "Не могли бы вы мне помочь, пожалуйста?"},
    {"phrase": "Where is the nearest railway station?", "translation": "Где находится ближайший вокзал?"},
    {"phrase": "How do I get to the city center?", "translation": "Как мне добраться до центра города?"},
    {"phrase": "Is it far on foot?", "translation": "Это далеко пешком?"},
    {"phrase": "Could you show it on the map?", "translation": "Не могли бы вы показать это на карте?"},
    
    # Покупки и деньги
    {"phrase": "How much does this cost?", "translation": "Сколько это стоит?"},
    {"phrase": "Can I pay by card?", "translation": "Могу ли я оплатить картой?"},
    {"phrase": "Do you accept cash?", "translation": "Вы принимаете наличные?"},
    {"phrase": "Can I get a discount?", "translation": "Могу ли я получить скидку?"},
    {"phrase": "I'm just looking, thank you.", "translation": "Я просто смотрю, спасибо."},

    # Отель
    {"phrase": "I would like to book a room.", "translation": "Я бы хотел забронировать номер."},
    {"phrase": "Is breakfast included in the price?", "translation": "Включен ли завтрак в стоимость?"},
    {"phrase": "The air conditioning isn't working.", "translation": "Кондиционер не работает."},
    {"phrase": "Can I have another room, please?", "translation": "Могу ли я получить другой номер?"},
    {"phrase": "What time is check-out?", "translation": "Во сколько выселение?"},

    # Ресторан
    {"phrase": "Could we have the menu, please?", "translation": "Можно нам меню, пожалуйста?"},
    {"phrase": "I am allergic to nuts.", "translation": "У меня аллергия на орехи."},
    {"phrase": "Could we have the bill, please?", "translation": "Можно нам счет, пожалуйста?"},
    {"phrase": "Can we split the bill?", "translation": "Можем ли мы разделить счет?"},
    {"phrase": "The food was delicious!", "translation": "Еда была восхитительной!"}
]

# ==============================================================================
# 3. ПОЛНОЦЕННЫЕ СЮЖЕТНЫЕ КВЕСТЫ (Интерактивные обучающие сценарии)
# ==============================================================================
TRAVEL_DIALOGUES = {
    "module_1": {
        "title": "✈️ Квест №1: Аэропорт и потерянный багаж",
        "story": (
            "🎬 **Сюжет:** Ты прилетел в лондонский аэропорт Хитроу. На часах полночь, "
            "пассажиры разошлись, а лента выдачи остановилась. Твоего чемодана нет. "
            "Тебе нужно найти стойку розыска багажа (Lost & Found) и объясниться с сотрудником."
        ),
        "phrases": [
            "🗣️ *«Excuse me, my luggage didn't arrive.»* — Извините, мой багаж не прилетел.",
            "🗣️ *«Here is my claim tag and boarding pass.»* — Вот моя багажная бирка и посадочный.",
            "🗣️ *«Where can I track it?»* — Где я могу отследить его?"
        ],
        "task_text": "🎮 **Сюжетный выбор:** Ты подходишь к стойке. Какую фразу лучше использовать первой?",
        "options": [
            {"text": "«Here is my claim tag. My luggage didn't arrive.»", "correct": True},
            {"text": "«Give me a new suitcase right now, this is unacceptable!»", "correct": False},
            {"text": "«I lost my bag somewhere in the clouds, find it fast.»", "correct": False}
        ],
        "tip": "💡 Вежливое обращение (*Excuse me*) и демонстрация бирки (*claim tag*) ускоряют решение проблемы в 10 раз."
    },
    "module_2": {
        "title": "🏨 Квест №2: Отель и сломанный кондиционер",
        "story": (
            "🎬 **Сюжет:** Ты заселился в отель в центре Барселоны. На улице +35°C, "
            "ты заходишь в номер, а кондиционер издает странный треск и дует горячим воздухом. "
            "В комнате духота. Нужно спуститься на ресепшн и потребовать помощи."
        ),
        "phrases": [
            "🗣️ *«The air conditioning in my room isn't working.»* — Кондиционер в моем номере не работает.",
            "🗣️ *«Can I get another room, please?»* — Могу ли я получить другой номер?",
            "🗣️ *«It's too hot in there.»* — Там слишком жарко."
        ],
        "task_text": "🎮 **Сюжетный выбор:** Администратор смотрит на тебя. Как грамотно описать проблему?",
        "options": [
            {"text": "«The AC in my room isn't working. Can I get another room?»", "correct": True},
            {"text": "«Your hotel is terrible, fix the weather outside immediately.»", "correct": False},
            {"text": "«I want cold air for free or I will sleep in the lobby.»", "correct": False}
        ],
        "tip": "💡 Конструкция *'isn't working'* идеально подходит для любых поломок техники в номерах."
    },
    "module_3": {
        "title": "🍽️ Квест №3: Ресторан и раздельный счет",
        "story": (
            "🎬 **Сюжет:** Ты поужинал с новыми знакомыми в итальянском ресторане в Риме. "
            "Еда была отличной, но теперь официант приносит общий бумажный чек. "
            "Вам нужно вежливо попросить разделить сумму на всех участников."
        ),
        "phrases": [
            "🗣️ *«Could we have the bill, please?»* — Можно нам счет, пожалуйста?",
            "🗣️ *«Can we split the bill equally?»* — Можем ли мы разделить счет поровну?",
            "🗣️ *«Can I pay by card separately?»* — Могу ли я оплатить картой отдельно?"
        ],
        "task_text": "🎮 **Сюжетный выбор:** Официант ждет ответа. Что сказать, чтобы разделить чек?",
        "options": [
            {"text": "«Can we split the bill, please?»", "correct": True},
            {"text": "«Take all my money and run away.»", "correct": False},
            {"text": "«I will pay for everyone forever, don't worry.»", "correct": False}
        ],
        "tip": "💡 Фраза *'split the bill'* универсальна для баров, кафе и ресторанов по всему миру."
    },
    "module_4": {
        "title": "🚨 Квест №4: ЧП и потеря документов",
        "story": (
            "🎬 **Сюжет:** Ты вышел из метро в незнакомом мегаполисе, зазевался, "
            "и у тебя из кармана вытащили кошелек, в котором лежали карты и паспорт. "
            "Срочно нужно обратиться к полицейскому на улице."
        ),
        "phrases": [
            "🗣️ *«Excuse me! My wallet has been stolen!»* — Извините! Мой кошелек украли!",
            "🗣️ *«Where is the nearest police station?»* — Где ближайший полицейский участок?",
            "🗣️ *«I need to block my bank cards.»* — Мне нужно заблокировать банковские карты."
        ],
        "task_text": "🎮 **Сюжетный выбор:** Ты подходишь к патрульному. С чего начать разговор?",
        "options": [
            {"text": "«Excuse me, my wallet was stolen, I need help.»", "correct": True},
            {"text": "«Do you want to play a hide and seek game with me?»", "correct": False},
            {"text": "«Everything is fine, I lost my money for fun.»", "correct": False}
        ],
        "tip": "💡 В экстренной ситуации всегда привлекай внимание вежливым *'Excuse me'* и сразу заявляй о краже (*stolen*)."
    }
}

def get_random_travel_dialogue():
    """Возвращает случайный сюжетный модуль путешествий."""
    key = random.choice(list(TRAVEL_DIALOGUES.keys()))
    return key, TRAVEL_DIALOGUES[key]
CHAT_SCENARIOS = {
    "start": {
        "character": "📱 Выберите контакт для переписки",
        "dialogue": "У вас три непрочитанных сообщения в мессенджере. Кому ответите первому?",
        "options": [
            {"text": "💻 Алекс (Тимлид): Срочный вопрос по дедлайну", "next": "alex_start", "correct": True},
            {"text": "🕶️ Неизвестный абонент: Зашифрованное сообщение", "next": "client_start", "correct": True},
            {"text": "🇬🇧 Сара (Коллега): Планы на вечер и паб", "next": "sarah_start", "correct": True}
        ]
    },
    "alex_start": {
        "character": "💻 Алекс (Тимлид)",
        "dialogue": (
            "Hey! The client is freaking out because the production server is down again. "
            "Can you fix this ASAP or are you gonna ghost us, no cap?"
        ),
        "options": [
            {"text": "😎 Chill, I got this under control, no cap.", "next": "alex_code_review", "correct": True},
            {"text": "🧢 Why are you talking about caps? My hat is fine.", "next": "fail_alex_1", "correct": False},
            {"text": "🏃‍♂️ I'm running away from the office right now.", "next": "fail_alex_2", "correct": False}
        ],
        "feedback": "🔥 Тимлид оценил хладнокровие и знание сленга."
    },
    "alex_code_review": {
        "character": "💻 Алекс (Тимлид)",
        "dialogue": (
            "Awesome. By the way, management is breathing down our necks about the new feature. "
            "How's the refactoring going?"
        ),
        "options": [
            {"text": "🔥 It's a piece of cake, almost done!", "next": "alex_crisis", "correct": True},
            {"text": "🫁 Tell them to stop breathing on my neck, that's creepy.", "next": "fail_alex_3", "correct": False}
        ],
        "feedback": "⚡ Отличный выбор идиомы!"
    },
    "alex_crisis": {
        "character": "💻 Алекс (Тимлид)",
        "dialogue": (
            "One last thing before deployment. The junior developer dropped the ball on database migration. "
            "Can you salvage it before the meeting?"
        ),
        "options": [
            {"text": "🎯 Leave it to me, I'll cut to the chase and fix the dump.", "next": "victory_alex", "correct": True},
            {"text": "⚽ I don't play football, why are we dropping balls?", "next": "fail_alex_4", "correct": False}
        ],
        "feedback": "👑 Все задачи решены идеально."
    },
    "client_start": {
        "character": "🕶️ Неизвестный абонент",
        "dialogue": (
            "I know what you did in London. Don't try to give me the slip, "
            "otherwise you'll be totally screwed."
        ),
        "options": [
            {"text": "🕵️‍♂️ You won't catch me, I'm already miles away.", "next": "client_meetup", "correct": True},
            {"text": "📄 Do you want me to sign a slip of paper?", "next": "fail_client_1", "correct": False}
        ],
        "feedback": "🕶️ Вы держите интригу в опасном диалоге."
    },
    "client_meetup": {
        "character": "🕶️ Неизвестный абонент",
        "dialogue": (
            "Meet me at the old docks in an hour. Come alone, and watch your back. "
            "The agency is monitoring all our chats."
        ),
        "options": [
            {"text": "👀 Got it, I'll watch my back and be extra careful.", "next": "victory_client", "correct": True},
            {"text": "🧘 I'm going to stretch my spine and look backwards.", "next": "fail_client_2", "correct": False}
        ],
        "feedback": "🧩 Безопасность на высшем уровне."
    },
    "sarah_start": {
        "character": "🇬🇧 Сара (Коллега)",
        "dialogue": (
            "Hey mate! Rough week at work? Let's grab a pint tonight. "
            "The first round is on the house, what do you say?"
        ),
        "options": [
            {"text": "🍺 Sounds amazing, count me in!", "next": "sarah_pub", "correct": True},
            {"text": "🏠 No thanks, I don't want to drink inside a house.", "next": "fail_sarah_1", "correct": False}
        ],
        "feedback": "🍻 Отличный выбор для пятничного вечера."
    },
    "sarah_pub": {
        "character": "🇬🇧 Сара (Коллега)",
        "dialogue": (
            "Brilliant! By the way, don't sweat about the presentation tomorrow. "
            "You're gonna ace it, no worries."
        ),
        "options": [
            {"text": "😎 Thanks Sarah, I feel much better now.", "next": "victory_sarah", "correct": True},
            {"text": "🥵 Why are you telling me to sweat? It's cold here.", "next": "fail_sarah_2", "correct": False}
        ],
        "feedback": "🎉 Дружеская поддержка получена."
    },
    "victory_alex": {
        "title": "🏆 ПОБЕДА: Успешный релиз",
        "text": "Ты блестяще разрулил рабочий кризис, поддержал сленговый диалог с тимлидом и заслужил уважение всей IT-команды!"
    },
    "victory_client": {
        "title": "🏆 ПОБЕДА: Контакты установлены",
        "text": "Ты перехитрил тайного агента, правильно расшифровал все угрозы и вышел победителем из опасной шпионской игры."
    },
    "victory_sarah": {
        "title": "🏆 ПОБЕДА: Отличный вечер",
        "text": "Ты расслабился в пабе, обсудил последние новости на живом английском и отлично провел время."
    },
    "fail_alex_1": {"title": "💀 Увольнение", "text": "Тимлид решил, что вы не понимаете контекст работы, и закрыл вам доступ к репозиторию."},
    "fail_alex_2": {"title": "💀 Побег", "text": "Вас уволили за прогул рабочего места прямо во время инцидента."},
    "fail_alex_3": {"title": "💀 Неловкость", "text": "Вашу шутку про шею сочли странной, проект передали другому спецу."},
    "fail_alex_4": {"title": "💀 Провал", "text": "Вы не справились с миграцией базы данных, проект сгорел."},
    "fail_client_1": {"title": "💀 Арест", "text": "Вы не поняли сленг погони и были задержаны спецслужбами."},
    "fail_client_2": {"title": "💀 Засада", "text": "Из-за потери бдительности вас поймали в темном переулке."},
    "fail_sarah_1": {"title": "💀 Одиночество", "text": "Сара решила, что вы зануда, и пошла в паб без вас."},
    "fail_sarah_2": {"title": "💀 Непонимание", "text": "Ваша реакция на совет расслабиться испугала коллегу."}
}

FAIL_SCENARIOS = {
    "button": "🔄 Вернуться к списку чатов"
}

VICTORY_SCENARIOS = {
    "button": "🔄 Выбрать другой чат"
}
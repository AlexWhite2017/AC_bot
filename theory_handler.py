import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
import logging

logger = logging.getLogger(__name__)

class TheoryHandler:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = self.load_data()
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading theory data: {e}")
            return {"sections": {}}
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню теории"""
        keyboard = [
            [InlineKeyboardButton("📚 Основы работы", callback_data='theory_basics')],
            [InlineKeyboardButton("⚙️ Выбор и установка", callback_data='theory_selection')],
            [InlineKeyboardButton("🔧 Обслуживание", callback_data='theory_maintenance')],
            [InlineKeyboardButton("🔙 Назад в меню", callback_data='main_menu')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "📖 *Теория кондиционеров*\n\n"
            "Выберите раздел для изучения:\n\n"
            "• *Основы работы* - принципы работы, типы систем\n"
            "• *Выбор и установка* - как подобрать и установить\n"
            "• *Обслуживание* - уход и эксплуатация"
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def show_section_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, section_key):
        """Показать меню раздела"""
        section = self.data["sections"].get(section_key, {})
        
        if not section:
            await update.callback_query.answer("Раздел не найден")
            return
        
        keyboard = []
        for content_key, content in section.get("content", {}).items():
            keyboard.append([
                InlineKeyboardButton(
                    f"• {content['title']}",
                    callback_data=f'theory_{section_key}_{content_key}'
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад к разделам", callback_data='theory_back')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text=f"*{section['title']}*\n\nВыберите тему:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE, section_key, content_key):
        """Показать содержание темы"""
        content = self.data["sections"][section_key]["content"][content_key]
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к разделу", callback_data=f'theory_{section_key}')],
            [InlineKeyboardButton("📚 Все разделы", callback_data='theory_back')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"*{content['title']}*\n\n{content['text']}"
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback-запросов"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == 'theory_back':
            await self.show_main_menu(update, context)
        
        elif data in ['theory_basics', 'theory_selection', 'theory_maintenance']:
            section_key = data.replace('theory_', '')
            await self.show_section_menu(update, context, section_key)
        
        elif data.startswith('theory_') and '_' in data:
            parts = data.split('_')
            if len(parts) == 3:
                await self.show_content(update, context, parts[1], parts[2])

import json
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
import logging
from database import db

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AREA_INPUT, = range(1)

class CalculatorHandler:
    def __init__(self, data_path, btu_per_m2=340):
        self.data_path = data_path
        self.btu_per_m2 = btu_per_m2
        self.models_data = self.load_data()
    
    def load_data(self):
        """Загрузка данных моделей"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading models data: {e}")
            return {"models": []}
    
    async def start_calculation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс подбора"""
        text = (
            "🔢 *Подбор кондиционера по площади*\n\n"
            "Введите площадь помещения в квадратных метрах (например: 25)\n\n"
            "📝 *Примечание:* Учитывайте:\n"
            "• Высоту потолков (стандарт - 2.5-3 м)\n"
            "• Количество окон и их ориентацию\n"
            "• Наличие тепловыделяющей техники\n\n"
            "Для отмены введите /cancel"
        )
        
        await update.message.reply_text(text, parse_mode='Markdown')
        return AREA_INPUT
    
    async def calculate_ac(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Расчет и подбор кондиционера"""
        try:
            # Получаем и проверяем площадь
            user_input = update.message.text.replace(',', '.')
            area = float(user_input)
            
            if area <= 0 or area > 500:
                await update.message.reply_text(
                    "❌ Пожалуйста, введите реальную площадь помещения (от 1 до 500 м²)"
                )
                return AREA_INPUT
            
            # Рассчитываем требуемую мощность
            required_btu = int(math.ceil(area * self.btu_per_m2 / 1000) * 1000)
            
            # Находим подходящие модели
            suitable_models = []
            for model in self.models_data.get("models", []):
                if model["area_min_m2"] <= area <= model["area_max_m2"]:
                    suitable_models.append(model)
            
            # Сортируем по цене и мощности
            suitable_models.sort(key=lambda x: (
                {"бюджетный": 0, "средний": 1, "премиум": 2}[x["price_range"]],
                abs(x["btu"] - required_btu)
            ))
            
            # Логируем запрос
            user_id = update.effective_user.id
            db.log_calculation(user_id, area, required_btu, len(suitable_models))
            
            # Формируем ответ
            response = self._format_response(area, required_btu, suitable_models)
            
            # Добавляем кнопку для нового расчета
            keyboard = [[InlineKeyboardButton("🔄 Новый расчет", callback_data='new_calculation')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return ConversationHandler.END
            
        except ValueError:
            await update.message.reply_text(
                "❌ Пожалуйста, введите число (например: 25 или 25.5)"
            )
            return AREA_INPUT
    
    def _format_response(self, area, required_btu, models):
        """Форматирование ответа"""
        response = (
            f"📐 *Результаты подбора для {area} м²*\n\n"
            f"✅ Рекомендуемая мощность: *{required_btu} BTU*\n"
            f"   (≈{required_btu / 3.517:.1f} кВт охлаждения)\n\n"
        )
        
        if not models:
            response += "❌ *Подходящих моделей не найдено*\n\n"
            response += "Попробуйте:\n• Увеличить/уменьшить площадь\n• Обратиться к консультанту"
        else:
            response += f"✅ Найдено *{len(models)}* подходящих моделей:\n\n"
            
            for i, model in enumerate(models[:5], 1):  # Показываем максимум 5 моделей
                response += (
                    f"*{i}. {model['brand']} {model['model']}*\n"
                    f"   • Мощность: {model['btu']} BTU ({model['cooling_power_kw']} кВт)\n"
                    f"   • Площадь: {model['area_min_m2']}-{model['area_max_m2']} м²\n"
                    f"   • Тип: {model['type']}\n"
                    f"   • Инвертор: {'✅' if model['inverter'] else '❌'}\n"
                    f"   • Wi-Fi: {'✅' if model['wifi'] else '❌'}\n"
                    f"   • Класс энергии: {model['energy_class']}\n"
                    f"   • Ценовой диапазон: {model['price_range']}\n\n"
                )
            
            if len(models) > 5:
                response += f"... и еще {len(models) - 5} моделей\n\n"
            
            response += (
                "📝 *Рекомендации:*\n"
                "• Для спальни выбирайте тихие модели (<25 дБ)\n"
                "• Для часто меняющихся условий - инверторные\n"
                "• Для умного дома - модели с Wi-Fi\n"
            )
        
        return response
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена подбора"""
        await update.message.reply_text("❌ Подбор отменен")
        return ConversationHandler.END
    
    async def handle_new_calculation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса на новый расчет"""
        query = update.callback_query
        await query.answer()
        
        text = (
            "🔄 *Новый расчет*\n\n"
            "Введите площадь помещения в квадратных метрах (например: 25)"
        )
        
        await query.edit_message_text(text, parse_mode='Markdown')
        context.user_data.clear()
        
        return AREA_INPUT
    
    def get_conversation_handler(self):
        """Получить ConversationHandler для этого модуля"""
        return ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex('^🔍 Подобрать кондиционер$'), self.start_calculation)
            ],
            states={
                AREA_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.calculate_ac)
                ]
            },
            fallbacks=[MessageHandler(filters.Regex('^/cancel$'), self.cancel)],
            allow_reentry=True
        )

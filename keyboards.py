from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_btn_1 = InlineKeyboardButton('💪 Push Ups', callback_data='btn1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

inline_kb_full = InlineKeyboardMarkup(row_width=1).add(inline_btn_1)
inline_kb_full.add(InlineKeyboardButton('ℹ️ About as', url='https://www.instagram.com/nikstor_/'))


btn_start = InlineKeyboardButton('Start', callback_data='btn2')
btn_start = InlineKeyboardMarkup().add(btn_start)


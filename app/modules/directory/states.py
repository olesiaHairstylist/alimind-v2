# app/modules/directory/states.py
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class PartnerAddStates(StatesGroup):
    waiting_title = State()
    waiting_category = State()
    waiting_subcategory = State()
    waiting_description_short = State()
    waiting_description_full = State()
    waiting_location = State()
    waiting_contact = State()
    waiting_confirm = State()
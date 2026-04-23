from aiogram.fsm.state import State, StatesGroup


class PartnerCheckStates(StatesGroup):
    waiting_partner_id = State()


class PartnerDisableStates(StatesGroup):
    waiting_partner_id = State()
    waiting_confirm_disable = State()


class PartnerUpdateStates(StatesGroup):
    waiting_partner_id = State()
    waiting_field_choice = State()
    waiting_new_value = State()
    waiting_confirm_update = State()
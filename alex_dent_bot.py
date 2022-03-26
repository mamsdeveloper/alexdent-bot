import smtplib
from functools import partial

from telebot import types

import config
from pagesbot import PagesBot


class AlexDentBot(PagesBot):
	def get_reply_addons(self) -> "tuple[str, list[types.KeyboardButton]]":
		add_text = '📞 Заказать обратный звонок\n\n'
		add_text += '🌹 Записаться на прием'

		add_btns = [
			types.KeyboardButton('📞 Заказать обратный звонок'),
			types.KeyboardButton('🌹 Записаться на прием'),
		]

		return add_text, add_btns

	def addons_handler(self, message: types.Message):
		text = message.text

		if text == '📞 Заказать обратный звонок':
			markup = types.ReplyKeyboardMarkup(
				resize_keyboard=True, one_time_keyboard=True)
			markup.add(types.KeyboardButton(
				'Поделиться контактом', request_contact=True))
			self.send_message(
				message.chat.id,
				'📞 Укажите, пожалуйста, номер телефона',
				reply_markup=markup
			)
			self.register_next_step_handler(message, self.order_call)

		elif text == '🌹 Записаться на прием':
			markup = types.ReplyKeyboardMarkup(
				resize_keyboard=True, one_time_keyboard=True)
			markup.add(types.KeyboardButton(
				'Поделиться контактом', request_contact=True))
			self.send_message(
				message.chat.id,
				'📞 Укажите, пожалуйста, номер телефона',
				reply_markup=markup
			)
			self.register_next_step_handler(message, self.order_appointment_phone)

		else:
			self.send_message(
				message.chat.id,
				'Нет такой команды или страницы'
			)

	def order_call(self, message: types.Message):
		if message.contact is not None:
			phone = message.contact.phone_number
		else:
			phone = message.text

		mail_text = f'Запрос обратного вызова\nКлиент: {message.chat.first_name} {message.chat.last_name}\nНомер: {phone}'
		self.send_email(mail_text)
		self.send_message(
			message.chat.id,
			'Спасибо за обращение, скоро с вами свяжутся менеджеры',
		)
		self.go_root_page(message)

	def order_appointment_phone(self, message: types.Message):
		if message.contact is not None:
			phone = message.contact.phone_number
		else:
			phone = message.text

		self.send_message(
			message.chat.id,
			'👨 Укажите, пожалуйста, ваше ФИО'
		)
		self.register_next_step_handler(
			message, partial(self.order_appointment_name, [phone]))

	def order_appointment_name(self, data: "list[str]", message: types.Message):
		data += [message.text]
		self.send_message(
			message.chat.id,
			'🕑 Напишите желаемое время и дату приема'
		)
		self.register_next_step_handler(
			message, partial(self.order_appointment_date, data))

	def order_appointment_date(self, data: "list[str]", message: types.Message):
		data += [message.text]
	
		doctors = [
			'Не важно, какой врач',
			'Татитянц Артур Валерьевич',
			'Коротыш Игорь Валентинович',
			'Тарасова Татьяна Витальевна',
			'Исмаилов Рустам Евгеньевич',
			'Бадалян Шираз Кронвельович',
			'Дилбарян Назели Оганесовна',
			'Голубкова Олеся Валерьевна'
			]

		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.add(*[types.KeyboardButton(d) for d in doctors])

		self.send_message(
			message.chat.id,
			'Выберите врача',
			reply_markup=markup
		)
		self.register_next_step_handler(message, partial(self.order_appointment_last, data))

	def order_appointment_last(self, data: "list[str]", message: types.Message):
		data += [message.text]
		phone, name, date, doctor = data

		mail_text = f'Запись на прием\nКлиент: {name}\nНомер: {phone}\nДата: {date}\nВрач: {doctor}'
		self.send_email(mail_text)
		self.send_message(
			message.chat.id,
			'Спасибо за обращение.\n Ожидайте звонка от нашего специалиста',
		)
		self.go_root_page(message)

	def send_email(self, text: str):
		domain = config.FROM_EMAIL.split('@')[1]
		server = smtplib.SMTP(
			'smtp.' + domain,
			587 if domain == 'gmail.com' else 465
		)
		server.starttls()
		server.login(config.FROM_EMAIL, config.FROM_EMAIL_PSW)
		server.sendmail(config.FROM_EMAIL, config.TO_EMAIL, text.encode('utf-8'))
		server.quit()


if __name__ == '__main__':
	bot = AlexDentBot('./pages', 'Меню', config.TOKEN)
	bot.polling(non_stop=True)

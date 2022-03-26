import itertools
import os
import json

import telebot
from telebot import types


class PagesBot(telebot.TeleBot):
	def __init__(self, pages_path: str, first_page: str, *args, **kwargs) -> None:
		"""Initialize TeleBot, parse pages folder

		Args:
			pages_path (str): folder with pages.json and pages content
			first_page (str): name of first displayed page
		"""

		super().__init__(*args, **kwargs)
		self.first_page = first_page
		with open(os.path.join(pages_path, 'pages.json'), 'rb') as f:
			self.pages = json.load(f)

		self.pages_contents = {}
		self.pages_imgs = {}
		for file in os.listdir(pages_path):
			filename, ext = os.path.splitext(file)
			if ext == '.txt':
				with open(os.path.join(pages_path, file), 'r', encoding='utf-8') as f:
					self.pages_contents[filename] = f.read()
			elif ext in ('.png', '.jpg', '.jpeg', '.webm'):
				with open(os.path.join(pages_path, file), 'rb') as f:
					self.pages_imgs[filename] = f.read()

		self.register_message_handler(
			self.handler,
			content_types=['text', 'emoji']
		)

	def display_page(self, message: types.Message, pages: str):
		"""Send message with content of last page in pages

		Args:
			message (str): reply message
			pages (str): current page path in pages.json in formar "page0.page1..."
		"""

		pages_names = pages.split('.')
		curr_page_name = pages_names[-1]
		next_pages = self.get_available_pages(message)

		text = self.pages_contents[curr_page_name]

		if next_pages:
			text += '\n' + '-' * 10 + '\n'

		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		btns = []
		for page_name in next_pages:
			btns += [types.KeyboardButton(page_name)]
			text += f'· {page_name}\n'

		text += '\n' + '-' * 10 + '\n'
		text += '· 🏠\n\n· 🔙'
		btns += [types.KeyboardButton('🏠'), types.KeyboardButton('🔙')]

		add_text, add_btns = self.get_reply_addons()
		if add_text:
			text += '\n' + '-' * 10 + '\n'
			text += add_text
		
		text = text.format(**locals())

		btns += add_btns
		markup.add(*btns)
		
		self.send_message(message.chat.id, text, reply_markup=markup)
		if curr_page_name in self.pages_imgs:
			self.send_photo(message.chat.id, self.pages_imgs[curr_page_name])

	def get_reply_addons(self) -> tuple[str, list[types.KeyboardButton]]:
		"""User extension for page displaying

		Returns:
			tuple[str, list[types.KeyboardButton]]: added text and buttons
		"""

		return '', []

	def go_next_page(self, message: types.Message, page: str):
		"""Go to child page from current page

		Args:
			message (str): reply message
			page (str): name of target page
		"""

		pages = self.get_user_pages(message.chat.username)
		pages += f'.{page}'
		self.set_user_pages(message.chat.username, pages)

		self.display_page(message, pages)

	def go_previous_page(self, message: types.Message):
		"""Go to page where user located before

		Args:
			message (str): reply message
		"""

		pages = self.get_user_pages(message.chat.username)
		if len(pages.split('.')) > 1:
			pages = '.'.join(pages.split('.')[:-1])
		self.set_user_pages(message.chat.username, pages)

		self.display_page(message, pages)

	def go_root_page(self, message: types.Message):
		"""Go to first page

		Args:
			message (str): reply message
		"""

		pages = self.get_user_pages(message.chat.username)
		pages = pages.split('.')[0]
		self.set_user_pages(message.chat.username, pages)

		self.display_page(message, pages)

	def get_available_pages(self, message: types.Message) -> list[str]:
		"""Return names of availabels next pages

		Args:
			message (types.Message): reply message

		Returns:
			list[str]: pages names
		"""
		pages = self.get_user_pages(message.chat.username)
		curr_page = self.pages
		pages_names = pages.split('.')
		for page_name in pages_names:
			curr_page = curr_page[page_name]
		next_pages = curr_page.keys()

		return next_pages

	def get_user_pages(self, username: str) -> str:
		"""Get pages where user located from users.json

		Args:
			username (str): chat username

		Returns:
			str: current page path in pages.json in formar "page0.page1..."
		"""

		with open('users.json', 'r') as f:
			try:
				users = json.load(f)
			except json.JSONDecodeError:
				users = {}

		return users.get(username)

	def set_user_pages(self, username: str, page: str):
		"""Set current pages to users.json

		Args:
			username (str): chat username
			page (str): page path in pages.json in formar "page0.page1..."
		"""

		with open('users.json', 'r') as f:
			try:
				users = json.load(f)
			except json.JSONDecodeError:
				users = {}

		users[username] = page

		with open('users.json', 'w') as f:
			json.dump(users, f)

	def addons_handler(self, message: types.Message):
		"""Handler for extensional functionality

		Args:
			message (types.Message): reply message
		"""

		self.send_message(message.chat.id, 'Not such command')

	def handler(self, message: types.Message):
		"""Main message handler 

		Args:
			message (types.Message): _description_
		"""
		text = message.text
		if text == '/start':
			self.set_user_pages(message.chat.username, self.first_page)
		available_pages = self.get_available_pages(message)

		if text == '/start':
			self.display_page(message, self.first_page)
		elif text in available_pages:
			self.go_next_page(message, text)
		elif text == '🔙':
			self.go_previous_page(message)
		elif text == '🏠':
			self.go_root_page(message)
		else:
			self.addons_handler(message)


if __name__ == '__main__':
	import config

	bot = PagesBot('pages', 'Меню', config.TOKEN)
	bot.polling(non_stop=True)

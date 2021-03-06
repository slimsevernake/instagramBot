from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from data import users_settings_dict, direct_users_list
import time
import random
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import requests
import os


class InstagramBot():
	"""Instagram Bot на Python by PythonToday"""

	def __init__(self, username, password):

		self.username = username
		self.password = password
		options = Options()
		# options.add_argument(f"--window-size={window_size}")
		#options.add_argument("--headless")
		self.browser = webdriver.Chrome("../chromedriver/chromedriver", options=options)

	# метод для закрытия браузера
	def close_browser(self):

		self.browser.close()
		self.browser.quit()

	# метод логина
	def login(self):

		browser = self.browser
		browser.get('https://www.instagram.com')
		time.sleep(random.randrange(3, 5))

		username_input = browser.find_element_by_name('username')
		username_input.clear()
		username_input.send_keys(username)

		time.sleep(2)

		password_input = browser.find_element_by_name('password')
		password_input.clear()
		password_input.send_keys(password)

		password_input.send_keys(Keys.ENTER)
		time.sleep(10)

	# метод ставит лайки по hashtag
	def like_photo_by_hashtag(self, hashtag):

		browser = self.browser
		browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
		time.sleep(5)

		for i in range(1, 4):
			browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(random.randrange(3, 5))

		hrefs = browser.find_elements_by_tag_name('a')
		posts_urls = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

		for url in posts_urls:
			try:
				browser.get(url)
				time.sleep(3)
				like_button = browser.find_element_by_xpath(
					'/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button').click()
				time.sleep(random.randrange(80, 100))
			except Exception as ex:
				print(ex)
				self.close_browser()

	# метод проверяет по xpath существует ли элемент на странице
	def xpath_exists(self, url):

		browser = self.browser
		try:
			browser.find_element_by_xpath(url)
			exist = True
		except NoSuchElementException:
			exist = False
		return exist

	# метод ставит лайк на пост по прямой ссылке
	def put_exactly_like(self, userpost):

		browser = self.browser
		browser.get(userpost)
		time.sleep(4)

		wrong_userpage = "/html/body/div[1]/section/main/div/h2"
		if self.xpath_exists(wrong_userpage):
			print("Такого поста не существует, проверьте URL")
			self.close_browser()
		else:
			print("Пост успешно найден, ставим лайк!")
			time.sleep(2)

			like_button = "/html/body/div[1]/section/main/div/div/article/div[3]/section[1]/span[1]/button"
			browser.find_element_by_xpath(like_button).click()
			time.sleep(2)

			print(f"Лайк на пост: {userpost} поставлен!")
			self.close_browser()

	# метод собирает ссылки на все посты пользователя
	def get_all_posts_urls(self, userpage):

		browser = self.browser
		browser.get(userpage)
		time.sleep(4)

		wrong_userpage = "/html/body/div[1]/section/main/div/h2"
		if self.xpath_exists(wrong_userpage):
			print("Такого пользователя не существует, проверьте URL")
			self.close_browser()
		else:
			print("Пользователь успешно найден, ставим лайки!")
			time.sleep(2)

			posts_count = int(browser.find_element_by_xpath(
				"/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span").text)
			loops_count = int(posts_count / 12)
			print(loops_count)

			posts_urls = []
			for i in range(0, loops_count):
				hrefs = browser.find_elements_by_tag_name('a')
				hrefs = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

				for href in hrefs:
					posts_urls.append(href)

				browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(random.randrange(2, 4))
				print(f"Итерация #{i}")

			file_name = userpage.split("/")[-2]

			with open(f'{file_name}.txt', 'a') as file:
				for post_url in posts_urls:
					file.write(post_url + "\n")

			set_posts_urls = set(posts_urls)
			set_posts_urls = list(set_posts_urls)

			with open(f'{file_name}_set.txt', 'a') as file:
				for post_url in set_posts_urls:
					file.write(post_url + '\n')

	# метод ставит лайки по ссылке на аккаунт пользователя
	def put_many_likes(self, userpage):

		browser = self.browser
		self.get_all_posts_urls(userpage)
		file_name = userpage.split("/")[-2]
		time.sleep(4)
		browser.get(userpage)
		time.sleep(4)

		with open(f'{file_name}_set.txt') as file:
			urls_list = file.readlines()

			for post_url in urls_list[0:6]:
				try:
					browser.get(post_url)
					time.sleep(2)

					like_button = "/html/body/div[1]/section/main/div/div/article/div[3]/section[1]/span[1]/button"
					browser.find_element_by_xpath(like_button).click()
					# time.sleep(random.randrange(80, 100))
					time.sleep(2)

					print(f"Лайк на пост: {post_url} успешно поставлен!")
				except Exception as ex:
					print(ex)
					self.close_browser()

		self.close_browser()

	# метод скачивает контент со страницы пользователя  ?????????????????
	def download_userpage_content(self, userpage):

		browser = self.browser
		self.get_all_posts_urls(userpage)
		file_name = userpage.split("/")[-2]
		time.sleep(4)
		browser.get(userpage)
		time.sleep(4)

		# создаём папку с именем пользователя для чистоты проекта
		if os.path.exists(f"{file_name}"):
			print("Папка уже существует!")
		else:
			os.mkdir(file_name)

		img_and_video_src_urls = []
		with open(f'{file_name}_set.txt') as file:
			urls_list = file.readlines()

			for post_url in urls_list:
				try:
					browser.get(post_url)
					time.sleep(4)

					img_src = "/html/body/div[1]/section/main/div/div[1]/article/div[2]/div/div/div[1]/img"
					video_src = "/html/body/div[1]/section/main/div/div[1]/article/div[2]/div/div/div[1]/div/div/video"
					post_id = post_url.split("/")[-2]

					if self.xpath_exists(img_src):
						img_src_url = browser.find_element_by_xpath(img_src).get_attribute("src")
						img_and_video_src_urls.append(img_src_url)

						# сохраняем изображение
						get_img = requests.get(img_src_url)
						with open(f"{file_name}/{file_name}_{post_id}_img.jpg", "wb") as img_file:
							img_file.write(get_img.content)

					elif self.xpath_exists(video_src):
						video_src_url = browser.find_element_by_xpath(video_src).get_attribute("src")
						img_and_video_src_urls.append(video_src_url)

						# сохраняем видео
						get_video = requests.get(video_src_url, stream=True)
						with open(f"{file_name}/{file_name}_{post_id}_video.mp4", "wb") as video_file:
							for chunk in get_video.iter_content(chunk_size=1024 * 1024):
								if chunk:
									video_file.write(chunk)
					else:
						# print("Упс! Что-то пошло не так!")
						img_and_video_src_urls.append(f"{post_url}, нет ссылки!")
					print(f"Контент из поста {post_url} успешно скачан!")

				except Exception as ex:
					print(ex)
					self.close_browser()

			self.close_browser()

		with open(f'{file_name}/{file_name}_img_and_video_src_urls.txt', 'a') as file:
			for i in img_and_video_src_urls:
				file.write(i + "\n")

	# метод подписки на всех подписчиков переданного аккаунта  ----- исправил
	def get_all_followers(self, userpage):# передаем усера

		browser = self.browser
		browser.get(userpage)
		print(userpage)
		time.sleep(4)
		file_name = userpage.split("/")[-2]

		# создаём папку с именем пользователя для чистоты проекта
		if os.path.exists(f"{file_name}"):
			print(f"Папка {file_name} уже существует!")
		else:
			print(f"Создаём папку пользователя {file_name}.")
			os.mkdir(file_name)

		wrong_userpage = "/html/body/div[1]/section/main/div/h2"
		if self.xpath_exists(wrong_userpage):# ищет путь xpath возврашает тру фолс
			print(f"Пользователя {file_name} не существует, проверьте URL")
			self.close_browser()
		else:
			print(f"Пользователь {file_name} успешно найден, начинаем скачивать ссылки на подписчиков!")
			time.sleep(2)
			# ищем тэги li / a
			followers_button = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span")
			followers_count = followers_button.get_attribute('title')
			# followers_count = followers_button.text
			# followers_count = int(followers_count.split(' ')[0])

			# если количество подписчиков больше 999, убираем из числа запятые
			if ',' in followers_count:
				followers_count = int(''.join(followers_count.split(',')))# магия склейки
			else:
				followers_count = int(followers_count)

			print(f"Количество подписчиков: {followers_count}")
			time.sleep(2)

			loops_count = int(followers_count / 12)
			print(f"Число итераций: {loops_count}")
			time.sleep(4)

			followers_button.click()# кликаем на подписчиков
			time.sleep(4)
	#/html/body/div[5]/div/div/div[2]/ul/div/li[1]
			followers_ul = browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]")

			try:
				followers_urls = []# список для ссылок подписчиков
				for i in range(1, loops_count + 1):
					browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
					time.sleep(random.randrange(2, 4))
					print(f"Итерация #{i}")

				all_urls_div = followers_ul.find_elements_by_tag_name("li")

				for url in all_urls_div:
					url = url.find_element_by_tag_name("a").get_attribute("href")
					followers_urls.append(url)# список для ссылок подписчиков

				# сохраняем всех подписчиков пользователя в файл папка/фаил
				with open(f"{file_name}/{file_name}.txt", "a") as text_file:
					for link in followers_urls:
						text_file.write(link + "\n")

				with open(f"{file_name}/{file_name}.txt") as text_file:
					users_urls = text_file.readlines()

					for user in users_urls[0:10]:
						try:
							try:# проверка файла есть ли там подписчик
								with open(f'{file_name}/{file_name}_subscribe_list.txt',
										  'r') as subscribe_list_file:
									lines = subscribe_list_file.readlines()
									if user in lines:# смотрит в файле что подписаны
										print(f'Мы уже подписаны на {user}, переходим к следующему пользователю!')
										continue

							except Exception as ex:
								print('Файл со ссылками ещё не создан!')
								# print(ex)

							browser = self.browser
							browser.get(user)
							print('user  ',user)
							page_owner = user.split("/")[-2]
							# проверка кнопки edit
							if self.xpath_exists("/html/body/div[1]/section/main/div/header/section/div[1]/div/a"):

								print("Это наш профиль, уже подписан, пропускаем итерацию!")
							elif self.xpath_exists(
									"//button[@class='_5f5mN    -fzfL     _6VtSN     yZn4P   ']"):
							#		"/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/div/span/span[1]/button/div/span"):
								print(f"Уже подписаны, на {page_owner} пропускаем итерацию!")
							else:
								time.sleep(random.randrange(4, 8))

								if self.xpath_exists(  # xpath  = надпись аккаунт приватный
										"/html/body/div[1]/section/main/div/div/article/div[1]/div/h2"):
							
									try:
										
										follow_button = browser.find_element_by_xpath(
											#"//button[@class='sqdOP  L3NKy _4pI4F  y3zKF     ']").click()
											"//div[@class='                     Igw0E     IwRSH      eGOV_        vwCYk                                                                                                               ']").click()
											#"/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button").click()
										print(f'Запросили подписку на пользователя {page_owner}. Закрытый аккаунт!')
									except Exception as ex:
										print(ex)
								else:
									try:
										#print('xpath buton2')
										if self.xpath_exists("//button[@class='_5f5mN       jIbKX  _6VtSN     yZn4P   ']"):
										#if self.xpath_exists("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button"):
											follow_button = browser.find_element_by_xpath("//button[@class='_5f5mN       jIbKX  _6VtSN     yZn4P   ']").click()
											#follow_button = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button").click()
											print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
										else:
											print('xpath buton3')
											#follow_button = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/span/span[1]/button").click()
											#                                              //button[@class='_5f5mN       jIbKX  _6VtSN     yZn4P   ']
											follow_button = browser.find_element_by_xpath("//button[@class='_5f5mN       jIbKX  _6VtSN     yZn4P   ']")
											print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
									except Exception as ex:
										print(ex)

								# записываем данные в файл для ссылок всех подписок, если файла нет, создаём, если есть - дополняем
								with open(f'{file_name}/{file_name}_subscribe_list.txt',
										  'a') as subscribe_list_file:
									subscribe_list_file.write(user)

								time.sleep(random.randrange(7, 15))

						except Exception as ex:
							print(ex)
							self.close_browser()

			except Exception as ex:
				print(ex)
				self.close_browser()

		self.close_browser()

	# метод для отправки сообщений в директ
	def send_direct_message(self, usernames="", message="", img_path=''):

		browser = self.browser
		time.sleep(random.randrange(2, 4))

		direct_message_button = "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/a"

		if not self.xpath_exists(direct_message_button):
			print("Кнопка отправки сообщений не найдена!")
			self.close_browser()
		else:
			print("Отправляем сообщение...")
			direct_message = browser.find_element_by_xpath(direct_message_button).click()
			time.sleep(random.randrange(2, 4))

		# отключаем всплывающее окно
		if self.xpath_exists("/html/body/div[4]/div/div"):
			browser.find_element_by_xpath("/html/body/div[4]/div/div/div/div[3]/button[2]").click()
		time.sleep(random.randrange(2, 4))

		send_message_button = browser.find_element_by_xpath(
			"/html/body/div[1]/section/div/div[2]/div/div/div[2]/div/button").click()
		time.sleep(random.randrange(2, 4))

		# отправка сообщения нескольким пользователям
		for user in usernames:
			# вводим получателя
			to_input = browser.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/div[1]/div/div[2]/input")
			to_input.send_keys(user)
			time.sleep(random.randrange(2, 4))

			# выбираем получателя из списка
			users_list = browser.find_element_by_xpath(
				"/html/body/div[4]/div/div/div[2]/div[2]").find_element_by_tag_name("button").click()
			time.sleep(random.randrange(2, 4))

		next_button = browser.find_element_by_xpath(
			"/html/body/div[4]/div/div/div[1]/div/div[2]/div/button").click()
		time.sleep(random.randrange(2, 4))

		# отправка текстового сообщения
		if message:
			text_message_area = browser.find_element_by_xpath(
				"/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea")
			text_message_area.clear()
			text_message_area.send_keys(message)
			time.sleep(random.randrange(2, 4))
			text_message_area.send_keys(Keys.ENTER)
			print(f"Сообщение для {usernames} успешно отправлено!")
			time.sleep(random.randrange(2, 4))

		# отправка изображения
		if img_path:
			send_img_input = browser.find_element_by_xpath("/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/form/input")
			send_img_input.send_keys(img_path)
			print(f"Изображение для {usernames} успешно отправлено!")
			time.sleep(random.randrange(2, 4))

		self.close_browser()


for user, user_data in users_settings_dict.items():
	username = user_data['login']
	password = user_data['password']
	window_size = user_data['window_size']
	userpage = direct_users_list[0]
	my_bot = InstagramBot(username, password)
	my_bot.login()
	# my_bot.close_browser()
	# my_bot.send_direct_message(direct_users_list, "Hey! How's it going?", "/home/cain/PycharmProjects/instagram_bot/lesson_6/img1.jpg")
	#my_bot.get_all_followers(userpage)
	my_bot.download_userpage_content("https://www.instagram.com/aleksandr_khabidulin/")
	time.sleep(random.randrange(4, 8))
#get_all_posts_urls
# my_bot = InstagramBot(username, password)
# my_bot.login()
# my_bot.send_direct_message(direct_users_list, "Hey! How's it going?", "/home/cain/PycharmProjects/instagram_bot/lesson_6/img1.jpg")
# my_bot.get_all_followers('https://www.instagram.com/username/')
# my_bot.download_userpage_content("https://www.instagram.com/username/")
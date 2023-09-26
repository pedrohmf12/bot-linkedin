import os
import random
from time import sleep
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

class LinkedInBot:
    def __init__(self, username, password, profile_keywords):
        """
        __init__ _summary_

        Args:
            username (str): A string representing the username
            password (str): A string representing the password
            profile_keywords (str): A string representing the profile type for search
        """
        self.LOGIN = username
        self.PASSWORD = password
        self.PROFILE = profile_keywords

        self.SESSION_DIRECTORY = f'linkedin/session_{self.LOGIN}'
        if not os.path.exists(self.SESSION_DIRECTORY):
            os.makedirs(self.SESSION_DIRECTORY)

        self.SELECTORS = {
            "username_field": {"id": "username"},
            "password_field": {"id": "password"},
            "login_btn": {"xpath": "//button[@type='submit']"},
            "2fa_input": {"xpath": "/html/body/div/main/div[2]/form/div[1]/input[17]"},
            "user_logged_in": {"xpath": "//div[@class='member__profile']"},
            "search_btn": {"xpath": "//button[@class='search-global-typeahead__collapsed-search-button']"},
            "search_field": {"xpath": "//input[@class='search-global-typeahead__input']"},
            "peoples_connection": {"xpath": "//button[contains(@aria-label, 'Convidar')]"},
            "next_button": {"xpath": "//button[contains(@aria-label, 'Avançar')]"},
            "message_btn": {"xpath": ".//button[contains(@aria-label, 'Enviar mensagem')]"},
            "connection_username": {"xpath": ".//ancestor::div[contains(@class, 'entity-result__item')]//a[contains(@class, 'app-aware-link')]//span[@aria-hidden='true']"},
            "add_note_btn": {"xpath": "//button[@aria-label='Adicionar nota']"},
            "msg_txtarea": {"xpath": "//textarea[@name='message']"},
            "send_btn": {"xpath": "//button[@aria-label='Enviar agora']"}
        }

    def open_site(self):
        """
        open_site  this funcion is responsible for create the instance of the chromedriver and navigate to the linkedin website 
        """
        chrome_options = Options()
        chrome_options.add_argument("user-data-dir=" + os.path.abspath(self.SESSION_DIRECTORY))
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get('https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin')
        print("Site aberto com sucesso.")

    def verify_login(self):
        """
        Verify if the user is logged in.

        Returns:
            bool: True if the user is logged in, False otherwise.
        """
        try:
            user_logged_in = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, self.SELECTORS["user_logged_in"]["xpath"]))
            )
            if user_logged_in:
                print("O usuário já está logado.")
                return True
        except TimeoutException:
            print("O usuário não está logado.")
        return False

    def login_account(self):
        """
        Log into the user's account.

        This function fills in the username and password fields, submits the login form,
        and prints success or error messages.

        Returns:
            None
        """
        try:
            # Find and fill in the username field
            login_field = self.driver.find_element(By.ID, self.SELECTORS["username_field"]["id"])
            login_field.send_keys(self.LOGIN)
            sleep(random.randint(2, 5))
            
            # Find and fill in the password field
            pass_field = self.driver.find_element(By.ID, self.SELECTORS["password_field"]["id"])
            pass_field.send_keys(self.PASSWORD)
            print("Campos de login e senha preenchidos.")
            sleep(random.randint(2, 5))
            
            # Submit the login form by pressing Enter
            pass_field.send_keys(Keys.ENTER)
            print("Login realizado com sucesso.")
            sleep(random.randint(2, 5))
        except Exception as e:
            print(f"Erro ao fazer login: {str(e)}")

    def handle_2fa(self):
        """
        Handle Two-Factor Authentication (2FA) if prompted during login.

        If the current URL contains "checkpoint," the function prompts the user to input
        their 2FA code. It then attempts to locate the 2FA input field, enters the code,
        and submits it.

        Returns:
            None
        """
        if "checkpoint" in self.driver.current_url:
            verification_code = input("Digite o código 2FA e pressione Enter: ")
            try:
                # Wait for the presence of the 2FA input field and then locate it
                input_2fa_xpath = self.SELECTORS["2fa_input"]["xpath"]
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, input_2fa_xpath))
                )
                input_2fa_element = self.driver.find_element(By.XPATH, input_2fa_xpath)
                # Enter the 2FA code and submit it
                input_2fa_element.send_keys(verification_code)
                input_2fa_element.send_keys(Keys.ENTER)
                print("Código 2FA inserido e enviado.")
            except Exception as e:
                print(f"Erro ao lidar com o 2FA: {e}")

    def search_profiles(self, keywords):
        """
        Search for LinkedIn profiles based on provided keywords.

        This function takes a string of keywords, encodes them, and constructs a URL
        for searching LinkedIn profiles with those keywords.

        Args:
            keywords (str): Keywords for the profile search.

        Returns:
            str: The URL for the LinkedIn profile search.
        """
        try:
            # Encode the keywords and construct the search URL
            encoded_keywords = quote(keywords)
            base_url = "https://www.linkedin.com/search/results/people/"
            search_url = f"{base_url}?keywords={encoded_keywords}"
            return search_url
        except Exception as e:
            print(f"Erro ao compor a URL de pesquisa: {str(e)}")

    def navigate_to_search_page(self, page_number):
        """
        Navigate to a specific page of search results on LinkedIn.

        This function constructs the URL for the specified search results page number
        and then navigates to that page.

        Args:
            page_number (int): The page number of the search results to navigate to.

        Returns:
            None
        """
        try:
            search_url = self.search_profiles(self.PROFILE)
            page_url = f"{search_url}&page={page_number}"
            self.driver.get(page_url)
        except Exception as e:
            print(f"Erro ao navegar para a página {page_number} de pesquisa: {str(e)}")

    def connect_people(self, messages):
        """
        Connect with people on LinkedIn and send personalized connection requests with notes.

        This function finds and clicks the "Connect" button for multiple LinkedIn users,
        checks if you're already connected with them, and sends personalized connection
        requests with notes. It uses a list of messages to create personalized notes.

        Args:
            messages (list): List of messages to personalize connection requests.

        Returns:
            None
        """
        try:
            # Find the list of people connections in search results
            connections = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, self.SELECTORS["peoples_connection"]["xpath"]))
            )
            if connections:
                 # Get a list of "To Connect" buttons
                to_connect_btns = self.driver.find_elements(By.XPATH, self.SELECTORS["peoples_connection"]["xpath"])
                for to_connect_btn in to_connect_btns:
                    try:
                        # Check if the "Message" button is present; if yes, skip this user
                        to_connect_btn.find_element(By.XPATH, self.SELECTORS["message_btn"]["xpath"])
                        print(f'Você já está conectado com esta pessoa. Ignorando...')
                    except NoSuchElementException:
                        # Extract the user's username
                        connection_username = to_connect_btn.find_element(By.XPATH, self.SELECTORS["connection_username"]["xpath"])
                        people_username = connection_username.text.strip()
                        print(f'Se conectando com {people_username} e enviando nota')
                        
                        # Click the "Connect" button
                        to_connect_btn.click()
                        sleep(random.randint(2, 5))

                        # Extract the first name of the user
                        first_name = people_username.split()[0]

                        # Select a random message from the list and personalize it
                        message = random.choice(messages)
                        personalized_message = message.replace("[Nome da Pessoa]", first_name)

                        # Click the "Add a note" button
                        add_note_btn = self.driver.find_element(By.XPATH, self.SELECTORS["add_note_btn"]["xpath"])
                        add_note_btn.click()

                        # Enter the personalized message
                        msg_txtarea = self.driver.find_element(By.XPATH, self.SELECTORS["msg_txtarea"]["xpath"] )
                        msg_txtarea.send_keys(personalized_message)

                        sleep(random.randint(0, 5))

                        # Click the "Send" button
                        send_btn = self.driver.find_element(By.XPATH, self.SELECTORS["send_btn"]["xpath"])
                        send_btn.click()
                        sleep(random.randint(2, 5))
        except TimeoutException:
            print("Botão Conectar não encontrado.")
            return False
        except Exception as e:
            print(f"Erro ao conectar com as pessoas: {str(e)}")
            return False

    def connect_on_multiple_pages(self, messages, max_pages=20):
        """
        Connect with people on multiple pages of LinkedIn search results.

        This function navigates through multiple pages of LinkedIn search results, connects
        with people, and sends personalized connection requests with notes. It uses a list
        of messages to create personalized notes.

        Args:
            messages (list): List of messages to personalize connection requests.
            max_pages (int, optional): Maximum number of search result pages to navigate.
                Default is 20.

        Returns:
            None
        """
        current_page = 1
        self.navigate_to_search_page(page_number=current_page)

        while current_page <= max_pages:
            try:
                # Connect with people on the current page
                self.connect_people(messages)
                current_page += 1
                
                # Navigate to the next search result page
                self.navigate_to_search_page(page_number=current_page)
                sleep(random.randint(2, 5))

            except NoSuchElementException:
                print("Não foi possível encontrar o botão 'Avançar'. Finalizando a conexão.")
                break
            except Exception as e:
                print(f"Erro durante a conexão: {str(e)}")
                break

if __name__ == '__main__':
    username = 'seuemail@gmail.com'
    password = 'suasenha'
    profile_keywords = 'Palavra Chave'

    bot = LinkedInBot(username, password, profile_keywords)
    bot.open_site()
    if not bot.verify_login():
        bot.login_account()
        bot.handle_2fa()

    mensagens_personalizadas = [
        "Olá [Nome da Pessoa], sou [SEU NOME AQUI] e também trabalho na área de programação. Notei que temos interesses semelhantes e conexões em comum. Gostaria de nos conectar e trocar ideias sobre nossas experiências e projetos. Espero que possamos estabelecer uma conexão valiosa.",
        "Oi [Nome da Pessoa], percebi que compartilhamos interesses na área de programação, em python. Acredito que podemos aprender muito um com o outro e trocar conhecimento. Vamos nos conectar?",
        "Caro [Nome da Pessoa], sou [SEU NOME AQUI], um profissional da área de programação. Estou sempre em busca de expandir minha rede de contatos com pessoas talentosas e experientes como você. Vamos nos conectar e explorar oportunidades de colaboração?",
        "Oi [Nome da Pessoa], sou [SEU NOME AQUI], e estou sempre em busca de aprender com outros profissionais talentosos. Notei que você tem uma sólida experiência em programação. Vamos nos conectar e compartilhar nossos conhecimentos e insights?"
    ]
    bot.search_profiles(keywords=profile_keywords)
    bot.connect_on_multiple_pages(messages=mensagens_personalizadas)

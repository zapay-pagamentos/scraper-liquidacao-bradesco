from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from seleniumrequests import Chrome
from datetime import datetime
from .enum import StatesSet
from .helpers import log
import time
import os


class GetBradescoReceipts(object):

    index_page = "https://www.ne12.bradesconetempresa.b.br/ibpjlogin/login.jsf"
    renavams_list = []
    current_year = datetime.today().year
    receipt_list = []
    browser_driver = None
    user = os.environ.get('BDSC_USER')
    password = os.environ.get('BDSC_PASSWORD')
    code_ctrl = ''
    wait = None
    state = ""
    state_option = ""
    logged = False

    def __init__(self, renavams_list, state):
        self.logged = False
        self.renavams_list = renavams_list
        self.result = {
            "success_list": [],
            "fail_list": []
        }
        log("Initializing new process")
        log(f"{len(self.renavams_list)} renavams received")
        self.state = state
        self.state_option = StatesSet.get(state)
        log(f"State: {self.state}")
        self.initiate_browser()
        self.get_receipts()

    def initiate_browser(self):
        log("Initializing browser")
        chrome_options = Options()
        chrome_options.binary_location = ''
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument(
            '--browser.helperApps.neverAsk.saveToDisk=application/pdf'
        )
        if self.index_page:
            prefs = {
                "plugins.plugins_list": [
                    {"enabled": False, "name": "Chrome PDF Viewer"}
                ],
                "plugins.always_open_pdf_externally": True,
                "browser.download.folderList": 2,
                "download.default_directory": "./temp/",
                "download.extensions_to_open": "applications/pdf",
                "plugin.scan.plid.all": False,
                "plugin.scan.Acrobat": "99.0",

            }
            chrome_options.add_experimental_option("prefs", prefs)

        self.browser_driver = Chrome(chrome_options=chrome_options)
        self.browser_driver.implicitly_wait(1)
        self.wait = WebDriverWait(self.browser_driver, 30)


    def login(self):
        log("Login...")
        login_data = [
            {
                "id": "identificationForm:txtUsuario",
                "value": self.user
            },
            {
                "id": "identificationForm:txtSenha",
                "value": self.password
            }
        ]

        self.logged = False
        retry = 0
        while(retry < 3 and self.logged is not True):
            self.get_page(self.index_page)
            self.click_button_by_id("rdoTipoAcesso02")
            time.sleep(3)
            self.fill_form(login_data)
            self.click_button_by_id("identificationForm:botaoAvancar")
            time.sleep(5)
            element = self.browser_driver.find_element_by_id('_id402')
            if(element.text):
                self.browser_driver.execute_script(
                    "arguments[0].click();",
                    element
                )
                self.logged = True
                log("Login success")
            else:
                log("Login failed...")
                retry += 1
                if retry < 3:
                    log("Retry...")

        if retry >= 3:
            log("Login problem!")

    
    def get_search_receipt_page(self):
        search_url = (
            'https://www.ne12.bradesconetempresa.b.br' +
            '/ibpjreemissao/pesquisa.jsf'
        )
        search_url += "?CTRL=" + self.code_ctrl
        self.get_page(search_url)
        self.index_page = search_url

    def fill_search_form(self, renavam):
        log(f"\tFill {self.state} form")
        actions = ActionChains(self.browser_driver)
        self.get_search_receipt_page()
        self.select_option('cmbOperacoes', 'Débitos de Veículos')
        time.sleep(3)
        self.select_option('cmbUFDVReemissao', self.state_option)
        if self.state == 'SP':
            licensing_option = self.browser_driver.find_element_by_id(
                'frm:licenciamento_tipoDebitoSP'
            )
            self.browser_driver.execute_script(
                "arguments[0].click();",
                licensing_option
            )
            actions.send_keys(Keys.TAB)
            actions.perform()
            actions.send_keys(renavam+str(self.current_year))
            actions.perform()

        elif self.state == 'BA':
            actions.send_keys(Keys.TAB)
            actions.perform()
            actions.key_down(
                Keys.LEFT_SHIFT
            ).send_keys(
                Keys.TAB
            ).key_up(
                Keys.LEFT_SHIFT
            )
            actions.perform()
            actions.send_keys(renavam+str(self.current_year))
            actions.perform()

        confirm_button = self.browser_driver.find_element_by_id("frm:_id492")
        self.browser_driver.execute_script(
            "arguments[0].click();",
            confirm_button
        )
        time.sleep(3)

    def click_button_by_id(self, id):
        self.browser_driver.find_element_by_id(id).click()

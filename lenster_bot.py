import pathlib
import re
import secrets
import time
import random
import requests
from selenium.webdriver import Keys
import os
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import openai

files_path = str(pathlib.Path(__file__).resolve().parent) + "/"
EXTENSION_PATH = str(pathlib.Path(__file__).resolve().parent) + '/metamaskExtension.crx'
EXTENSION_ID = 'nkbihfbeogaeaoehlefnkodbefgpgknn'


def get_coin_value(symbol):
    # Get the current value of the coin using Binance API
    API_URL = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper() + 'USDT'}"
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        return float(data["price"])
    else:
        return None


def chatgpt():
    # Set up your API key
    openai.api_key = "YOUR_CHAT_GPT_API"

    # Define your prompt
    unique_id1 = secrets.token_hex(16)
    prompt = "write 10 unique tweet in different type of financial advice for cryptocurrency or stock market and finally choose randomly one of them and show me the chosen one."
    # "write 10 unique tweet about cryptocurrency in different type like: Blockchain Decentralization Smart contracts Ethereum Bitcoin Altcoins Cryptography Mining Wallets Tokens NFTs DeFi DApps Gas fees Consensus Proof of work Proof of stake Scaling Layer 2 Sharding DAOs Governance Interoperability Cross-chain Web3 IPFS Filecoin Polkadot Solana Avalanche Binance Smart Chain Chainlink Oracles Decentralized exchanges Liquidity pools Yield farming Staking Lending Borrowing Flash loans AMMs Impermanent loss Crypto wallets Hardware wallets Cold storage Hot wallets Public keys Private keys Seed phrases Multi-sig wallets Crypto taxes Crypto regulations KYC AML Privacy coins Monero Zcash Dash Mimblewimble Lightning Network Raiden Network Plasma Rollups EIP-1559 Gas limit Gas price Forks Soft forks Hard forks Bitcoin Cash Bitcoin SV Ethereum Classic Dogecoin Cardano Tezos Cosmos Filecoin Arweave Sia Storj Golem Augur 0x Uniswap SushiSwap PancakeSwap Curve Balancer Aave Compound MakerDAO Synthetix Nexus Mutual Yearn Finance Rarible OpenSea SuperRare CryptoKitties Axie Infinity The Sandbox and finally choose randomly one of them and show me the chosen one."
    # f"write a very short insights on these topic and please choose one of these topic and write a short tweet about that only. you can use one of these topic randomly : cardano , pancakeswap, binance lab, matic, qgix, ai token, defi , stable coin , nft , market futers , swap , liquidity , pools , staking , margin, call margin , bitcoin , decentralasation , cbdc , scam , financial advice about being safe in crypto market , borrow and land platfor, gaming platform , bet platform, mining , pos , pow ({unique_id1})."

    # Set up the parameters for the text generation
    model_engine = "text-davinci-002"
    max_tokens = 1024
    temperature = 0.7

    # Call the OpenAI API to generate the text
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # Extract the generated text from the response
    generated_text = response.choices[0].text.strip()
    tweets = []
    for tweet in generated_text.split("\n"):
        if tweet.strip() != "":
            try:
                if re.match(r"^\d+\.", tweet):
                    twit = re.sub(r"^\d+\.", "", tweet)
                    tweets.append(twit.strip())
                else:
                    tweets.append(tweet.strip())

            except IndexError:
                tweets.append(tweet.strip())

    # Choose a random tweet and print it
    chosen_tweet = random.choice(tweets)

    return str(chosen_tweet)


def downloadMetamaskExtension():
    print('Setting up metamask extension please wait...')
    url = 'https://xord-testing.s3.amazonaws.com/selenium/10.0.2_0.crx'
    urllib.request.urlretrieve(url, str(pathlib.Path(__file__).resolve().parent) + '/metamaskExtension.crx')
    print("Metamask Extention Download completed.")


def launchSeleniumWebdriver(headless):
    # print('path', EXTENSION_PATH)
    chrome_options = Options()
    if headless == True:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--enable-automation")
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    # chrome_options.add_argument("window-size=1400,2100")
    chrome_options.add_argument(f"user-data-dir={files_path}TestProfile")  # Save Profile
    #chrome_options.add_argument(f"--profile-directory={files_path}TestProfile")  # Choose witch profile you would like to use
    chrome_options.add_extension(EXTENSION_PATH)

    global driver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    time.sleep(5)
    print("Extension has been loaded")
    return driver



def metamaskSetup():
    recoveryPhrase = "seed1 seed2 seed3 seed4 seed5 seed6 seed7 seed8 seed9 seed10 seed11 seed12"
    password = "YourPassword"
    driver.get("chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html")
    time.sleep(1)
    current_address = str(driver.current_url)
    print(current_address)
    metamask_install = False
    if current_address.endswith("unlock"):
        print("MetaMask is installed.")
        metamask_install = True
    else:
        print("MetaMask is not installed.")

    if metamask_install == False:
        driver.get('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#initialize/welcome')
        driver.switch_to.window(driver.window_handles[1])

        driver.find_element(By.XPATH, '//button[text()="Get Started"]').click()
        driver.find_element(By.XPATH, '//button[text()="Import wallet"]').click()
        driver.find_element(By.XPATH, '//button[text()="No Thanks"]').click()

        time.sleep(5)

        inputs = driver.find_elements(By.XPATH, '//input')
        inputs[0].send_keys(recoveryPhrase)
        inputs[1].send_keys(password)
        inputs[2].send_keys(password)
        driver.find_element(By.CSS_SELECTOR, '.first-time-flow__terms').click()
        time.sleep(1)
        import_button = driver.find_element(By.XPATH, '//button[text()="Import"]')
        import_button.click()
        time.sleep(5)

        driver.find_element(By.XPATH, '//button[text()="All Done"]').click()
        time.sleep(2)

        # closing the message popup after all done metamask screen
        driver.find_element(By.XPATH, '//*[@id="popover-content"]/div/div/section/header/div/button').click()
        time.sleep(2)
        print("Wallet has been imported successfully")
        time.sleep(10)
        driver.switch_to.window(driver.window_handles[0])
        driver.save_screenshot(files_path + "sign2.png")

    else:
        print("Metamask Alls Set Completed")
        driver.switch_to.window(driver.window_handles[0])


def Unlock_Wallet():
    driver.switch_to.window(driver.window_handles[1])
    driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
    time.sleep(0.5)
    import_wallet_button = driver.find_element(By.XPATH, '//*[@id="password"]')
    import_wallet_button.send_keys("YourPassword")
    time.sleep(0.5)
    import_wallet_button.send_keys(Keys.RETURN)
    CYAN = "\033[36m"
    print(CYAN + "Login to Metamask Wallet Success.\n")
    driver.switch_to.window(driver.window_handles[0])


def changeMetamaskNetwork(networkName):
    # opening network
    print("Changing network")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('chrome-extension://{}/home.html'.format(EXTENSION_ID))
    print("closing popup")
    time.sleep(5)
    try:
        popup_close_button = driver.find_element(By.XPATH,
                                                 '//*[@id="popover-content"]/div/div/section/header/div/button')
        if popup_close_button.is_displayed():
            popup_close_button.click()
    except NoSuchElementException:
        pass

    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
    time.sleep(2)
    print("opening network dropdown")
    time.sleep(2)
    elem = driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div')
    time.sleep(2)
    all_li = elem.find_elements(By.TAG_NAME, "li")
    time.sleep(2)
    for li in all_li:
        text = li.text
        if (text == networkName):
            li.click()
            print(text, "is selected")
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(3)
            return
    time.sleep(2)
    print("Please provide a valid network name")

    driver.switch_to.window(driver.window_handles[0])
    time.sleep(3)


def signConfirm():
    print("sign")
    time.sleep(3)

    # driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get('chrome-extension://{}/popup.html'.format(EXTENSION_ID))
    time.sleep(5)
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    time.sleep(1)

    #New NEXT BUTTON CHECKING :
    def check_next_sign_button():
        try:
            check_signz_button = driver.find_element(By.XPATH,
                                                     '//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]')
            if check_signz_button.is_displayed():
                return True
            else:
                return False
        except:
            pass

    # check if the element exists
    if check_next_sign_button():
        time.sleep(2)
        Next_BTN = driver.find_element(By.XPATH,
                                       '//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]')
        Next_BTN.click()
        time.sleep(1)
        connect_BTN = driver.find_element(By.XPATH,
                                          '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]')
        connect_BTN.click()
        time.sleep(1)
    else:
        try:
            button_element = driver.find_element(By.XPATH, "//div[@class='request-signature__footer']//button[text()='Sign']")
            check_sgn_button = driver.find_element(By.XPATH, "//div[@class='request-signature__footer']//button[text()='Sign']")
            sign_but = driver.find_element(By.XPATH, "//div[@class='request-signature__footer']//button[text()='Sign']")
            if check_sgn_button.is_displayed():
                if not check_sgn_button.is_enabled():
                    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[4]/div[1]/i').click()
                    check_sgn_button.click()
                else:
                    check_sgn_button.click()
            elif sign_but.is_displayed():
                sign_but.click()
            else:
                print("There is no tx for signing")
        except:
            pass





    time.sleep(1)
    # driver.find_element_by_xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
    # time.sleep(3)
    print('Sign confirmed')
    # print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(3)


# Check We are Login or not this is the first time :

def check_login():
    try:
        check_login_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/header/div/div/div[2]/button/div').text

        # check if the length of the list is greater than 0
        if check_login_button == "Login":
            print("Not Login")
            return True
        else:
            print("Logined")
            return False
    except :
        pass


def connectToWebsite(url):
    driver.get(url)
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[0])
    driver.save_screenshot("handle.png")

    if check_login():
        connect_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/header/div/div/div[2]/button')))
        connect_button.click()

        time.sleep(2)

        # '/html/body/div[3]/div/div/div/div/div[2]/div[2]/div/div[2]/button[1]' browser wallet
        # "/html/body/div[3]/div/div/div/div/div[2]/div[2]/div/div[2]/div/button[1]" sign with wallet
        # find the element by its ID
        def check_sign_in_wallet_or_web_browser():
            try:
                driver.find_element(By.XPATH, './/div[2]/div/div[2]/div/button[1]')
            except NoSuchElementException:
                return False
            return True

        if check_sign_in_wallet_or_web_browser():
            print("Sign-In with Lens")
            finalsign_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[3]/div/div/div/div/div[2]/div[2]/div/div[2]/div/button[1]')))
            finalsign_button.click()
            signConfirm()
            print("Login To Lens Success")
        else:
            print("Browser Wallet")
            finalsign_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, './/div[2]/div[2]/div/div[2]/button[1]')))
            finalsign_button.click()
            signConfirm()
            time.sleep(2)
            finalsign_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, './/div[2]/div/div[2]/div/button[1]')))
            finalsign_button.click()
            time.sleep(2)
            signConfirm()
            print("First Login To Lens Success")

        # driver.execute_script("window.open('');")
        # driver.switch_to.window(driver.window_handles[-1])

        time.sleep(3)
        print('Lens Connected to Metamask')
        # print(driver.window_handles)
        driver.switch_to.window(driver.window_handles[0])

    else:
        # You Are Logined Enjoy for Scrapping From Lens:
        print("Lens Logined Success")


def like():
    # wait for the page to load
    wait = WebDriverWait(driver, 10)
    time.sleep(5)
    action = ActionChains(driver)
    i = 3
    counter = 0

    # scroll through the entire page and click on each like and mirror button
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        like_buttons = action.move_to_element(driver.find_element(By.XPATH, f"(.//button[@aria-label='Like'])[{i}]")).perform()

        time.sleep(3)

        # check if the like button has already been liked
        like_button = wait.until(EC.presence_of_element_located((By.XPATH, f"(.//button[@aria-label='Like'])[{i}]")))
        i = i + 1
        path_element = like_button.find_element(By.XPATH, ".//span/*[name()='svg']/*[name()='path']")
        if path_element.get_attribute("fill-rule") == "evenodd":
            continue

        # click on the like button
        ActionChains(driver).click(like_button).perform()
        counter = counter + 1
        MAGENTA = "\033[35m"
        print(MAGENTA + str(counter))
        time.sleep(2)

        # scroll down to the next set of like buttons
        new_height = driver.execute_script("return document.body.scrollHeight")

        last_height = new_height
    driver.quit()

def like_and_mirror():
    # wait for the page to load
    wait = WebDriverWait(driver, 10)
    time.sleep(5)
    action = ActionChains(driver)
    i = 3
    like_counter = 0
    mirror_counter = 0

    # scroll through the entire page and click on each like and mirror button
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        like_buttons = action.move_to_element(driver.find_element(By.XPATH, f"(.//button[@aria-label='Like'])[{i}]")).perform()
        time.sleep(1)
        # check if the like button has already been liked
        like_button = wait.until(EC.presence_of_element_located((By.XPATH, f"(.//button[@aria-label='Like'])[{i}]")))

        #Mirror
        mirror_buttons = action.move_to_element(driver.find_element(By.XPATH, f"(.//button[@aria-label='Mirror'])[{i}]")).perform()
        time.sleep(2)
        # check if the like button has already been liked
        mirror_button = wait.until(EC.presence_of_element_located((By.XPATH, f"(.//button[@aria-label='Mirror'])[{i}]")))
        mirrored_btn = driver.find_element(By.XPATH, f"(.//button[@aria-label='Mirror']//div)[{i}]")
        mirrored_btn_div_class = mirrored_btn.get_attribute("class")
        #print(mirrored_btn_div_class)
        i = i + 1

        like_path_element = like_button.find_element(By.XPATH, ".//span/*[name()='svg']/*[name()='path']")
        if not like_path_element.get_attribute("fill-rule") == "evenodd":
            ActionChains(driver).click(like_button).perform()
            like_counter = like_counter + 1

        # click on the like button

        time.sleep(4)

        if not mirrored_btn_div_class == "hover:bg-green-300 rounded-full p-1.5 hover:bg-opacity-20":
            ActionChains(driver).click(mirror_button).perform()
            time.sleep(1)
            signConfirm()
            mirror_counter = mirror_counter + 1


        time.sleep(2)

        MAGENTA = "\033[35m"
        print(MAGENTA + f"Total Like : {like_counter}   |   Total Mirror : {mirror_counter}")

        # scroll down to the next set of like buttons
        new_height = driver.execute_script("return document.body.scrollHeight")

        last_height = new_height
    driver.quit()

def post(post_time):
    while True:
        time.sleep(2)
        msg_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div[1]/div[1]/div/button')))
        msg_button.click()
        time.sleep(2)

        msg_input = driver.find_element(By.XPATH, './/div/div/div/div/div[2]/div[2]/div[1]/div[2]')
        msg_input.click()
        # msg_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        # (By.XPATH, '/html/body/div[2]/div/div/div/div/div[2]/div[2]/div[1]/div[2]')))
        # msg_input.click()
        timing = int(time.time())
        msgtext = chatgpt()
        time.sleep(2)
        if msgtext:
            btc = get_coin_value("BTC")
            eth = get_coin_value("ETH")
            ada = get_coin_value("ADA")
            msgtext = msgtext + "\n" + f"BTC : {btc}  |  ETH : {eth}  |  ADA : {ada}"
            msg_input.send_keys(msgtext)
            post_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, './/div/div/div/div/div[2]/div[2]/div[2]/div[2]/button')))
            post_btn.click()
            GREEN = "\033[32m"
            YELLOW = "\033[33m"
            print(GREEN + f"New Post: " + YELLOW + f"{msgtext}")
        else:
            RED = "\033[31m"
            print(RED + f"Chat GPT Dosen't Work Correctly!")
        time.sleep(post_time)
    driver.quit()

# Setup Extention in WebDriver:
if not os.path.exists(EXTENSION_PATH):
    downloadMetamaskExtension()
else:
    print("Metamask .CRX File already exists.")

driver = launchSeleniumWebdriver(True)
metamaskSetup()
time.sleep(2)
Unlock_Wallet()
time.sleep(2)
connectToWebsite("https://lenster.xyz/")
#driver.get("https://lenster.xyz/u/relaxbody")
time.sleep(2)

#like()
#like_and_mirror()
post(100)

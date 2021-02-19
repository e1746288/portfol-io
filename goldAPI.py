import selenium
from selenium import webdriver	# Allows you to launch/initialise a browser.
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait	 # Allows you to wait for a page to load.
from selenium.webdriver.support import expected_conditions as EC  # Specify what you are looking for on a specific page in order to determine that the webpage has loaded.
from selenium.webdriver.common.by import By	 # Allows you to search for things using specific parameters.
from selenium.common.exceptions import TimeoutException  # Handling a timeout situation.

goldSymbolDict =\
    {
        "bilezik":  "tdB_T",
        "gr":       "tdGAT",
        "ceyrek":   "tdEC",   
        "yarım":    "tdEY",    
        "tam":      "tdET",      
        "ata":      "tdA_T"
    }

def get_gold_prices(goldList):

    # Chrome WebDriver Options
    chrome_options = Options()
    # Comment the line below if you would like to watch the kapos-man!
    chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--start-maximized")
    try:
        driver = webdriver.Chrome(executable_path='.\\webDrivers\\chromedriver.exe', options=chrome_options)
    except:
        driver = webdriver.Chrome(executable_path='./webDrivers/chromedriver', options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.altinkaynak.com/Altin/Kur/Guncel")
    goldTable = wait.until(EC.visibility_of_element_located((By.XPATH, "//table[@class='table gold']/tbody")))

    goldDict = {}
    for gold in goldList:
        gSymbol = goldSymbolDict[gold]
        buy = goldTable.find_element_by_id(gSymbol+"Buy").text.replace(',', '.')
        sell = goldTable.find_element_by_id(gSymbol+"Sell").text.replace(',', '.')
        goldDict[gold] = {}
        goldDict[gold]["buyRate"] = float(buy)
        goldDict[gold]["sellRate"] = float(sell)
    
    driver.quit()
    return goldDict
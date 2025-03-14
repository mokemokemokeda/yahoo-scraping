import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


# Chromeのオプションを設定
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')  # ヘッドレスモードでブラウザを表示せずに動作

# Chrome WebDriverのインスタンスを作成
driver = webdriver.Chrome(options=CHROME_OPTIONS)

# 検索キーワード
keyword = 'JELEE'

# URLエンコード
url_encoded_keyword = urllib.parse.quote(keyword)

# WebDriverでYahooリアルタイム検索のページを開く
driver.get(f'https://search.yahoo.co.jp/realtime/search?p={url_encoded_keyword}')
time.sleep(1)  # サーバー側の負荷を避けるために1秒待機

# 「Tab_on__cXzYq」クラスの要素をクリックして、タイムラインの自動更新を停止する
driver.find_element(By.CLASS_NAME, 'Tab_on__cXzYq').click()
time.sleep(1)

def extract_tweet_texts(tweet_elements):
    '''
    ツイートのテキストを取得する
    '''
    tweet_texts = []
    for tweet_element in tweet_elements:
        try:
            # ツイートのテキスト要素を取得
            tweet_text_element = tweet_element.find_element(By.CLASS_NAME, 'Tweet_body__XtDoj')
            tweet_texts.append(tweet_text_element.text)
        except NoSuchElementException:
            continue
    return tweet_texts

# ツイートコンテナ要素を取得
tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')

# ツイートのテキストを取得
tweet_texts = extract_tweet_texts(tweet_elements)

print("取得したツイート数: ", len(tweet_texts))
def scroll_to_elem(driver, elem):
    '''
    指定された要素までスクロールする
    '''
    try:
        actions = ActionChains(driver)
        actions.move_to_element(elem)
        actions.perform()
        time.sleep(1)
        return True
    except (NoSuchElementException, StaleElementReferenceException):
        return False

def find_show_more_button(driver):
    '''
    もっと見るボタンを取得する
    '''
    try:
        return driver.find_element(By.CLASS_NAME, 'More_More__rHgzp')
    except NoSuchElementException:
        return None

def click_show_more_button(driver):
    '''
    もっと見るボタンをクリックする
    '''
    try:
        find_show_more_button(driver).click()
        time.sleep(1)
        return True
    except NoSuchElementException:
        return False

def extract_tweet_elements(driver, max_tweets=100):
    '''
    ツイート要素を取得する
    '''
    # "もっと見る"ボタンをクリックして追加のツイートを取得
    while True:
        # ツイートコンテナ要素を取得
        tweet_elements = driver.find_elements(By.CLASS_NAME, 'Tweet_TweetContainer__gC_9g')
        
        # 取得ツイート数が指定された数に達するか、もっと見るボタンがない場合は終了
        if len(tweet_elements) >= max_tweets or not find_show_more_button(driver):
            break
        
        # もっと見るボタンをクリック
        click_show_more_button(driver)
        
        # 指定回数スクロール（次のもっと見るボタンが出てくるまで）
        while True:
            # もっと見るボタンを取得
            show_more_button_element = find_show_more_button(driver)
            
            # もっと見るボタンまでスクロール
            scroll_to_elem(driver, show_more_button_element)
            
            # もっと見るボタンがないか、もっと見るボタンまでスクロール出来たら終了
            if not find_show_more_button(driver) or show_more_button_element == find_show_more_button(driver):
                break
    
    return tweet_elements[:max_tweets]

# ツイートを取得
tweet_elements = extract_tweet_elements(driver, max_tweets=100)

# ツイートのテキストを取得
tweet_texts = extract_tweet_texts(tweet_elements)
print("取得したツイート数: ", len(tweet_texts))

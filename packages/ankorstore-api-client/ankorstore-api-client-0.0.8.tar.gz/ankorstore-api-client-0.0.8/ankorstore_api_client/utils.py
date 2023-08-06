def urljoin(*args):
    """
    Joins given arguments into a url. Trailing but not leading slashes are
    stripped for each argument.
    https://stackoverflow.com/a/11326230
    """
    return "/".join(map(lambda x: str(x).strip('/').rstrip('/'), args))

def transfert_cookies(driver, s):
    headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    }
    s.headers.update(headers)

    for cookie in driver.get_cookies():
        c = {cookie['name']: cookie['value']}
        s.cookies.update(c)

def transfert_headers(res, s):
    src_headers = {
        k: v
        for k, v in res.headers.items()
    }
    s.headers.update(src_headers)

def init_firefox_browser():
    from seleniumwire import webdriver
    from selenium.webdriver.firefox.options import Options

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    browser = webdriver.Firefox(firefox_options=options)
    return browser

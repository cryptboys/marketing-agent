import os, sys, time, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--log-level=3')
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    s = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=s, options=opts)

def screenshot(url, path='debug.png'):
    """Ambil screenshot dashboard. path relatif ke CWD."""
    d = _driver()
    try:
        d.get(url)
        d.implicitly_wait(3)
        time.sleep(1)
        ap = os.path.abspath(path)
        d.save_screenshot(ap)
        return {"ok": True, "path": ap, "size": os.path.getsize(ap) if os.path.exists(ap) else 0}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        d.quit()

def page_source(url):
    """Ambil HTML yg sudah di-render untuk analisa DOM."""
    d = _driver()
    try:
        d.get(url)
        d.implicitly_wait(3)
        time.sleep(1)
        return {"ok": True, "html": d.page_source, "title": d.title, "url": d.current_url}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        d.quit()

def evaluate(url, js):
    """Jalankan JavaScript di halaman, return hasilnya."""
    d = _driver()
    try:
        d.get(url)
        d.implicitly_wait(3)
        time.sleep(1)
        r = d.execute_script(js)
        return {"ok": True, "result": r}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        d.quit()

def check_menu(url):
    """Cek apakah menu dashboard beneran ganti konten atau cuma alert."""
    js = """
        const menus = document.querySelectorAll('[data-menu], .menu-item, nav a, aside a');
        return Array.from(menus).map(m => ({
            text: m.textContent.trim(),
            href: m.href || '',
            onclick: m.onclick ? m.onclick.toString().substring(0, 150) : (m.getAttribute('onclick') ? m.getAttribute('onclick').substring(0, 150) : ''),
            id: m.id || '',
            class: m.className
        }));
    """
    return evaluate(url, js)

def check_page_content(url):
    """Deteksi placeholder atau dummy text di halaman."""
    js = """
        const text = document.body.innerText.toLowerCase();
        const found = [];
        const markers = ['coming soon', 'lorem ipsum', 'dummy', 'placeholder', 'sample data', 'under construction'];
        markers.forEach(m => { if(text.includes(m)) found.push(m); });
        return {found, has_dummy: found.length > 0};
    """
    return evaluate(url, js)

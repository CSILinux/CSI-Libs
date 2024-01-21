import sys, os, shutil, subprocess, json, requests, psutil, time

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtNetwork import QNetworkProxy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from stem import Signal
from stem.control import Controller
import stem.process
import stem
import stem.control

from bs4 import BeautifulSoup
from functools import partial
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


import socket
import socks
from stem import Signal
from stem.control import Controller

from .utils import get_random_useragent
from .auth import checkpass

def ChromedriverCheck(startme, additional_options=None, onion=False):
    driver = None
    # https://stackoverflow.com/questions/76727774/selenium-webdriver-chrome-115-stopped-working
    chromedriver_path = ChromeDriverManager().install()

    def check_tor_usage():
        response = requests.get("https://check.torproject.org/?lang=en-US&small=1&uptodate=1")
        if "Congratulations" in response.text:
            print("Tor is being used.")
        else:
            print("Tor is not being used.")

    def start_chromedriver():
        print("Initializing WebDriver...")
        service = Service(chromedriver_path)
        service.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--incognito")
        options.add_argument("--headless")

        # Add additional options if provided
        if additional_options:
            for option in additional_options:
                options.add_argument(option)

        if onion:
            options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://check.torproject.org/?lang=en-US&small=1&uptodate=1")
        check_tor_usage()

        print("Chromedriver service started.")
        return driver

    if startme.lower() == "on":
        driver = start_chromedriver()

    elif startme.lower() == "off":
        # Kill all running chromedriver processes
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and proc.info['name'].startswith('chromedriver'):
                proc.terminate()
        print("Chromedriver instances have been stopped.")

    else:
        print("Invalid command. No action taken.")

    return driver
    
def TorCheck(Torstartme):
    def check_tor_service():
        command = ["service", "tor", "status"]
        result = subprocess.run(command, capture_output=True)
        output = result.stdout.decode().lower()
        # Check if service has exited
        if "active: active" not in output:
            print("Service not running")
            return False
        else:
            print("Service is running")
            return True

    def check_tor_usage():
        url = "https://check.torproject.org/?lang=en-US&small=1&uptodate=1"
        proxies = {
            "http": "socks5h://localhost:9050",
            "https": "socks5h://localhost:9050",
        }
        try:
            response = requests.get(url, proxies=proxies)
            if "Congratulations" in response.text:
                print("Tor is being used.")
            else:
                print("Tor is not being used.")
        except requests.exceptions.RequestException as e:
            print(f"Error checking Tor usage: {e}")
 
    def request_newnym():
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        clearnet_ip, _ = my_ip()  # Extract the IP and ignore the istor
        tor_ip, _ = my_tor_ip()  # Extract the IP and ignore the isto
        print(f"Clearnet IP: " + clearnet_ip)
        print(f"Tor IP: " + tor_ip)
        # while True:
            # if sent loop time.sleep(tortime)
            # Change identity
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                print("New identity signal sent successfully.")
        except stem.InvalidRequest as e:
            print(f"Invalid request to send the NEWNYM signal: {e}")
        except stem.OperationFailed as e:
            print(f"Failed to send the NEWNYM signal: {e}")      
        except stem.ControllerError as e:
            print(f"An error occurred while communicating with the Tor controller: {e}")
        except stem.PasswordAuthFailed as e:
            print(f"Authentication failed. Please check the Tor controller password.")
        return
            
    if Torstartme == "on":
        service_was_running = check_tor_service()
        if not service_was_running:
            password = checkpass()
            command = ["sudo", "-S", "service", "tor", "start"]
            try:
                subprocess.run(command, input=password.encode(), check=True)
                print("Tor service started.")
                time.sleep(10)  # wait for 10 seconds
            except subprocess.CalledProcessError as e:
                print(f"Error starting Tor service: {e}")
        check_tor_usage()

    elif Torstartme == "newnym":
        if check_tor_service():
            print("Tor service is running.")
            request_newnym()
            check_tor_usage()

    elif Torstartme == "off":
        password = checkpass()

        command = ["sudo", "-S", "service", "tor", "stop"]
        try:
            subprocess.run(command, input=password.encode(), check=True)
            print("Tor service stopped.")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping Tor service: {e}")
    else:
        print("Invalid Torstartme command. No action taken.")
	# Usage
	# TTorstartme = "on"  # Set to "off" to stop Tor, "newnym" to request new identity
	# TorCheck(Torstartme)

# OLD my_ip
def my_ip():
    headers = get_random_useragent()
    try:
        response = requests.get('https://check.torproject.org/', headers=headers)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None, None

    if "Congratulations" in response.text:
        istor = "on"
    else:
        istor = "off"

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        ip_element = soup.find('p').find('strong')
        ip_address = ip_element.text.strip()
    except AttributeError:
        print("Failed to parse the response HTML. The structure of the page may have changed.")
        return None, None

    return ip_address, istor

# OLD WhatIsMyTorIP
def my_tor_ip():
    headers = get_random_useragent()
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    try:
        response = requests.get('https://check.torproject.org/', headers=headers, proxies=proxies)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None, None

    istor = None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        ip_element = soup.find('p').find('strong')
        ip_address = ip_element.text.strip()
    except AttributeError:
        print("Failed to parse the response HTML. The structure of the page may have changed.")
        return None, None

    return ip_address, istor


def CSIIPLocation(ip_address, istor):
    # Define the URLs for different APIs
    api_urls = {
        "ipapi": f"https://ipapi.co/{ip_address}/json/",
        "ipinfo": f"https://ipinfo.io/{ip_address}/json",
        "ip-api": f"http://ip-api.com/json/{ip_address}",
    }

    headers = get_random_useragent()

    # Iterate over the APIs
    for api_name, url in api_urls.items():
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()

                if not any(keyword in data for keyword in ["error", "limit", "permission", "403", "forbidden"]):
                    print(f"CSIIPLocation After {api_name}: {ip_address}")

                    # Extract and standardize latitude and longitude
                    latitude = data.get('latitude') or data.get('lat') or (float(data.get('loc', ',').split(',')[0]) if 'loc' in data else None)
                    longitude = data.get('longitude') or data.get('lon') or (float(data.get('loc', ',').split(',')[1]) if 'loc' in data else None)

                    # Replace or add the standardized coordinates into the response data
                    data['latitude'], data['longitude'] = latitude, longitude

                    return data
                else:
                    raise ValueError(f"Response from {api_name} contains 'error' or 'limit'.")
            else:
                raise requests.exceptions.HTTPError(f"Request to {api_name} returned status code {response.status_code}.")
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"Could not fetch or decode the response from {api_name}. Trying next API... {e}")

    # If we've gone through all APIs and haven't returned yet, then all requests failed
    print("Could not fetch or decode the response from any service. Getting information from Torproject to verify Tor access.")
    if istor == "on":
        print("Returning default Tor message due to all service failures.")
        return {"ip": ip_address, "message": "Congratulations, you are using Tor"}

    return None

# Multithreaded version of the above one
def CSIIPLocation2(ip_address, istor):
    # Define the URLs for different APIs
    api_urls = {
        "ipapi": f"https://ipapi.co/{ip_address}/json/",
        "ipinfo": f"https://ipinfo.io/{ip_address}/json",
        "ip-api": f"http://ip-api.com/json/{ip_address}",
    }

    headers = get_random_useragent()

    # Iterate over the APIs
    def multi_task(api_url):
        api_name, url = api_url
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()

            if not any(keyword in data for keyword in ["error", "limit", "permission", "forbidden"]):
                print(f"CSIIPLocation After {api_name}: {ip_address}")

                # Extract and standardize latitude and longitude
                latitude = data.get('latitude') or data.get('lat') or (float(data.get('loc', ',').split(',')[0]) if 'loc' in data else None)
                longitude = data.get('longitude') or data.get('lon') or (float(data.get('loc', ',').split(',')[1]) if 'loc' in data else None)

                # Replace or add the standardized coordinates into the response data
                data['latitude'], data['longitude'] = latitude, longitude

                return data
            else:
                raise ValueError(f"Response from {api_name} contains 'error' or 'limit'.")
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException, requests.exceptions.JSONDecodeError, ValueError):
            print(f"Could not fetch or decode the response from {api_name}. Trying next API...")

    def check_results(results):
        for result in results:
            if result:  # If non-empty result is found
                print("Terminating remaining threads...")
                # Cancel all pending tasks
                for future in futures:
                    if future.done():
                        future.cancel()
                break
    
    with ThreadPoolExecutor() as executor:
        t1 = time.perf_counter()

        futures = [executor.submit(partial(multi_task), api_url) for api_url in api_urls.items()]
        results = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED).done
        check_results(results)
        print(results)
        print("time taken by multi: ",time.perf_counter() - t1)


    # If we've gone through all APIs and haven't returned yet, then all requests failed
    print("Could not fetch or decode the response from any service. Getting information from Torproject to verify Tor access.")
    if istor == "on":
        print("Returning default Tor message due to all service failures.")
        return {"ip": ip_address, "message": "Congratulations, you are using Tor"}

    return None


def connectMeTo(network: str, object_proxy=None):
    """Incomplete summary: connects Pyside6 webengineview, chrome driver and socks tor and other nets
    

    Args:
        network (str): 'tor' or 'i2p' or 'loki'
        object_proxy (Object/Class, optional): takes webdriver.Chrome() or QWebEngineView() Object. Defaults to None.

    Returns:
        object: only returns in case of chromedriver
    """
    network = network.lower()
    match network:
        case "tor":
            return _connect_to_tor(object_proxy)
            
            
def disconnectMeFrom(network: str, object_proxy=None):
    network = network.lower()
    match network:
        case "tor":
            return _disconnect_from_tor(object_proxy)
            

# the below dis/connect functions are only intended to be used by dis/connectMe[To/From]() 
def _connect_to_tor(object_proxy = None):
    # Check if Tor service is running
    if os.name == 'posix':  # Linux
        tor_running = os.system("systemctl is-active --quiet tor")
    elif os.name == 'nt':  # Windows
        tor_running = os.system("sc query tor | findstr STATE_RUNNING")

    if tor_running == 0:
        try:
            # Connect to the Tor control port with authentication
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()  # You may need to provide username and password here

            # Set SOCKS proxy for QWebEngineView if provided
            if object_proxy and isinstance(object_proxy, QWebEngineView):
                # Check if QWebEngineView has a valid QWebEnginePage
                if object_proxy.page():
                    # Set up QNetworkProxy for QWebEngineView
                    proxy = QNetworkProxy()
                    proxy.setType(QNetworkProxy.Socks5Proxy)
                    proxy.setHostName("127.0.0.1")
                    proxy.setPort(9050)
                    QNetworkProxy.setApplicationProxy(proxy)
                return object_proxy

            # Set SOCKS proxy for ChromeDriver if provided
            elif object_proxy and isinstance(object_proxy, webdriver.Chrome):
                # Set up the SOCKS proxy for connection
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
                
                # Create a new ChromeDriver instance with the updated options
                chromedriver = webdriver.Chrome(options=chrome_options)
                print("Connected to Tor with ChromeDriver.")
                return chromedriver
            
            else:
                # Set up the SOCKS proxy for connection
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
                socket.socket = socks.socksocket


            print("Connected to Tor.")
        except Exception as e:
            print(f"Error connecting to Tor: {e}")
    else:
        print("Tor service is not running.")    
        
        
def _disconnect_from_tor(object_proxy=None):
    try:
        # If object_proxy is a QWebEngineView, revert the QNetworkProxy settings
        if object_proxy and isinstance(object_proxy, QWebEngineView):
            QNetworkProxy.setApplicationProxy(QNetworkProxy())
            print("Disconnected from Tor in QWebEngineView.")

        # If object_proxy is a ChromeDriver, update the SOCKS proxy settings
        elif object_proxy and isinstance(object_proxy, webdriver.Chrome):
            # Set up the SOCKS proxy for connection
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')

            object_proxy.quit()
                        
            # Create a new ChromeDriver instance with the updated options
            chromedriver = webdriver.Chrome(options=chrome_options)
            print("Disconnected from Tor in ChromeDriver.")
            return chromedriver

        # Send a NEWNYM signal to Tor to get a new IP address
        with Controller.from_port(port=9051) as controller:
            controller.signal(Signal.NEWNYM)
            print("Disconnected from Tor network. Moved to surface net.")

    except Exception as e:
        print(f"Error disconnecting from Tor: {e}")
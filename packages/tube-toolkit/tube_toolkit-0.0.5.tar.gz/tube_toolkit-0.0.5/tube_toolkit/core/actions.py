from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.keys import Keys
from typing import Optional, Union
import requests

class Actions():
    def __init__(self, instance):
        self.driver = instance.driver
        self.timeout = 10

    def click(self, by_type: By, by_value: str, timeout: Optional[int], retry: Optional[int]) -> None:
        """
        This method executes a click if the element is found within a time range.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
            retry (Optional): After logging the error, attempts X times again to locate the element, every try can generate a new error.
        """

        while True:
            try:
                Wait(self.driver, timeout or self.timeout).until(EC.element_to_be_clickable((by_type, by_value))).click()
                break
            except Exception as e:
                print(e)
                if retry > 0:
                    retry -= 1
                else:
                    break

    def api_post(self, url: str, headers: Optional[dict], payload: dict, verifySSL = True) -> Optional[requests.Response]:
        '''
        Use this method to send a POST request to any API. 
        Arguments:
            url: The url of the API.
            headers: The headers of the request that will be sent.
                the default headers included in the function are:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            payload: The payload it has to be sent to the API.
            verifySSL: If the SSL certificate should be verified.   (Default: True)
        Returns:
            The response of the API if the request was successful.
            None if the request was not successful.
        '''

        try:
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = 'application/json'

            response = requests.post(url, headers=headers, data=payload, verify=verifySSL)
            return response
        except Exception as e:
            print(e)
            return None

    def api_get(self, url: str, headers: Optional[dict], verifySSL = True) -> Optional[requests.Response]:
        '''
        Use this method to send a GET request to any API. 
        Arguments:
            url: The url of the API.
            headers: The headers of the request that will be sent.
                the default headers included in the function are:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            verifySSL: If the SSL certificate should be verified.   (Default: True)
        Returns:
            The response of the API if the request was successful.
            None if the request was not successful.
        '''

        try:
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = 'application/json'

            response = requests.get(url, headers=headers, verify=verifySSL)
            return response
        except Exception as e:
            print(e)
            return None

    def clear_input(self, by_type: By, by_value: str, timeout: Optional[int], retry: Optional[int]) -> None:
    
        """
        This method executes a clear if the element is found within a time range.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
            retry (Optional): After logging the error, attempts X times again to locate the element, every try can generate a new error.
        """
        
        while True:
            try:
                Wait(self.driver, timeout or self.timeout).until(EC.presence_of_element_located((by_type, by_value))).clear()
                break
            except Exception as e:
                print(e)
                if retry > 0:
                    retry -= 1
                else:
                    break

    def send_keys(self, by_type: By, by_value: str, keys_array: list[[str, Keys]], timeout: Optional[int], retry: Optional[int]) -> None:

        """
        This method press the keys in the sent array if the element is found within a time range.

        Arguments:
            by_type: one of the By class constants, you can find them in selenium.webdriver.common.by module.

            by_value: the value of the element to be clicked, for example:
                '//*[@id="element"]' for an element with id='element'
                '//*[@class="element"]' for an element with class='element'

            keys_array: the array of keys to be sent to the element, the keys will send in order. For example:
                ['a', 'b', 'c'] for the keys 'a', 'b' and 'c'.
                you can use selenium.webdriver.common.keys module to get the keys too.

            timeout (Optional): Generates a error if can't locate the element in x seconds. (Standard timeout: 10 seconds).
            retry (Optional): After logging the error, attempts X times again to locate the element, every try can generate a new error.
        """
        
        while True:
            try:
                Wait(self.driver, timeout or self.timeout).until(EC.visibility_of_element_located(locator)((by_type, by_value))).send_keys(', '.join(keys_array))
                break
            except Exception as e:
                print(e)
                if retry > 0:
                    retry -= 1
                else:
                    break

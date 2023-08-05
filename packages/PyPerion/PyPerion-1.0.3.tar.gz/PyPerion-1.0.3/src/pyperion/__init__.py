from requests import post

def obfuscate(
    code: str,
    camouflate: bool=False,
    ultrasafemode: bool=False
):
    url = "https://api.plague.fun"

    headers = {
        'authority': 'api.plague.fun',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://obf.plague.fun',
        'referer': 'https://obf.plague.fun/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36',
    }

    payload = code.removeprefix("\n")

    resp = post(f"{url}?camouflate={str(camouflate).lower()}&ultrasafemode={str(ultrasafemode).lower()}", headers=headers, data=payload)

    if resp.status_code != 200:
        print("ERROR")
        return

    obf_code = resp.text

    return obf_code
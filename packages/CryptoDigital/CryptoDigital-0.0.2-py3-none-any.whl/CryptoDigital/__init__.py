from bs4 import BeautifulSoup
import requests,json
# Developer : @SudoSaeed , © Copyright from this library is prosecuted!
def dolar():
    dr = "https://www.tgju.org/%D9%82%DB%8C%D9%85%D8%AA-%D8%AF%D9%84%D8%A7%D8%B1"
    res = requests.get(dr,timeout=10)
    msoup = BeautifulSoup(res.text ,"html.parser")
    dolar = msoup.find_all("li" ,attrs={"class":"market-details-price"})
    dic_dolar = {"dolar":f"${dolar[0].text}".replace('\nنرخ فعلی :\n','')}
    return dic_dolar
    
def crypto():
    cypo = "https://www.tgju.org/"
    res = requests.get(cypo,timeout=10)
    msoup = BeautifulSoup(res.text ,"html.parser")
    crp = msoup.find_all("td" ,attrs={"class":"market-price"})
    btc = msoup.find_all("td" ,attrs={"data-market-name":"p"})
    crypto_json = {"crypto":{
        "btc":f"${btc[0].text}".replace('\n',''),
        "ethereum":f"${btc[1].text}".replace('\n',''),
        "litecoin":f"${btc[2].text}".replace('\n',''),
        "bitcoin-cash":f"${crp[3].text}".replace('\n',''),
        "tether":f"${crp[4].text}".replace('\n',''),
        "tron":f"${crp[5].text}".replace('\n',''),
        "binance-coin":f"${crp[6].text}".replace('\n',''),
        "stellar":f"${crp[7].text}".replace('\n',''),
        "ripple":f"${crp[8].text}".replace('\n',''),
        "dogecoin":f"${crp[9].text}".replace('\n',''),
        "dash":f"${crp[10].text}".replace('\n',''),
        "cardano":f"${crp[11].text}".replace('\n',''),
        "polkadot":f"${crp[12].text}".replace('\n',''),
        "solana":f"${crp[13].text}".replace('\n',''),
        "avalanche":f"${crp[14].text}".replace('\n',''),
        "Developer":"SudoSaeed",
        "Telegram":"@PySofts"
    }}
    print('For criticisms and suggestions,\ncontact the author of this libraryon Telegram and Instagram :)\ntelegram --> @SudoSaeed\ninstagram --> SudoSaeed\n© Copyright from this library is prosecuted!')
    return json.dumps(crypto_json,indent=2)

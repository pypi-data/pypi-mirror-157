def get(url,where):
    import requests
    print("下载中.........................")
    r = requests.get(url)
    with open(where, "wb") as code:
        code.write(r.content)

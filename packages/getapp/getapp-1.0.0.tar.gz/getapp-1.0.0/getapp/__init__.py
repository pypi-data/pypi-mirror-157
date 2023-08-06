def get(url,where):
    a=int(input("你有requests吗？有填1没有填2！"))
    if a == 1:
        import requests
        print("下载中.........................")
        r = requests.get(url)
        with open(where, "wb") as code:
          code.write(r.content)
    else:
        if a == 2:
            print("你先要在终端执行pip install requests!")

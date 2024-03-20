import requests


def download_file(url, filename, proxy=None):
    # 定义代理字典
    proxies = {"http": proxy, "https": proxy} if proxy else None

    # 发送 GET 请求下载文件
    response = requests.get(url, proxies=proxies)
    print(response.text)
    # 检查响应状态码是否为 200 (成功)
    if response.status_code == 200:
        # 打开文件并写入响应内容
        with open(filename, 'wb') as f:
            f.write(response.content)
        print("文件下载成功！")
    else:
        print("文件下载失败:", response.status_code)


# 定义 JSON 文件的 URL
url = "https://api.raydium.io/v2/sdk/liquidity/mainnet.json"
# 定义本地保存的文件名
filename = "liquidity_mainnet.json"
# 定义代理地址，例如：http://proxy.example.com:8080
proxy = "http://127.0.0.1:10809"

# 调用函数下载文件
download_file(url, filename, proxy)

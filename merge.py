import base64
import json
import urllib.request
import yaml
import codecs
import logging

# 提取节点
def process_urls(url_file, processor):
    try:
        with open(url_file, 'r') as file:
            urls = file.read().splitlines()

        for index, url in enumerate(urls):
            try:
                response = urllib.request.urlopen(url)
                data = response.read().decode('utf-8')
                processor(data, index)
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")
    except Exception as e:
        logging.error(f"Error reading file {url_file}: {e}")
#提取clash节点
def process_clash(data, index):
            # 解析YAML格式的内容
            content = yaml.safe_load(data)

            # 提取proxies部分并合并到merged_proxies中
            proxies = content.get('proxies', [])
            
            for proxy in proxies:
                # 如果类型是reality
                if proxy['type'] == 'vless' :
                    server = proxy['server']
                    port  = proxy['port']
                    udp = proxy['udp']
                    uuid = proxy['uuid']
                    tls = proxy['tls']
                    serverName = proxy['servername']
                    flow = proxy['flow']
                    network = proxy['network']
                    publicKey = proxy['reality-opts']['public-key']
                    fp = proxy['client-fingerprint']
                    reality_meta =  f"vless://{uuid}@{server}:{port}?security=reality&flow={flow}&type={network}&fp={fp}&pbk={publicKey}&sni={serverName}#reality_meta{index}"
                    merged_proxies.append(reality_meta)
                    merged_proxies_neko.append(reality_meta)
                if proxy['type'] == 'vmess' :
                    server = proxy['server']
                    port  = proxy['port']
                    cipher = proxy['cipher']
                    uuid = proxy['uuid']
                    alterId = proxy['alterId']
                    tls = proxy['tls']
                    server_name = proxy['servername']
                    skip_cert_verify = proxy['skip-cert-verify']
                    network = proxy['network']
                    ws_path = proxy['ws-opts']['path']
                    ws_headers_host = proxy['ws-opts']['headers']['host']
                    data = {
                        'add': server,
                        'aid': alterId,
                        'host': ws_headers_host,
                        'id': uuid,
                        'net': network,
                        'path': ws_path,
                        'port': port,
                        'scy': cipher,
                        'sni': server_name,
                        'tls': '',
                        'type': 'none',
                        'v': '2'                        
                    }
                    json_str = json.dumps(data)
                    json_str = base64.b64encode(json_str.encode()).decode()
                    vmess_meta =  f"vmess://{json_str}"
                    merged_proxies.append(vmess_meta)
                    merged_proxies_neko.append(vmess_meta)
                elif proxy['type'] == 'tuic':
                    server = proxy["server"]
                    port = proxy["port"]
                    udp = proxy["udp"]
                    uuid = proxy['uuid']
                    password = proxy['password']
                    alpn = proxy["alpn"][0]
                    #disable_sni = proxy["disable-sni"]
                    udp_relay_mode = proxy['udp-relay-mode']
                    congestion =   proxy['congestion-controller']
                    tuic_meta = f"tuic://{server}:{port}?uuid={uuid}&version=5&password={password}&insecure=1&alpn={alpn}&mode={udp_relay_mode}"
                    merged_proxies.append(tuic_meta)
                    merged_proxies_neko.append(tuic_meta)
                elif proxy['type'] == 'hysteria':
                    server = proxy["server"]           
                    mport = str(proxy["port"])
                    ports = mport.split(",")
                    port = int(ports[0])
                    protocol = proxy["protocol"]
                    # up_mbps = proxy["up"]
                    # down_mbps = proxy["down"]
                    up_mbps = 50
                    down_mbps = 80                   
                    alpn = proxy["alpn"][0]
                    obfs = ""
                    insecure = int(proxy["skip-cert-verify"])
                    server_name = proxy["sni"]
                    fast_open = 1
                    auth = proxy["auth_str"]
                    # 生成URL
                    hysteria_meta = f"hysteria://{server}:{port}?peer={server_name}&auth={auth}&insecure={insecure}&upmbps={up_mbps}&downmbps={down_mbps}&alpn={alpn}&mport={mport}&obfs={obfs}&protocol={protocol}&fastopen={fast_open}#hysteria{index}"
                    merged_proxies.append(hysteria_meta)
                    merged_proxies_neko.append(hysteria_meta)
                elif proxy['type'] == 'ssr':
                    server = proxy["server"]           
                    port = proxy["port"]
                    password = proxy["password"]
                    password = base64.b64encode(password.encode()).decode()
                    cipher = proxy["cipher"]
                    obfs = proxy["obfs"]
                    protocol = proxy["protocol"]

                    # 生成URL
                    ssr_source=f"{server}:{port}:{protocol}:{cipher}:{obfs}:{password}/?remarks=&protoparam=&obfsparam="
                    
                    ssr_source=base64.b64encode(ssr_source.encode()).decode()
                    ssr_meta = f"ssr://{ssr_source}"
                    merged_proxies.append(ssr_meta)

def process_naive(data, index):
    try:
        json_data = json.loads(data)
        # 处理 shadowtls 数据

        proxy_str = json_data["proxy"]
        proxy_str = proxy_str.replace("https://", "")
        # 对 proxy 进行 Base64 编码
        encoded_proxy = base64.b64encode(proxy_str.encode()).decode()
        # 添加前缀
        naiveproxy = "http2://" + encoded_proxy
        naiveproxy_neko = f"naive+https://{proxy_str}"
        merged_proxies.append(naiveproxy)
        merged_proxies_neko.append(naiveproxy_neko)

    except Exception as e:
        logging.error(f"Error processing shadowtls data for index {index}: {e}")

def process_shadowtls(data, index):
    try:
        json_data = json.loads(data)
        # 处理 shadowtls 数据

        server = json_data["outbounds"][1]["server"]
        server_port = json_data["outbounds"][1]["server_port"]
        method = json_data["outbounds"][0]["method"]
        password = json_data["outbounds"][0]["password"]
        version = "1"
        host = json_data["outbounds"][1]["tls"]["server_name"]
        ss = f"{method}:{password}@{server}:{server_port}"
        shadowtls = f'{{"version": "{version}", "host": "{host}"}}'
        shadowtls_proxy = "ss://"+base64.b64encode(ss.encode()).decode()+"?shadow-tls="+base64.b64encode(shadowtls.encode()).decode()+f"#shadowtls{index}"
        
        merged_proxies.append(shadowtls_proxy)

    except Exception as e:
        logging.error(f"Error processing shadowtls data for index {index}: {e}")
#hysteria
def process_hysteria(data, index):
    try:
        json_data = json.loads(data)
        # 处理 hysteria 数据
        # 提取字段值
        server = json_data["server"]
        protocol = json_data["protocol"]
        # up_mbps = json_data["up_mbps"]
        # down_mbps = json_data["down_mbps"]
        up_mbps = 50
        down_mbps = 100
        alpn = json_data["alpn"]
        obfs = json_data["obfs"]
        insecure = int(json_data["insecure"])
        server_name = json_data["server_name"]
        fast_open = int(json_data["fast_open"])
        auth = json_data["auth_str"]
        # 生成URL
        hysteria = f"hysteria://{server}?peer={server_name}&auth={auth}&insecure={insecure}&upmbps={up_mbps}&downmbps={down_mbps}&alpn={alpn}&obfs={obfs}&protocol={protocol}&fastopen={fast_open}#hysteria{index}"
        merged_proxies.append(hysteria)
        merged_proxies_neko.append(hysteria)

    except Exception as e:
        logging.error(f"Error processing hysteria data for index {index}: {e}")
# 处理hysteria2
def process_hysteria2(data, index):
    try:
        json_data = json.loads(data)
        # 处理 hysteria2 数据
        # 提取字段值
        server = json_data["server"]
        insecure = int(json_data["tls"]["insecure"])
        sni = json_data["tls"]["sni"]
        auth = json_data["auth"]
        # 生成URL
        hysteria2 = f"hysteria2://{auth}@{server}?insecure={insecure}&sni={sni}#hysteria2_{index}"
        merged_proxies_neko.append(hysteria2)

    except Exception as e:
        logging.error(f"Error processing hysteria2 data for index {index}: {e}")

#处理xray
def process_xray(data, index):
    try:
        json_data = json.loads(data)
        # 处理 xray 数据
        # 提取所需字段
        protocol = json_data["outbounds"][0]["protocol"]
        server = json_data["outbounds"][0]["settings"]["vnext"][0]["address"]
        port = json_data["outbounds"][0]["settings"]["vnext"][0]["port"]
        uuid = json_data["outbounds"][0]["settings"]["vnext"][0]["users"][0]["id"]
        istls = True
        flow = json_data["outbounds"][0]["settings"]["vnext"][0]["users"][0]["flow"]
        # 传输方式
        network = json_data["outbounds"][0]["streamSettings"]["network"]
        publicKey = json_data["outbounds"][0]["streamSettings"]["realitySettings"]["publicKey"]
        shortId = json_data["outbounds"][0]["streamSettings"]["realitySettings"]["shortId"]
        serverName = json_data["outbounds"][0]["streamSettings"]["realitySettings"]["serverName"]
        fingerprint = json_data["outbounds"][0]["streamSettings"]["realitySettings"]["fingerprint"]
        spx = json_data["outbounds"][0]["streamSettings"]["realitySettings"]["spiderX"]
        # udp转发
        isudp = True
        name = f"reality{index}"
        
        # 根据network判断tcp
        if network == "tcp":
            reality = f"vless://{uuid}@{server}:{port}?security=reality&flow={flow}&type={network}&fp={fingerprint}&pbk={publicKey}&sni={serverName}&spx={spx}&sid={shortId}#REALITY{index}"

        # 根据network判断grpc
        elif network == "grpc":
            serviceName = json_data["outbounds"][0]["streamSettings"]["grpcSettings"]["serviceName"]
            reality = f"vless://{uuid}@{server}:{port}?security=reality&flow={flow}&&type={network}&fp={fingerprint}&pbk={publicKey}&sni={serverName}&spx={spx}&sid={shortId}&serviceName={serviceName}#REALITY{index}"

        # 将当前proxy字典添加到所有proxies列表中
        merged_proxies.append(reality)
        merged_proxies_neko.append(reality)
    except Exception as e:
        logging.error(f"Error processing xray data for index {index}: {e}")

def update_proxy_groups(config_data, merged_proxies):
    for group in config_data['proxy-groups']:
        if group['name'] in ['自动选择', '节点选择']:
            group['proxies'].extend(proxy['name'] for proxy in merged_proxies)

def update_warp_proxy_groups(config_warp_data, merged_proxies):
    for group in config_warp_data['proxy-groups']:
        if group['name'] in ['自动选择', '手动选择', '负载均衡']:
            group['proxies'].extend(proxy['name'] for proxy in merged_proxies)
# 定义一个空列表用于存储合并后的代理配置
merged_proxies = []
merged_proxies_neko = []
# 处理 clash URLs
process_urls('./urls/clash_urls.txt', process_clash)

# 处理 shadowtls URLs
process_urls('./urls/shadowtls_urls.txt', process_shadowtls)

# 处理 naive URLs
process_urls('./urls/naiverproxy_urls.txt', process_naive)

# 处理 hysteria URLs
process_urls('./urls/hysteria_urls.txt', process_hysteria)

# 处理 hysteria2 URLs
process_urls('./urls/hysteria2_urls.txt', process_hysteria2)

# 处理 xray URLs
process_urls('./urls/reality_urls.txt', process_xray)

# 将结果写入文件
try:
    with open("./sub/shadowrocket.txt", "w") as file:
        for proxy in merged_proxies:
            file.write(proxy + "\n")
except Exception as e:
    print(f"Error writing to file: {e}")
# 将结果写入文件
try:
    with open("./sub/neko.txt", "w") as file:
        for proxy in merged_proxies_neko:
            file.write(proxy + "\n")
except Exception as e:
    print(f"Error writing to file: {e}")

try:
    with open("./sub/shadowrocket.txt", "r") as file:
        content = file.read()
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    with open("./sub/shadowrocket_base64.txt", "w") as encoded_file:
        encoded_file.write(encoded_content)
        
    print("Content successfully encoded and written to file.")
except Exception as e:
    print(f"Error encoding file content: {e}")

try:
    with open("./sub/neko.txt", "r") as file:
        content = file.read()
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    with open("./sub/neko_base64.txt", "w") as encoded_file:
        encoded_file.write(encoded_content)
        
    print("Content successfully encoded and written to file.")
except Exception as e:
    print(f"Error encoding file content: {e}")
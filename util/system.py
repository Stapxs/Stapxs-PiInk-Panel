import subprocess
import re

def get_wifi_list(no_cache=False):
    ''''
    获取 Wi-Fi 列表

    Returns:
        List[Dict[str, str]], Wi-Fi 列表
    '''
    try:
        command = ["iwlist", "wlan0", "scan"]
        if no_cache:
            command = ["sudo", "iwlist", "wlan0", "scan"]

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        wifi_list = []

        # 正则匹配信息
        ssid_pattern = re.compile(r'ESSID:"(.*?)"')
        quality_pattern = re.compile(r"Quality=(\d+)/(\d+)")
        signal_pattern = re.compile(r"Signal level=(-?\d+) dBm")
        encryption_pattern = re.compile(r"Encryption key:(\w+)")
        wpa_pattern = re.compile(r"(WPA\d?)\s+Version (\d+)")

        ssids = ssid_pattern.findall(result.stdout)
        qualities = quality_pattern.findall(result.stdout)
        signals = signal_pattern.findall(result.stdout)
        encryptions = encryption_pattern.findall(result.stdout)
        wpa_matches = wpa_pattern.findall(result.stdout)

        for i in range(len(ssids)):
            ssid = ssids[i].strip()
            if not ssid:  # 跳过空白 SSID
                continue

            quality = int(qualities[i][0]) if i < len(qualities) else 0
            max_quality = int(qualities[i][1]) if i < len(qualities) else 100
            signal = int(signals[i]) if i < len(signals) else -100
            encryption = encryptions[i] if i < len(encryptions) else "off"
            is_secure = encryption.lower() == "on"

            # 解析 WPA 版本（用逗号连接）
            wpa_versions = ",".join(set(match[0] for match in wpa_matches)) if wpa_matches else "None"

            wifi_list.append({
                "title": ssid,
                "quality": quality,
                "max_quality": max_quality,
                "signal": signal,
                "password": is_secure,
                "wpa": wpa_versions
            })

        return wifi_list
    except Exception as e:
        print("Error:", e)
        return []
    
def get_connected_wifi():
    '''
    获取已连接的 Wi-Fi 信息

    Returns:
        Dict[str, str], 已连接的 Wi-Fi 信息
    '''
    try:
        result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True, check=True)
        connected_ssid = result.stdout.strip()

        if not connected_ssid:
            return None
        
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True, check=True)
        ip = result.stdout.strip().split(" ")[0]

        return {
            "title": connected_ssid,
            "ip": ip
        }
    except Exception as e:
        print("Error:", e)
        return None
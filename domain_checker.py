import requests
import time
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class DomainChecker:
    def __init__(self):
        self.api_url = "https://v2.xxapi.cn/api/whois"
        self.max_workers = 5  # 最大并发数
        self.delay = 1  # 查询延迟（秒）
        self.available_domains = []
        self.registered_domains = []
        self.error_domains = []
        self.total_domains = 0
        self.completed_domains = 0

    def is_valid_domain(self, domain):
        """验证域名格式是否合法"""
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        return bool(re.match(pattern, domain))

    def check_domain(self, domain):
        """检查单个域名的注册状态"""
        if not self.is_valid_domain(domain):
            print(f"无效的域名格式: {domain}")
            self.error_domains.append(domain)
            return

        try:
            headers = {
                'User-Agent': 'xiaoxiaoapi/1.0.0 (https://xxapi.cn)'
            }
            response = requests.get(f"{self.api_url}?domain={domain}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"API响应数据: {data}")  # 调试日志
                domain_data = data.get('data', {})
                # 通过dns_serve和DNS Serve字段判断域名是否已注册
                if domain_data.get('dns_serve') is None and domain_data.get('DNS Serve') is None:
                    print(f"[可注册] {domain}")
                    self.available_domains.append(domain)
                else:
                    print(f"[已注册] {domain}")
                    self.registered_domains.append(domain)
            else:
                print(f"查询失败: {domain} (HTTP {response.status_code})")
                self.error_domains.append(domain)

            time.sleep(self.delay)  # 添加延迟避免API限制

        except Exception as e:
            print(f"查询出错: {domain} ({str(e)})")
            self.error_domains.append(domain)

    def check_domains_from_file(self, filename, suffix):
        """从文件读取域名前缀并检查"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                prefixes = [line.strip() for line in f if line.strip()]

            domains = [f"{prefix}.{suffix.lstrip('.')}" for prefix in prefixes]
            self.check_domains_batch(domains)

        except FileNotFoundError:
            print(f"文件不存在: {filename}")
        except Exception as e:
            print(f"读取文件出错: {str(e)}")

    def check_domains_batch(self, domains):
        """批量检查域名"""
        self.total_domains = len(domains)
        self.completed_domains = 0
        
        def check_with_progress(domain):
            self.check_domain(domain)
            self.completed_domains += 1
            progress = (self.completed_domains / self.total_domains) * 100
            print(f"\r当前进度: {progress:.1f}% ({self.completed_domains}/{self.total_domains})", end="")
            if self.completed_domains == self.total_domains:
                print()  # 打印换行
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(check_with_progress, domains)

    def save_results(self):
        """保存查询结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"domain_check_results_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== 域名查询结果 ===\n\n")
            
            f.write("--- 可注册的域名 ---\n")
            for domain in self.available_domains:
                f.write(f"{domain}\n")
            
            f.write("\n--- 已注册的域名 ---\n")
            for domain in self.registered_domains:
                f.write(f"{domain}\n")
            
            f.write("\n--- 查询失败的域名 ---\n")
            for domain in self.error_domains:
                f.write(f"{domain}\n")

        print(f"\n结果已保存到文件: {filename}")
        print(f"可注册域名: {len(self.available_domains)}个")
        print(f"已注册域名: {len(self.registered_domains)}个")
        print(f"查询失败: {len(self.error_domains)}个")

def main():
    checker = DomainChecker()
    
    while True:
        print("\n=== 域名批量查询工具 ===")
        print("1. 从文件读取域名前缀")
        print("2. 手动输入域名前缀")
        print("3. 退出")
        
        choice = input("\n请选择操作 (1-3): ").strip()
        
        if choice == '3':
            break
        
        suffix = input("请输入域名后缀（如: com, net, org）: ").strip()
        if not suffix:
            print("域名后缀不能为空！")
            continue
        
        if choice == '1':
            filename = input("请输入文件路径: ").strip()
            checker.check_domains_from_file(filename, suffix)
            
        elif choice == '2':
            print("请输入域名前缀（每行一个，输入空行结束）:")
            prefixes = []
            while True:
                prefix = input().strip()
                if not prefix:
                    break
                prefixes.append(prefix)
            
            if prefixes:
                domains = [f"{prefix}.{suffix.lstrip('.')}" for prefix in prefixes]
                checker.check_domains_batch(domains)
            else:
                print("未输入任何域名前缀！")
                continue
        
        checker.save_results()
        
        # 清空结果列表，准备下一次查询
        checker.available_domains.clear()
        checker.registered_domains.clear()
        checker.error_domains.clear()

if __name__ == "__main__":
    main()
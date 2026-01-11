#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenDiggerCrawler:
    """OpenDigger 数据爬虫"""
    
    BASE_URL = "https://oss.open-digger.cn"
    
    def __init__(self, output_dir: str = "data"):
        """
        初始化爬虫
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OpenDigger-Crawler/1.0'
        })
    
    def build_url(self, platform: str, owner: str, repo: str, metric_file: str) -> str:
        """
        构建数据URL
        
        Args:
            platform: 平台 (github/gitee)
            owner: 仓库所有者或用户名
            repo: 仓库名称（如果是开发者数据，可为空）
            metric_file: 指标文件名
            
        Returns:
            完整的数据URL
        """
        return f"{self.BASE_URL}/{platform}/{owner}/{repo}/{metric_file}"
    
    def fetch_data(self, url: str, timeout: int = 10) -> Optional[Dict]:
        """
        获取数据
        
        Args:
            url: 数据URL
            timeout: 请求超时时间
            
        Returns:
            数据字典，获取失败返回None
        """
        try:
            logger.info(f"正在获取: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取数据失败 {url}: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"JSON 解析失败 {url}")
            return None
    
    def save_data(self, data: Dict, filename: str, subdir: str = "") -> bool:
        """
        保存数据到文件
        
        Args:
            data: 数据字典
            filename: 文件名
            subdir: 子目录名
            
        Returns:
            保存成功返回True
        """
        try:
            if subdir:
                save_dir = self.output_dir / subdir
                save_dir.mkdir(parents=True, exist_ok=True)
            else:
                save_dir = self.output_dir
            
            file_path = save_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存数据失败 {filename}: {e}")
            return False
    
    def fetch_repository_metrics(self, platform: str, owner: str, repo: str, 
                                  metrics: List[str]) -> Dict[str, Dict]:
        """
        获取仓库指标数据
        
        Args:
            platform: 平台 (github/gitee)
            owner: 仓库所有者
            repo: 仓库名称
            metrics: 指标文件列表
            
        Returns:
            指标数据字典
        """
        results = {}
        subdir = f"{platform}/{owner}/{repo}"
        
        for metric_file in metrics:
            if metric_file == "-":
                continue
            url = self.build_url(platform, owner, repo, metric_file)
            data = self.fetch_data(url)
            if data:
                results[metric_file] = data
                self.save_data(data, metric_file, subdir)
        
        return results
    
    def fetch_developer_metrics(self, platform: str, login: str, 
                                metrics: List[str]) -> Dict[str, Dict]:
        """
        获取开发者指标数据
        
        Args:
            platform: 平台 (github/gitee)
            login: 用户名
            metrics: 指标文件列表
            
        Returns:
            指标数据字典
        """
        results = {}
        subdir = f"{platform}/users/{login}"
        
        for metric_file in metrics:
            if metric_file == "-":
                continue
            # 开发者数据URL格式可能需要特殊处理
            url = f"{self.BASE_URL}/{platform}/users/{login}/{metric_file}"
            data = self.fetch_data(url)
            if data:
                results[metric_file] = data
                self.save_data(data, metric_file, subdir)
        
        return results
    
    def load_metrics_config(self, config_file: str = "metrics_data.json") -> Dict:
        """
        加载指标配置
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            指标配置字典
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {config_file}")
            return {}
    
    def fetch_all_metrics(self, platform: str, owner: str, repo: str) -> Dict:
        """
        获取仓库的所有指标
        
        Args:
            platform: 平台 (github/gitee)
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            所有指标数据
        """
        metrics_config = self.load_metrics_config()
        all_data = {}
        
        for category, metrics_list in metrics_config.items():
            logger.info(f"正在获取 {category} 类别的数据...")
            for metric_info in metrics_list:
                metric_name = metric_info.get('name', '')
                examples = metric_info.get('examples') or [metric_info.get('example', '')]
                
                for example_file in examples:
                    if example_file and example_file != "-":
                        url = self.build_url(platform, owner, repo, example_file)
                        data = self.fetch_data(url)
                        if data:
                            key = f"{category}/{metric_name}/{example_file}"
                            all_data[key] = data
                            self.save_data(
                                data,
                                example_file,
                                f"{platform}/{owner}/{repo}/{category}"
                            )
        
        return all_data


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenDigger 数据爬虫')
    parser.add_argument('--platform', default='github', 
                       choices=['github', 'gitee'],
                       help='平台名称')
    parser.add_argument('--owner', required=True, help='仓库所有者或用户名')
    parser.add_argument('--repo', required=True, help='仓库名称')
    parser.add_argument('--output', default='data', help='输出目录')
    
    args = parser.parse_args()
    
    crawler = OpenDiggerCrawler(output_dir=args.output)
    logger.info(f"开始爬取数据: {args.platform}/{args.owner}/{args.repo}")
    
    results = crawler.fetch_all_metrics(args.platform, args.owner, args.repo)
    
    logger.info(f"爬取完成，共获取 {len(results)} 个数据文件")
    logger.info(f"数据已保存到 {crawler.output_dir}")


if __name__ == '__main__':
    main()

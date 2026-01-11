#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenDigger 数据爬虫使用示例
"""

from crawler import OpenDiggerCrawler
import json

def example_fetch_github_repo():
    """示例：获取GitHub仓库数据"""
    print("=" * 60)
    print("示例 1: 获取 GitHub 仓库数据")
    print("=" * 60)
    
    crawler = OpenDiggerCrawler(output_dir=r"D:\HuaweiMoveData\Users\32002\Desktop\opendigger_data\example1")
    
    # 获取特定仓库的指标
    platform = "github"
    owner = "torvalds"
    repo = "linux"
    
    print(f"\n爬取仓库: {platform}/{owner}/{repo}")
    
    # 获取 OpenRank 数据
    openrank_url = crawler.build_url(platform, owner, repo, "openrank.json")
    openrank_data = crawler.fetch_data(openrank_url)
    if openrank_data:
        crawler.save_data(openrank_data, "openrank.json", f"{owner}/{repo}")
        print(f"✓ 获取 OpenRank 数据成功")
    
    # 获取活跃度数据
    activity_url = crawler.build_url(platform, owner, repo, "activity.json")
    activity_data = crawler.fetch_data(activity_url)
    if activity_data:
        crawler.save_data(activity_data, "activity.json", f"{owner}/{repo}")
        print(f"✓ 获取活跃度数据成功")
    
    # 获取星标数据
    stars_url = crawler.build_url(platform, owner, repo, "stars.json")
    stars_data = crawler.fetch_data(stars_url)
    if stars_data:
        crawler.save_data(stars_data, "stars.json", f"{owner}/{repo}")
        print(f"✓ 获取星标数据成功")


def example_fetch_multiple_repos():
    """示例：批量获取多个仓库的数据"""
    print("\n" + "=" * 60)
    print("示例 2: 批量获取多个仓库的关键指标")
    print("=" * 60)
    
    crawler = OpenDiggerCrawler(output_dir=r"D:\HuaweiMoveData\Users\32002\Desktop\opendigger_data\example2")
    
    repos = [
        ("github", "keras-team", "keras"),
        ("github", "pallets", "flask"),
        ("github", "django", "django"),
    ]
    
    metrics = [
        "openrank.json",
        "activity.json",
        "stars.json",
    ]
    
    for platform, owner, repo in repos:
        print(f"\n爬取: {platform}/{owner}/{repo}")
        results = crawler.fetch_repository_metrics(platform, owner, repo, metrics)
        print(f"  获取了 {len(results)} 个指标")


def example_fetch_all_metrics():
    """示例：获取仓库的所有指标"""
    print("\n" + "=" * 60)
    print("示例 3: 获取仓库的所有可用指标")
    print("=" * 60)
    
    crawler = OpenDiggerCrawler(output_dir=r"D:\HuaweiMoveData\Users\32002\Desktop\opendigger_data\example3")
    
    platform = "github"
    owner = "kubernetes"
    repo = "kubernetes"
    
    print(f"\n爬取: {platform}/{owner}/{repo}")
    results = crawler.fetch_all_metrics(platform, owner, repo)
    print(f"✓ 成功获取 {len(results)} 个指标数据文件")


def example_batch_developers():
    """示例：获取开发者数据"""
    print("\n" + "=" * 60)
    print("示例 4: 获取开发者指标数据")
    print("=" * 60)
    
    crawler = OpenDiggerCrawler(output_dir=r"D:\HuaweiMoveData\Users\32002\Desktop\opendigger_data\example4")
    
    platform = "github"
    login = "torvalds"
    
    metrics = [
        "activity.json",
        "participants.json",
    ]
    
    print(f"\n爬取开发者: {platform}/{login}")
    results = crawler.fetch_developer_metrics(platform, login, metrics)
    print(f"✓ 获取了 {len(results)} 个开发者指标")


if __name__ == '__main__':
    # 运行示例
    try:
        example_fetch_github_repo()
        example_fetch_multiple_repos()
        example_fetch_all_metrics()
        example_batch_developers()
        
        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        print("\n查看数据文件夹获取爬取的数据")
        
    except Exception as e:
        print(f"执行出错: {e}")
        import traceback
        traceback.print_exc()

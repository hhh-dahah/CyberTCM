#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CyberTCM 数据管理工具
用于管理和导出数据库中的数据
"""

import database
import pandas as pd
from datetime import datetime
import sys

def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🧬 CyberTCM 数据管理工具")
    print("="*50)
    print("1. 📊 查看数据统计")
    print("2. 👥 查看所有用户")
    print("3. 📝 查看所有问卷")
    print("4. 🔍 搜索问卷")
    print("5. 📄 导出为 CSV")
    print("6. 📊 导出为 Excel")
    print("7. 🗄️  查看数据库信息")
    print("0. 🚪 退出")
    print("="*50)

def show_statistics():
    """显示数据统计"""
    print("\n📊 数据统计概览")
    print("-" * 30)
    
    stats = database.get_statistics()
    
    print(f"👥 总用户数: {stats['total_users']}")
    print(f"📝 总问卷数: {stats['total_questionnaires']}")
    print(f"📅 今日新增: {stats['today_count']}")
    
    if stats['type_distribution']:
        print("\n🧬 体质类型分布:")
        for item in stats['type_distribution']:
            print(f"  {item['type_code']} - {item['type_name']}: {item['count']} 人")

def show_all_users():
    """显示所有用户"""
    print("\n👥 所有用户列表")
    print("-" * 50)
    
    users = database.get_all_users()
    
    if not users:
        print("暂无用户数据")
        return
    
    print(f"{'ID':<5} {'昵称':<20} {'问卷数':<8} {'创建时间'}")
    print("-" * 50)
    
    for user in users:
        print(f"{user['id']:<5} {user['nickname']:<20} {user['questionnaire_count']:<8} {user['created_at']}")

def show_all_questionnaires():
    """显示所有问卷"""
    print("\n📝 所有问卷记录")
    print("-" * 70)
    
    questionnaires = database.get_all_questionnaires()
    
    if not questionnaires:
        print("暂无问卷数据")
        return
    
    print(f"{'ID':<5} {'用户':<15} {'体质代码':<10} {'体质名称':<15} {'提交时间'}")
    print("-" * 70)
    
    for q in questionnaires:
        print(f"{q['id']:<5} {q['nickname']:<15} {q['type_code']:<10} {q['type_name']:<15} {q['created_at']}")

def search_questionnaires():
    """搜索问卷"""
    print("\n🔍 搜索问卷")
    print("-" * 30)
    
    nickname = input("输入用户昵称（留空表示不筛选）: ").strip()
    type_code = input("输入体质代码（留空表示不筛选）: ").strip()
    start_date = input("输入开始日期 (YYYY-MM-DD，留空表示不筛选）: ").strip()
    end_date = input("输入结束日期 (YYYY-MM-DD，留空表示不筛选）: ").strip()
    
    # 转换空字符串为None
    nickname = nickname if nickname else None
    type_code = type_code if type_code else None
    start_date = start_date if start_date else None
    end_date = end_date if end_date else None
    
    results = database.search_questionnaires(nickname, type_code, start_date, end_date)
    
    print(f"\n找到 {len(results)} 条记录:")
    print("-" * 70)
    
    if results:
        print(f"{'ID':<5} {'用户':<15} {'体质代码':<10} {'体质名称':<15} {'提交时间'}")
        print("-" * 70)
        
        for q in results:
            print(f"{q['id']:<5} {q['nickname']:<15} {q['type_code']:<10} {q['type_name']:<15} {q['created_at']}")
    else:
        print("未找到匹配的记录")

def export_to_csv():
    """导出为CSV"""
    print("\n📄 导出为 CSV")
    print("-" * 30)
    
    filename = input("输入文件名（默认: cybertcm_export.csv）: ").strip()
    if not filename:
        filename = 'cybertcm_export.csv'
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    try:
        result = database.export_to_csv(filename)
        print(f"✅ 数据已成功导出到: {result}")
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def export_to_excel():
    """导出为Excel"""
    print("\n📊 导出为 Excel")
    print("-" * 30)
    
    filename = input("输入文件名（默认: cybertcm_export.xlsx）: ").strip()
    if not filename:
        filename = 'cybertcm_export.xlsx'
    
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    try:
        result = database.export_to_excel(filename)
        if result:
            print(f"✅ 数据已成功导出到: {result}")
        else:
            print("❌ 导出失败，请确保已安装 pandas 和 openpyxl")
            print("💡 提示: pip install pandas openpyxl")
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def show_database_info():
    """显示数据库信息"""
    print("\n🗄️  数据库信息")
    print("-" * 30)
    
    db_info = database.get_database_info()
    
    if db_info:
        print(f"数据库文件: {db_info['file_path']}")
        print(f"文件大小: {db_info['file_size']}")
        print(f"数据表: {', '.join(db_info['tables'])}")
    else:
        print("数据库文件不存在")

def main():
    """主函数"""
    # 初始化数据库
    database.init_db()
    
    print("🧬 CyberTCM 数据管理工具已启动")
    
    while True:
        show_menu()
        choice = input("\n请选择操作 (0-7): ").strip()
        
        if choice == '1':
            show_statistics()
        elif choice == '2':
            show_all_users()
        elif choice == '3':
            show_all_questionnaires()
        elif choice == '4':
            search_questionnaires()
        elif choice == '5':
            export_to_csv()
        elif choice == '6':
            export_to_excel()
        elif choice == '7':
            show_database_info()
        elif choice == '0':
            print("\n👋 感谢使用，再见！")
            break
        else:
            print("\n❌ 无效的选择，请重新输入")

if __name__ == "__main__":
    main()

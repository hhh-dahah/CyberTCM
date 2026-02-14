#!/usr/bin/env python3
# 数据库测试脚本

import database
import sqlite3

def test_init_db():
    """
    测试数据库初始化
    """
    print("=== 测试数据库初始化 ===")
    try:
        database.init_db()
        print("✅ 数据库初始化成功")
        
        # 检查表结构
        conn = sqlite3.connect('cybertcm.db')
        c = conn.cursor()
        
        # 检查表是否存在
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if c.fetchone():
            print("✅ users表存在")
        else:
            print("❌ users表不存在")
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questionnaires'")
        if c.fetchone():
            print("✅ questionnaires表存在")
        else:
            print("❌ questionnaires表不存在")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def test_user_creation():
    """
    测试用户创建
    """
    print("\n=== 测试用户创建 ===")
    try:
        # 测试创建新用户
        user_id1 = database.get_or_create_user("测试用户1")
        print(f"✅ 创建用户 '测试用户1'，ID: {user_id1}")
        
        # 测试获取已存在用户
        user_id2 = database.get_or_create_user("测试用户1")
        print(f"✅ 获取用户 '测试用户1'，ID: {user_id2}")
        
        if user_id1 == user_id2:
            print("✅ 用户ID一致，说明成功获取已存在用户")
        else:
            print("❌ 用户ID不一致，说明重复创建了用户")
        
        # 测试创建多个用户
        user_id3 = database.get_or_create_user("测试用户2")
        print(f"✅ 创建用户 '测试用户2'，ID: {user_id3}")
        
        return True
    except Exception as e:
        print(f"❌ 用户创建失败: {e}")
        return False

def test_database_connection():
    """
    测试数据库连接
    """
    print("\n=== 测试数据库连接 ===")
    try:
        conn = sqlite3.connect('cybertcm.db')
        c = conn.cursor()
        
        # 测试查询
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        print(f"✅ 数据库连接成功，当前用户数: {count}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    print("开始数据库测试...\n")
    
    success = True
    success &= test_init_db()
    success &= test_user_creation()
    success &= test_database_connection()
    
    print("\n=== 测试结果 ===")
    if success:
        print("🎉 所有测试通过！数据库功能正常")
    else:
        print("💥 部分测试失败，请检查错误信息")

#!/usr/bin/env python3
# 问卷数据存储测试脚本

import database
import sqlite3
import json

def test_questionnaire_storage():
    """
    测试问卷数据存储
    """
    print("=== 测试问卷数据存储 ===")
    try:
        # 获取或创建测试用户
        user_id = database.get_or_create_user("测试用户")
        print(f"✅ 获取用户，ID: {user_id}")
        
        # 模拟问卷数据
        test_data = {
            "type_code": "CVDQ",
            "type_name": "听风者",
            "radar_data": {
                "cold": 60,
                "heat": 40,
                "void": 70,
                "solid": 30,
                "dry": 50,
                "wet": 50,
                "qi": 60,
                "blood": 40
            },
            "energy_data": [
                {"label": "温度", "left": "❄️ 寒", "right": "🔥 热", "val": -20},
                {"label": "能量", "left": "☁️ 虚", "right": "💎 实", "val": -40},
                {"label": "环境", "left": "🌵 燥", "right": "💧 湿", "val": 0},
                {"label": "通畅", "left": "🌀 郁", "right": "🩸 瘀", "val": -20}
            ],
            "answers": {
                "q_1": "A. 非常符合 (5分)",
                "q_2": "B. 比较符合 (4分)",
                "q_3": "C. 一般 (3分)"
            }
        }
        
        # 存储问卷数据
        database.save_questionnaire(
            user_id=user_id,
            type_code=test_data["type_code"],
            type_name=test_data["type_name"],
            radar_data=test_data["radar_data"],
            energy_data=test_data["energy_data"],
            answers=test_data["answers"]
        )
        print("✅ 问卷数据存储成功")
        
        # 验证数据是否存储成功
        conn = sqlite3.connect('cybertcm.db')
        c = conn.cursor()
        
        # 查询问卷数据
        c.execute("SELECT COUNT(*) FROM questionnaires WHERE user_id = ?", (user_id,))
        count = c.fetchone()[0]
        print(f"✅ 该用户的问卷数量: {count}")
        
        if count > 0:
            # 查询最新的问卷数据
            c.execute("SELECT * FROM questionnaires WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
            row = c.fetchone()
            
            if row:
                print(f"✅ 问卷ID: {row[0]}")
                print(f"✅ 体质类型: {row[2]} - {row[3]}")
                
                # 验证数据完整性
                radar_data = json.loads(row[4])
                energy_data = json.loads(row[5])
                answers = json.loads(row[6])
                
                print("✅ 雷达数据: 已存储")
                print("✅ 能量数据: 已存储")
                print("✅ 答案数据: 已存储")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 问卷数据存储失败: {e}")
        return False

def test_user_questionnaires():
    """
    测试获取用户问卷历史
    """
    print("\n=== 测试获取用户问卷历史 ===")
    try:
        # 获取测试用户
        user_id = database.get_or_create_user("测试用户")
        
        # 获取用户问卷历史
        questionnaires = database.get_user_questionnaires(user_id)
        print(f"✅ 获取到 {len(questionnaires)} 份问卷历史")
        
        for q in questionnaires:
            print(f"  - ID: {q['id']}, 类型: {q['type_code']} - {q['type_name']}, 创建时间: {q['created_at']}")
        
        return True
    except Exception as e:
        print(f"❌ 获取问卷历史失败: {e}")
        return False

if __name__ == "__main__":
    print("开始问卷数据存储测试...\n")
    
    success = True
    success &= test_questionnaire_storage()
    success &= test_user_questionnaires()
    
    print("\n=== 测试结果 ===")
    if success:
        print("🎉 所有测试通过！问卷数据存储功能正常")
    else:
        print("💥 部分测试失败，请检查错误信息")

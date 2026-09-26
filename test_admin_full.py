"""完整测试管理员功能"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def test_login():
    """测试登录"""
    print("\n=== [1] 测试登录 ===")
    resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username": ADMIN_USER,
        "password": ADMIN_PASS
    })
    data = resp.json()
    if resp.status_code == 200 and data.get("code") == 200:
        token = data["data"]["access_token"]
        print(f"✓ 登录成功，获取 token")
        return token
    else:
        print(f"✗ 登录失败: {data}")
        sys.exit(1)

def test_dashboard(token):
    """测试仪表盘"""
    print("\n=== [2] 测试仪表盘统计 ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/v1/admin/dashboard/summary", headers=headers)
    data = resp.json()
    if resp.status_code == 200 and data.get("code") == 200:
        d = data["data"]
        print(f"✓ 仪表盘数据:")
        print(f"  - 总用户数: {d['total_users']} (不含管理员)")
        print(f"  - 总植物数: {d['total_plants']}")
        print(f"  - 总提醒数: {d['total_reminders']}")
        print(f"  - 活跃管理员: {d['active_admins']}")
        return True
    else:
        print(f"✗ 仪表盘失败: {data}")
        return False

def test_user_list(token):
    """测试用户列表"""
    print("\n=== [3] 测试用户列表 ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/v1/admin/users?page=1&page_size=10", headers=headers)
    data = resp.json()
    if resp.status_code == 200 and data.get("code") == 200:
        users = data["data"]["items"]
        print(f"✓ 用户列表 ({data['data']['total']} 个用户):")
        for u in users:
            print(f"  - ID:{u['id']} {u['username']} ({u['role']})")
        return True
    else:
        print(f"✗ 用户列表失败: {data}")
        return False

def test_plant_list(token):
    """测试植物列表"""
    print("\n=== [4] 测试植物列表 ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/v1/plants?page=1&page_size=10", headers=headers)
    data = resp.json()
    if resp.status_code == 200 and data.get("code") == 200:
        plants = data["data"]["items"]
        print(f"✓ 植物列表 ({data['data']['total']} 个植物):")
        for p in plants[:5]:
            print(f"  - ID:{p['id']} {p.get('nickname', p.get('plant_name', 'N/A'))}")
        return True
    else:
        print(f"✗ 植物列表失败: {data}")
        return False

def test_reminder_list(token):
    """测试提醒列表"""
    print("\n=== [5] 测试提醒列表 ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/v1/reminders", headers=headers)
    data = resp.json()
    if resp.status_code == 200 and data.get("code") == 200:
        reminders = data["data"]["items"]
        print(f"✓ 提醒列表 ({len(reminders)} 个提醒):")
        for r in reminders[:5]:
            print(f"  - ID:{r['id']} {r.get('plant_nickname', '无昵称')} (类型:{r.get('remind_type', 'N/A')})")
        return True
    else:
        print(f"✗ 提醒列表失败: {data}")
        return False

def test_unauthorized(token):
    """测试未授权访问"""
    print("\n=== [6] 测试未授权访问 ===")
    bad_token = "invalid_token_12345"
    headers = {"Authorization": f"Bearer {bad_token}"}
    resp = requests.get(f"{BASE_URL}/api/v1/admin/dashboard/summary", headers=headers)
    if resp.status_code == 401:
        print(f"✓ 未授权访问被正确拒绝 (401)")
        return True
    else:
        print(f"✗ 未授权访问测试失败: 返回 {resp.status_code}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("管理员功能完整测试")
    print("=" * 50)
    
    # 登录获取 token
    token = test_login()
    
    # 测试各个端点
    results = []
    results.append(("仪表盘", test_dashboard(token)))
    results.append(("用户列表", test_user_list(token)))
    results.append(("植物列表", test_plant_list(token)))
    results.append(("提醒列表", test_reminder_list(token)))
    results.append(("未授权测试", test_unauthorized(token)))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败")
        sys.exit(1)

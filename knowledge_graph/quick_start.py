#!/usr/bin/env python3
"""
知识图谱快速构建脚本
自动检查配置并导入数据到 Neo4j
"""
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from build_knowledge_graph import PlantKnowledgeGraph


def quick_start():
    """快速启动向导"""
    print("\n" + "=" * 70)
    print("🌿 植物知识图谱快速构建工具")
    print("=" * 70)
    
    # 检查配置文件
    print("\n【步骤 1】检查配置...")
    
    # Neo4j 连接配置（请根据实际情况修改）
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = input("请输入 Neo4j 密码: ").strip()
    NEO4J_DATABASE = "neo4j"
    
    if not NEO4J_PASSWORD:
        print("✗ 密码不能为空")
        return False
    
    # 检查 information 文件
    script_dir = Path(__file__).parent.parent
    info_file = script_dir / "information"
    
    if not info_file.exists():
        print(f"✗ 找不到 information 文件: {info_file}")
        return False
    
    print(f"✓ 找到 information 文件")
    
    # 询问是否清空数据库
    print("\n【步骤 2】数据库操作...")
    clear_db = input("是否清空现有数据？(y/n，默认 n): ").strip().lower()
    
    # 创建知识图谱管理器
    try:
        kg = PlantKnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    except Exception as e:
        print(f"✗ 连接 Neo4j 失败: {e}")
        print("\n提示：")
        print("1. 确保 Neo4j 服务已启动")
        print("2. 检查密码是否正确")
        print("3. 检查端口 7687 是否可访问")
        return False
    
    try:
        # 清空数据库（如果用户选择）
        if clear_db == 'y':
            print("\n正在清空数据库...")
            kg.clear_database()
            print("✓ 数据库已清空")
        
        # 创建约束和索引
        print("\n【步骤 3】创建约束和索引...")
        kg.create_constraints_and_indexes()
        
        # 解析数据
        print("\n【步骤 4】解析数据...")
        plants = kg.parse_information_file(str(info_file))
        
        if not plants:
            print("✗ 没有解析到任何植物数据")
            kg.close()
            return False
        
        # 导入数据
        print("\n【步骤 5】导入数据到 Neo4j...")
        kg.import_plants(plants)
        
        # 显示统计信息
        print("\n【步骤 6】生成统计报告...")
        stats = kg.get_statistics()
        
        print("\n" + "=" * 70)
        print("📊 知识图谱统计信息")
        print("=" * 70)
        print(f"  🌱 植物节点:     {stats['plants']:>5} 个")
        print(f"  🌳 科节点:       {stats['families']:>5} 个")
        print(f"  🌿 属节点:       {stats['genera']:>5} 个")
        print(f"  🦠 病害节点:     {stats['diseases']:>5} 个")
        print(f"  🐛 虫害节点:     {stats['pests']:>5} 个")
        print(f"  ───────────────────────")
        print(f"  🔗 属于科关系:   {stats['belongs_to_family_rels']:>5} 条")
        print(f"  🔗 属于属关系:   {stats['belongs_to_genus_rels']:>5} 条")
        print(f"  🔗 患有病害关系: {stats['has_disease_rels']:>5} 条")
        print(f"  🔗 患有虫害关系: {stats['has_pest_rels']:>5} 条")
        print("=" * 70)
        
        print("\n✅ 知识图谱构建成功！")
        print("\n下一步：")
        print("1. 运行测试脚本验证功能:")
        print("   python test_knowledge_graph.py")
        print("\n2. 在 Neo4j Browser 中查看图谱:")
        print("   http://localhost:7474")
        print("\n3. 启动后端服务使用知识图谱:")
        print("   cd backend && python app/main.py")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 构建过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        kg.close()


if __name__ == "__main__":
    try:
        success = quick_start()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

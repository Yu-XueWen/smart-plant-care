"""
数据库迁移脚本：为remind_config表添加养护提醒字段
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/plant_care")

def run_migration():
    """执行数据库迁移"""
    print("开始执行数据库迁移...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        check_columns = text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'remind_config'
            AND COLUMN_NAME IN ('product_name', 'dosage', 'application_date', 'notes')
        """)
        
        result = conn.execute(check_columns)
        existing_columns = [row[0] for row in result]
        
        print(f"已存在的字段: {existing_columns}")
        
        # 添加 product_name 字段
        if 'product_name' not in existing_columns:
            print("添加 product_name 字段...")
            conn.execute(text("""
                ALTER TABLE remind_config 
                ADD COLUMN product_name VARCHAR(100) COMMENT '产品/药品名称'
            """))
        
        # 添加 dosage 字段
        if 'dosage' not in existing_columns:
            print("添加 dosage 字段...")
            conn.execute(text("""
                ALTER TABLE remind_config 
                ADD COLUMN dosage VARCHAR(50) COMMENT '用量'
            """))
        
        # 添加 application_date 字段
        if 'application_date' not in existing_columns:
            print("添加 application_date 字段...")
            conn.execute(text("""
                ALTER TABLE remind_config 
                ADD COLUMN application_date DATE COMMENT '应用日期（施肥/施药/修剪日期）'
            """))
        
        # 添加 notes 字段
        if 'notes' not in existing_columns:
            print("添加 notes 字段...")
            conn.execute(text("""
                ALTER TABLE remind_config 
                ADD COLUMN notes TEXT COMMENT '备注'
            """))
        
        conn.commit()
    
    print("数据库迁移完成！")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"迁移失败: {e}")
        raise

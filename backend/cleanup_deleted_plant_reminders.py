"""
清理已删除植物关联的提醒
将status=0的植物关联的提醒禁用
"""
from app.api.core.database import SessionLocal
from app.api.models.reminder import RemindConfig
from app.api.models.plant import UserPlant
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_deleted_plant_reminders():
    """清理已删除植物的提醒"""
    db = SessionLocal()
    
    try:
        # 查找所有status=0的植物
        deleted_plants = db.query(UserPlant).filter(
            UserPlant.status == 0
        ).all()
        
        logger.info(f"找到 {len(deleted_plants)} 个已删除的植物")
        
        # 禁用这些植物的所有提醒
        for plant in deleted_plants:
            reminders = db.query(RemindConfig).filter(
                RemindConfig.user_plant_id == plant.id,
                RemindConfig.is_enabled == True
            ).all()
            
            if reminders:
                logger.info(f"植物 '{plant.plant_name}' (ID: {plant.id}) 有 {len(reminders)} 个启用的提醒")
                
                for reminder in reminders:
                    reminder.is_enabled = False
                    logger.info(f"  - 禁用提醒 ID: {reminder.id}, 类型: {reminder.remind_type}")
        
        db.commit()
        logger.info("清理完成！")
        
    except Exception as e:
        logger.error(f"清理失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_deleted_plant_reminders()

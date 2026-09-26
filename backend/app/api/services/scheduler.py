"""
提醒定时任务调度器
定期检查到期的提醒并发送通知
"""
import logging
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.api.core.database import SessionLocal
from app.api.models.reminder import RemindConfig
from app.api.models.plant import UserPlant

logger = logging.getLogger(__name__)

# 全局调度器实例（供外部触发即时检查）
scheduler = None


def check_and_send_reminders():
    """
    检查并发送到期提醒
    这个函数会被定时任务定期调用
    """
    logger.info("=" * 60)
    logger.info("开始检查到期提醒...")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        today = date.today()
        logger.info(f"当前日期: {today}")
        
        # 查询所有到期且启用的提醒
        due_reminders = db.query(RemindConfig).filter(
            RemindConfig.is_enabled == True,
            RemindConfig.scheduled_date <= today
        ).all()
        
        logger.info(f"找到 {len(due_reminders)} 个到期提醒")
        
        if len(due_reminders) == 0:
            logger.info("没有找到到期的提醒")
        
        for reminder in due_reminders:
            try:
                logger.info(f"\n处理提醒 ID={reminder.id}:")
                logger.info(f"  - 类型: {reminder.remind_type}")
                logger.info(f"  - 计划日期: {reminder.scheduled_date}")
                logger.info(f"  - 植物ID: {reminder.user_plant_id}")
                logger.info(f"  - 是否启用: {reminder.is_enabled}")
                logger.info(f"  - 重复间隔: {reminder.repeat_interval}天")
                
                # 获取植物信息
                plant = None
                if reminder.user_plant_id:
                    plant = db.query(UserPlant).filter(
                        UserPlant.id == reminder.user_plant_id,
                        UserPlant.status == 1  # 只处理活跃植物
                    ).first()
                    
                    if plant:
                        logger.info(f"  - 植物名称: {plant.plant_name}")
                        logger.info(f"  - 植物昵称: {plant.nickname}")
                        logger.info(f"  - 植物状态: {plant.status}")
                
                # 如果植物已删除，跳过并禁用提醒
                if not plant:
                    logger.warning(f"⚠️ 提醒ID {reminder.id} 关联的植物不存在或已删除，自动禁用")
                    reminder.is_enabled = False
                    db.commit()
                    continue
                
                plant_name = plant.nickname or plant.plant_name
                
                # 构建提醒消息
                message = build_reminder_message(reminder, plant_name)
                
                logger.info(f"✅ 📢 发送提醒: ID={reminder.id}, 用户={reminder.user_id}, 植物={plant_name}, 类型={reminder.remind_type}, 消息={message}")
                
                # TODO: 这里可以集成实际的通知方式
                # 1. WebSocket 推送（实时通知）
                # 2. 邮件通知
                # 3. 短信通知
                # 4. 移动端推送
                
                # 更新下次提醒日期（关键修复：防止重复触发）
                if reminder.repeat_interval and reminder.repeat_interval > 0:
                    # 周期性提醒：计算下一次日期
                    # 从 scheduled_date 开始累加，直到超过今天
                    next_date = reminder.scheduled_date
                    while next_date <= today:
                        next_date = next_date + timedelta(days=reminder.repeat_interval)
                    reminder.scheduled_date = next_date
                    logger.info(f"  🔄 周期性提醒，下次日期更新为: {next_date}")
                else:
                    # 一次性提醒：处理完成后自动禁用
                    reminder.is_enabled = False
                    logger.info(f"  🏁 一次性提醒，已自动禁用")
                
                db.commit()
                
            except Exception as e:
                logger.error(f"❌ 处理提醒 {reminder.id} 时出错: {e}", exc_info=True)
                db.rollback()
        
        logger.info("\n" + "=" * 60)
        logger.info("提醒检查完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 检查提醒时发生错误: {e}", exc_info=True)
    finally:
        db.close()


def trigger_immediate_check():
    """
    立即触发一次提醒检查（供 API 端点创建提醒后调用）
    使用线程池异步执行，不阻塞主请求
    """
    import threading
    thread = threading.Thread(target=check_and_send_reminders, daemon=True)
    thread.start()
    logger.info("⚡ 已触发即时提醒检查")


def build_reminder_message(reminder: RemindConfig, plant_name: str) -> str:
    """
    构建提醒消息
    
    Args:
        reminder: 提醒配置
        plant_name: 植物名称
        
    Returns:
        提醒消息文本
    """
    type_messages = {
        'water': f'💧 该给 {plant_name} 浇水啦！',
        'fertilize': f'🌱 该给 {plant_name} 施肥了！',
        'pesticide': f'🛡️ 该给 {plant_name} 进行病虫害防治了！',
        'prune': f'✂️ 该给 {plant_name} 修剪了！',
        'other': f'📋 {plant_name} 有新的养护任务！'
    }
    
    # 优先使用自定义消息
    if reminder.custom_message:
        return reminder.custom_message
    
    return type_messages.get(reminder.remind_type, f'📋 {plant_name} 有新的养护任务！')


def start_scheduler():
    """
    启动定时任务调度器
    """
    global scheduler
    scheduler = BackgroundScheduler(
        timezone='Asia/Shanghai',  # 使用中国时区
        job_defaults={
            'coalesce': True,       # 合并错过的任务（避免积压）
            'max_instances': 1,     # 同一任务最多同时运行1个实例
            'misfire_grace_time': 300  # 错过5分钟内的任务仍会执行
        }
    )
    
    # 每5分钟检查一次（高频扫描，确保延迟不超过5分钟）
    scheduler.add_job(
        func=check_and_send_reminders,
        trigger=IntervalTrigger(minutes=5),
        id='frequent_reminder_check',
        name='高频提醒检查（每5分钟）',
        replace_existing=True
    )
    
    # 每日定点检查（早中晚三个关键时段，确保不漏）
    for hour in [8, 12, 20]:
        scheduler.add_job(
            func=check_and_send_reminders,
            trigger=CronTrigger(hour=hour, minute=0, timezone='Asia/Shanghai'),
            id=f'daily_reminder_check_{hour}',
            name=f'每日定时检查 ({hour}:00)',
            replace_existing=True
        )
    
    # 启动调度器
    scheduler.start()
    logger.info("✅ 提醒定时任务调度器已启动")
    logger.info("   - 高频检查: 每5分钟")
    logger.info("   - 定点检查: 每日 8:00 / 12:00 / 20:00")
    logger.info(f"   - 时区: Asia/Shanghai")
    
    return scheduler


def init_scheduler():
    """初始化调度器（在应用启动时调用）"""
    global scheduler
    if scheduler is None:
        scheduler = start_scheduler()
    return scheduler


def shutdown_scheduler():
    """关闭调度器（在应用关闭时调用）"""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("提醒定时任务调度器已关闭")

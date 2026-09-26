"""
浇水提醒服务
"""
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from app.api.models.reminder import RemindConfig, WateringReminder
from app.api.models.plant import UserPlant, WateringRecord
from app.api.services.knowledge_graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)


class WateringReminderService:
    """浇水提醒服务"""
    
    def __init__(self):
        self.kg_service = KnowledgeGraphService()
    
    def get_current_season(self, current_date: Optional[date] = None) -> str:
        """
        根据日期获取当前季节
        
        Args:
            current_date: 当前日期，默认为今天
            
        Returns:
            季节名称: spring, summer, autumn, winter
        """
        if current_date is None:
            current_date = date.today()
        
        month = current_date.month
        
        # 春季: 3-5月
        if 3 <= month <= 5:
            return 'spring'
        # 夏季: 6-8月
        elif 6 <= month <= 8:
            return 'summer'
        # 秋季: 9-11月
        elif 9 <= month <= 11:
            return 'autumn'
        # 冬季: 12-2月
        else:
            return 'winter'
    
    def get_season_name_cn(self, season: str) -> str:
        """获取季节中文名"""
        season_map = {
            'spring': '春季',
            'summer': '夏季',
            'autumn': '秋季',
            'winter': '冬季'
        }
        return season_map.get(season, '未知季节')
    
    def get_watering_interval(self, db: Session, plant: UserPlant, current_date: Optional[date] = None) -> int:
        """
        获取植物的浇水间隔天数（根据季节从知识图谱查询）
        
        Args:
            db: 数据库会话
            plant: 用户植物对象
            current_date: 当前日期
            
        Returns:
            浇水间隔天数，默认7天
        """
        if current_date is None:
            current_date = date.today()
        
        # 获取当前季节
        season = self.get_current_season(current_date)
        
        # 从知识图谱查询浇水频率
        try:
            care_guide = self.kg_service.get_plant_care_guide(plant.plant_name.strip())
            
            if care_guide:
                # 尝试从知识图谱获取季节性浇水信息
                # 注意：这里需要根据实际的字段名调整
                season_field_map = {
                    'spring': 'watering_spring',
                    'summer': 'watering_summer',
                    'autumn': 'watering_autumn',
                    'winter': 'watering_winter'
                }
                
                field_name = season_field_map.get(season)
                if field_name:
                    # 通过Cypher查询获取具体的浇水频率
                    interval = self._get_seasonal_watering_from_kg(plant.plant_name.strip(), field_name)
                    if interval and interval > 0:
                        logger.info(f"植物 '{plant.plant_name}' {self.get_season_name_cn(season)}浇水间隔: {interval}天")
                        return interval
        except Exception as e:
            logger.warning(f"从知识图谱获取浇水频率失败: {e}")
        
        # 默认返回7天
        logger.info(f"使用默认浇水间隔: 7天")
        return 7
    
    def _get_seasonal_watering_from_kg(self, plant_name: str, season_field: str) -> Optional[int]:
        """
        从知识图谱获取季节性浇水频率
        
        Args:
            plant_name: 植物名称
            season_field: 季节字段名
            
        Returns:
            浇水间隔天数
        """
        query = f"""
        MATCH (p:Plant)
        WHERE p.name = $plant_name 
           OR p.scientific_name = $plant_name 
           OR p.name_en = $plant_name
           OR $plant_name IN p.aliases
        RETURN p.{season_field} AS watering_frequency
        LIMIT 1
        """
        
        try:
            with self.kg_service.neo4j_client.driver.session() as session:
                result = session.run(query, plant_name=plant_name)
                record = result.single()
                
                if record and record['watering_frequency']:
                    frequency_str = record['watering_frequency']
                    
                    # 解析 "X天/次" 格式
                    if '天' in frequency_str and '次' in frequency_str:
                        days = int(frequency_str.split('天')[0])
                        return days
                    
                    # 处理"断水"情况
                    if '断水' in frequency_str:
                        return 999  # 设置一个很大的值表示不需要浇水
                        
        except Exception as e:
            logger.error(f"查询知识图谱浇水频率失败: {e}")
        
        return None
    
    def create_or_update_watering_reminder(self, db: Session, user_id: int, plant_id: int, 
                                           last_watering_date: Optional[date] = None,
                                           current_date: Optional[date] = None) -> Dict[str, Any]:
        """
        创建或更新浇水提醒
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            plant_id: 植物ID
            last_watering_date: 上次浇水日期，如果为None则自动查询最近一次浇水记录
            current_date: 当前日期
            
        Returns:
            提醒配置信息
        """
        if current_date is None:
            current_date = date.today()
        
        logger.info(f"开始创建/更新浇水提醒: user_id={user_id}, plant_id={plant_id}")
        
        # 获取植物信息
        plant = db.query(UserPlant).filter(
            UserPlant.id == plant_id,
            UserPlant.user_id == user_id
        ).first()
        
        if not plant:
            logger.error(f"植物不存在: plant_id={plant_id}, user_id={user_id}")
            raise ValueError("植物不存在")
        
        logger.info(f"找到植物: {plant.plant_name}, planting_date={plant.planting_date}")
        
        # 确定基准日期：优先使用传入的日期，否则查询最近一次浇水记录
        base_date = last_watering_date
        
        if not base_date:
            # 查询最近一次浇水记录
            latest_watering = db.query(WateringRecord).filter(
                WateringRecord.user_plant_id == plant_id
            ).order_by(WateringRecord.watering_date.desc()).first()
            
            if latest_watering:
                base_date = latest_watering.watering_date
                logger.info(f"使用最近一次浇水记录日期: {base_date}")
            else:
                # 如果没有浇水记录，使用种植日期
                base_date = plant.planting_date or current_date
                logger.info(f"无浇水记录，使用种植日期: {base_date}")
        
        logger.info(f"基准日期: {base_date} (用于计算下次浇水)")
        
        # 获取浇水间隔
        interval_days = self.get_watering_interval(db, plant, current_date)
        logger.info(f"浇水间隔: {interval_days}天")
        
        # 计算下次浇水日期
        next_watering_date = base_date + timedelta(days=interval_days)
        logger.info(f"下次浇水日期: {next_watering_date}")
        
        # 检查是否已存在提醒配置
        reminder_config = db.query(RemindConfig).filter(
            RemindConfig.user_id == user_id,
            RemindConfig.user_plant_id == plant_id,
            RemindConfig.remind_type == 'water'
        ).first()
        
        if reminder_config:
            # 更新现有配置
            reminder_config.interval_days = interval_days
            reminder_config.scheduled_date = next_watering_date
            reminder_config.frequency_type = 'seasonal'
            reminder_config.is_enabled = True
            reminder_config.updated_at = datetime.now()
        else:
            # 创建新配置
            reminder_config = RemindConfig(
                user_id=user_id,
                user_plant_id=plant_id,
                remind_type='water',
                frequency_type='seasonal',
                interval_days=interval_days,
                scheduled_date=next_watering_date,
                is_enabled=True
            )
            db.add(reminder_config)
        
        db.commit()
        db.refresh(reminder_config)
        
        logger.info(f"创建/更新浇水提醒: 植物={plant.plant_name}, 下次浇水={next_watering_date}, 间隔={interval_days}天")
        
        return {
            "id": reminder_config.id,
            "interval_days": interval_days,
            "scheduled_date": next_watering_date.isoformat(),
            "frequency_type": "seasonal",
            "is_enabled": True,
            "current_season": self.get_current_season(current_date),
            "season_name": self.get_season_name_cn(self.get_current_season(current_date))
        }
    
    def get_today_reminders(self, db: Session, user_id: int, current_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        获取今日的浇水提醒列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            current_date: 当前日期
            
        Returns:
            今日提醒列表
        """
        if current_date is None:
            current_date = date.today()
        
        # 查询今日需要提醒的配置
        reminders = db.query(RemindConfig, UserPlant).join(
            UserPlant, RemindConfig.user_plant_id == UserPlant.id
        ).filter(
            RemindConfig.user_id == user_id,
            RemindConfig.remind_type == 'water',
            RemindConfig.is_enabled == True,
            RemindConfig.scheduled_date == current_date
        ).all()
        
        result = []
        for config, plant in reminders:
            # 检查今日是否已有提醒记录
            today_reminder = db.query(WateringReminder).filter(
                WateringReminder.user_id == user_id,
                WateringReminder.user_plant_id == plant.id,
                WateringReminder.reminder_date == current_date
            ).first()
            
            if not today_reminder:
                # 创建今日提醒记录
                today_reminder = WateringReminder(
                    user_id=user_id,
                    user_plant_id=plant.id,
                    reminder_date=current_date,
                    status='pending'
                )
                db.add(today_reminder)
                db.flush()
            
            result.append({
                "reminder_id": today_reminder.id,
                "plant_id": plant.id,
                "plant_name": plant.plant_name,
                "nickname": plant.nickname,
                "status": today_reminder.status,
                "completed_time_slot": today_reminder.completed_time_slot,
                "postpone_count": today_reminder.postpone_count,
                "time_slots": [
                    {"time": "07:50", "slot": "morning", "label": "早上"},
                    {"time": "12:00", "slot": "noon", "label": "中午"},
                    {"time": "18:00", "slot": "evening", "label": "晚上"}
                ]
            })
        
        db.commit()
        return result
    
    def complete_watering_reminder(self, db: Session, user_id: int, reminder_id: int,
                                   time_slot: str, current_datetime: Optional[datetime] = None) -> Dict[str, Any]:
        """
        完成浇水提醒
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            reminder_id: 提醒ID
            time_slot: 时间段 (morning/noon/evening)
            current_datetime: 当前时间
            
        Returns:
            操作结果
        """
        if current_datetime is None:
            current_datetime = datetime.now()
        
        reminder = db.query(WateringReminder).filter(
            WateringReminder.id == reminder_id,
            WateringReminder.user_id == user_id
        ).first()
        
        if not reminder:
            raise ValueError("提醒记录不存在")
        
        if reminder.status == 'completed':
            return {"message": "该提醒已完成", "already_completed": True}
        
        # 更新提醒状态
        reminder.status = 'completed'
        reminder.completed_at = current_datetime
        reminder.completed_time_slot = time_slot
        reminder.updated_at = current_datetime
        
        # 创建浇水记录
        plant = db.query(UserPlant).filter(UserPlant.id == reminder.user_plant_id).first()
        if plant:
            watering_record = WateringRecord(
                user_plant_id=plant.id,
                watering_date=reminder.reminder_date,
                notes=f"通过提醒完成浇水 ({time_slot})"
            )
            db.add(watering_record)
            
            # 更新下次浇水提醒
            self.create_or_update_watering_reminder(
                db, user_id, plant.id, 
                last_watering_date=reminder.reminder_date,
                current_date=current_datetime.date()
            )
        
        db.commit()
        
        return {
            "message": "浇水完成！",
            "plant_name": plant.plant_name if plant else "未知植物",
            "completed_at": current_datetime.isoformat()
        }
    
    def postpone_watering_reminder(self, db: Session, user_id: int, reminder_id: int,
                                   postpone_hours: int = 24) -> Dict[str, Any]:
        """
        推迟浇水提醒
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            reminder_id: 提醒ID
            postpone_hours: 推迟小时数，默认24小时
            
        Returns:
            操作结果
        """
        reminder = db.query(WateringReminder).filter(
            WateringReminder.id == reminder_id,
            WateringReminder.user_id == user_id
        ).first()
        
        if not reminder:
            raise ValueError("提醒记录不存在")
        
        if reminder.status == 'completed':
            return {"message": "该提醒已完成，无法推迟", "already_completed": True}
        
        # 更新推迟次数
        reminder.postpone_count += 1
        reminder.status = 'postponed'
        reminder.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "message": f"已推迟{postpone_hours}小时",
            "postpone_count": reminder.postpone_count,
            "next_reminder": f"{postpone_hours}小时后再次提醒"
        }

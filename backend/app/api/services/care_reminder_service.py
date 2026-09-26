"""
养护提醒服务（施肥、施药、修剪、浇水等）
"""
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from app.api.models.reminder import RemindConfig
from app.api.models.plant import UserPlant, TreatmentRecord, WateringRecord

logger = logging.getLogger(__name__)


class CareReminderService:
    """养护提醒服务"""
    
    def create_care_reminder(
        self, 
        db: Session, 
        user_id: int, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建养护提醒
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            data: 提醒数据，包含：
                - plant_id: 植物ID
                - remind_type: 类型 (fertilize/pesticide/prune/other)
                - scheduled_date: 计划日期
                - product_name: 产品/药品名称
                - dosage: 用量
                - notes: 备注
                - frequency_type: 频率类型
                - is_enabled: 是否启用
                
        Returns:
            创建的提醒信息
        """
        plant_id = data.get('plant_id')
        
        # 验证植物是否存在
        if plant_id:
            plant = db.query(UserPlant).filter(
                UserPlant.id == plant_id,
                UserPlant.user_id == user_id
            ).first()
            
            if not plant:
                raise ValueError("植物不存在")
        
        # 创建提醒配置
        reminder = RemindConfig(
            user_id=user_id,
            user_plant_id=plant_id,
            remind_type=data.get('remind_type', 'other'),
            frequency_type=data.get('frequency_type', 'one_time'),
            scheduled_date=data.get('scheduled_date'),
            application_date=data.get('scheduled_date'),  # 应用日期默认为计划日期
            product_name=data.get('product_name'),
            dosage=data.get('dosage'),
            notes=data.get('notes'),
            custom_message=data.get('custom_message'),
            is_enabled=data.get('is_enabled', True),
            interval_days=data.get('interval_days', 0),
            repeat_interval=data.get('repeat_interval', 0)
        )
        
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        
        logger.info(f"创建养护提醒成功: id={reminder.id}, type={reminder.remind_type}")
        
        return self._format_reminder_response(reminder, db)
    
    def get_user_reminders(
        self, 
        db: Session, 
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        remind_type: Optional[str] = None,
        status_filter: Optional[str] = None  # 'pending', 'completed'
    ) -> Dict[str, Any]:
        """
        获取用户的养护提醒列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            remind_type: 提醒类型过滤
            status_filter: 状态过滤
            
        Returns:
            提醒列表和总数
        """
        query = db.query(RemindConfig).filter(
            RemindConfig.user_id == user_id
        )
        
        # 类型过滤
        if remind_type:
            query = query.filter(RemindConfig.remind_type == remind_type)
        
        # 状态过滤（根据scheduled_date判断）
        if status_filter:
            today = date.today()
            if status_filter == 'pending':
                query = query.filter(
                    RemindConfig.scheduled_date >= today,
                    RemindConfig.is_enabled == True
                )
            elif status_filter == 'completed':
                query = query.filter(RemindConfig.scheduled_date < today)
        
        # 总数
        total = query.count()
        
        # 分页
        reminders = query.order_by(
            RemindConfig.scheduled_date.asc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化响应
        items = [self._format_reminder_response(r, db) for r in reminders]
        
        # 过滤掉关联已删除植物的提醒
        items = [item for item in items if item.get('plant_id') is not None and item.get('is_active', True)]
        # 更新总数
        total = len(items)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    def get_reminder_detail(
        self, 
        db: Session, 
        user_id: int, 
        reminder_id: int
    ) -> Dict[str, Any]:
        """
        获取提醒详情
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            reminder_id: 提醒ID
            
        Returns:
            提醒详情
        """
        reminder = db.query(RemindConfig).filter(
            RemindConfig.id == reminder_id,
            RemindConfig.user_id == user_id
        ).first()
        
        if not reminder:
            raise ValueError("提醒不存在")
        
        return self._format_reminder_response(reminder, db)
    
    def update_reminder(
        self, 
        db: Session, 
        user_id: int, 
        reminder_id: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新提醒
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            reminder_id: 提醒ID
            data: 更新数据
            
        Returns:
            更新后的提醒信息
        """
        reminder = db.query(RemindConfig).filter(
            RemindConfig.id == reminder_id,
            RemindConfig.user_id == user_id
        ).first()
        
        if not reminder:
            raise ValueError("提醒不存在")
        
        # 更新字段
        if 'remind_type' in data:
            reminder.remind_type = data['remind_type']
        if 'scheduled_date' in data:
            reminder.scheduled_date = data['scheduled_date']
            reminder.application_date = data['scheduled_date']
        if 'product_name' in data:
            reminder.product_name = data['product_name']
        if 'dosage' in data:
            reminder.dosage = data['dosage']
        if 'notes' in data:
            reminder.notes = data['notes']
        if 'custom_message' in data:
            reminder.custom_message = data['custom_message']
        if 'is_enabled' in data:
            reminder.is_enabled = data['is_enabled']
        if 'frequency_type' in data:
            reminder.frequency_type = data['frequency_type']
        if 'interval_days' in data:
            reminder.interval_days = data['interval_days']
        if 'repeat_interval' in data:
            reminder.repeat_interval = data['repeat_interval']
        
        reminder.updated_at = datetime.now()
        
        db.commit()
        db.refresh(reminder)
        
        logger.info(f"更新养护提醒成功: id={reminder_id}")
        
        return self._format_reminder_response(reminder, db)
    
    def delete_reminder(
        self, 
        db: Session, 
        user_id: int, 
        reminder_id: int
    ) -> bool:
        """
        删除提醒
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            reminder_id: 提醒ID
            
        Returns:
            是否删除成功
        """
        reminder = db.query(RemindConfig).filter(
            RemindConfig.id == reminder_id,
            RemindConfig.user_id == user_id
        ).first()
        
        if not reminder:
            raise ValueError("提醒不存在")
        
        db.delete(reminder)
        db.commit()
        
        logger.info(f"删除养护提醒成功: id={reminder_id}")
        
        return True
    
    def complete_and_sync_to_treatment(
        self, 
        db: Session, 
        user_id: int, 
        reminder_id: int,
        actual_date: Optional[date] = None,
        actual_product: Optional[str] = None,
        actual_dosage: Optional[str] = None,
        actual_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        完成提醒并同步到养护记录表或浇水记录表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            reminder_id: 提醒ID
            actual_date: 实际执行日期（默认为提醒的计划日期）
            actual_product: 实际使用的产品（默认使用提醒中的产品）
            actual_dosage: 实际用量（默认使用提醒中的用量）
            actual_notes: 实际备注（会与提醒备注合并）
            
        Returns:
            操作结果
        """
        # 获取提醒
        reminder = db.query(RemindConfig).filter(
            RemindConfig.id == reminder_id,
            RemindConfig.user_id == user_id
        ).first()
        
        if not reminder:
            raise ValueError("提醒不存在")
        
        if not reminder.user_plant_id:
            raise ValueError("提醒未关联植物")
        
        # 验证植物
        plant = db.query(UserPlant).filter(
            UserPlant.id == reminder.user_plant_id,
            UserPlant.user_id == user_id
        ).first()
        
        if not plant:
            raise ValueError("关联的植物不存在")
        
        # 确定实际执行日期
        execution_date = actual_date or reminder.scheduled_date or date.today()
        
        # 根据提醒类型同步到不同的表
        if reminder.remind_type == 'water':
            # 同步到浇水记录表
            record = WateringRecord(
                user_plant_id=reminder.user_plant_id,
                watering_date=execution_date,
                water_amount=actual_dosage or reminder.dosage,
                notes=self._merge_notes(reminder.notes, actual_notes)
            )
            record_type = 'watering'
        else:
            # 同步到养护记录表
            record = TreatmentRecord(
                user_plant_id=reminder.user_plant_id,
                treatment_type=reminder.remind_type,
                product_name=actual_product or reminder.product_name,
                dosage=actual_dosage or reminder.dosage,
                application_date=execution_date,
                notes=self._merge_notes(reminder.notes, actual_notes)
            )
            record_type = 'treatment'
        
        db.add(record)
        
        # 根据频率类型处理提醒
        if reminder.frequency_type == 'interval' and reminder.interval_days and reminder.interval_days > 0:
            # 自定义间隔：创建下一次提醒
            next_scheduled_date = execution_date + timedelta(days=reminder.interval_days)
            
            # 创建新的提醒配置
            new_reminder = RemindConfig(
                user_id=reminder.user_id,
                user_plant_id=reminder.user_plant_id,
                remind_type=reminder.remind_type,
                frequency_type='interval',
                interval_days=reminder.interval_days,
                scheduled_date=next_scheduled_date,
                product_name=reminder.product_name,
                dosage=reminder.dosage,
                notes=reminder.notes,
                custom_message=reminder.custom_message,
                is_enabled=True,
                repeat_interval=reminder.repeat_interval,
                created_at=datetime.now()
            )
            db.add(new_reminder)
            
            # 禁用当前提醒
            reminder.is_enabled = False
            reminder.updated_at = datetime.now()
            
            db.commit()
            db.refresh(record)
            
            logger.info(
                f"完成提醒并创建下次提醒: reminder_id={reminder_id}, "
                f"record_id={record.id}, next_date={next_scheduled_date}"
            )
        else:
            # 其他频率类型：仅禁用当前提醒
            reminder.is_enabled = False
            reminder.updated_at = datetime.now()
            
            db.commit()
            db.refresh(record)
            
            logger.info(
                f"完成提醒并同步到{record_type}记录: reminder_id={reminder_id}, "
                f"record_id={record.id}"
            )
        
        result = {
            "message": "提醒已完成，已同步到记录",
            "record_id": record.id,
            "record_type": record_type,
            "plant_name": plant.plant_name,
            "nickname": plant.nickname,
            "remind_type": reminder.remind_type,
            "application_date": execution_date.isoformat()
        }
        
        # 添加类型特定的字段
        if record_type == 'watering':
            result["water_amount"] = record.water_amount
        else:
            result["product_name"] = record.product_name
            result["dosage"] = record.dosage
        
        # 如果是自定义间隔，添加下次提醒信息
        if reminder.frequency_type == 'interval' and reminder.interval_days and reminder.interval_days > 0:
            next_scheduled_date = execution_date + timedelta(days=reminder.interval_days)
            result["next_reminder_date"] = next_scheduled_date.isoformat()
            result["interval_days"] = reminder.interval_days
            result["message"] = f"提醒已完成，已同步到记录。下次提醒：{next_scheduled_date.strftime('%Y年%m月%d日')}"
        
        return result
    
    def _format_reminder_response(
        self, 
        reminder: RemindConfig, 
        db: Session
    ) -> Dict[str, Any]:
        """
        格式化提醒响应
        
        Args:
            reminder: 提醒对象
            db: 数据库会话
            
        Returns:
            格式化后的字典
        """
        # 获取植物信息
        plant_info = {}
        if reminder.user_plant_id:
            plant = db.query(UserPlant).filter(
                UserPlant.id == reminder.user_plant_id
            ).first()
            
            if plant:
                plant_info = {
                    "plant_id": plant.id,
                    "plant_name": plant.plant_name,
                    "nickname": plant.nickname,
                    "is_active": plant.status == 1  # 标记植物是否活跃
                }
            else:
                # 植物不存在，标记为非活跃
                plant_info = {
                    "plant_id": None,
                    "plant_name": None,
                    "nickname": None,
                    "is_active": False
                }
        
        # 判断状态
        today = date.today()
        if reminder.scheduled_date:
            if reminder.scheduled_date < today:
                status = 'completed' if not reminder.is_enabled else 'overdue'
            elif reminder.scheduled_date == today:
                status = 'today'
            else:
                status = 'pending'
        else:
            status = 'unknown'
        
        return {
            "id": reminder.id,
            "user_id": reminder.user_id,
            **plant_info,
            "remind_type": reminder.remind_type,
            "frequency_type": reminder.frequency_type,
            "interval_days": reminder.interval_days,
            "scheduled_date": reminder.scheduled_date.isoformat() if reminder.scheduled_date else None,
            "application_date": reminder.application_date.isoformat() if reminder.application_date else None,
            "product_name": reminder.product_name,
            "dosage": reminder.dosage,
            "custom_message": reminder.custom_message,
            "notes": reminder.notes,
            "is_enabled": reminder.is_enabled,
            "status": status,
            "created_at": reminder.created_at.isoformat() if reminder.created_at else None,
            "updated_at": reminder.updated_at.isoformat() if reminder.updated_at else None
        }
    
    def _merge_notes(self, original_notes: Optional[str], additional_notes: Optional[str]) -> Optional[str]:
        """
        合并备注
        
        Args:
            original_notes: 原始备注
            additional_notes: 附加备注
            
        Returns:
            合并后的备注
        """
        if not original_notes and not additional_notes:
            return None
        
        if not original_notes:
            return additional_notes
        
        if not additional_notes:
            return original_notes
        
        return f"{original_notes}\n{additional_notes}"

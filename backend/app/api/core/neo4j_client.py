"""
Neo4j 知识图谱连接管理
"""
from neo4j import GraphDatabase
from app.api.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("neo4j_client")


class Neo4jClient:
    """Neo4j 客户端单例"""
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                    database=settings.neo4j_database
                )
                # 测试连接
                with self._driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"✓ Neo4j 连接成功: {settings.neo4j_uri}")
                self.connected = True
            except Exception as e:
                logger.warning(f"⚠ Neo4j 连接失败: {e}。知识图谱功能将不可用，但应用将继续运行。")
                self._driver = None
                self.connected = False
    
    @property
    def driver(self):
        return self._driver
    
    def close(self):
        if self._driver:
            self._driver.close()
            logger.info("✓ Neo4j 连接已关闭")


def get_neo4j_session():
    """获取 Neo4j session（用于依赖注入）"""
    client = Neo4jClient()
    session = client.driver.session(database=settings.neo4j_database)
    try:
        yield session
    finally:
        session.close()

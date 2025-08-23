from sqlalchemy import Column, Integer, String, DECIMAL, Text, JSON, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RecommendationSession(Base):
    """推奨セッションモデル"""
    __tablename__ = 'recommendation_sessions'

    session_id = Column(
        Integer, 
        primary_key=True
    )
    generated_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    principal = Column(DECIMAL(20,4), nullable=False)
    risk_tolerance = Column(String(20), nullable=False)
    strategy = Column(String(50), nullable=False)
    symbols = Column(ARRAY(String))
    technical_filter = Column(Text)
    ai_raw_response = Column(Text)
    total_return_estimate = Column(String(20))

class RecommendationResult(Base):
    """推奨結果モデル"""
    __tablename__ = 'recommendation_results'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable=False)
    symbol = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    allocation = Column(String(10), nullable=False)
    confidence = Column(DECIMAL(5,4))
    reason = Column(Text)

class PromptTemplate(Base):
    """プロンプトテンプレートモデル"""
    __tablename__ = 'prompt_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    agent_type = Column(String(20), nullable=False, server_default="direct")
    system_role = Column(Text)
    user_template = Column(Text, nullable=False)
    output_format = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

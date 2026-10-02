from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    env:str="dev"
    database_url:str="postgresql+asyncpg://agent:agent@localhost:5432/agent"
    redis_url:str="redis://localhost:6379/0"
    foundry_project_endpoint:str=""
    foundry_model_name:str=""
    toolbox_endpoint:str=""
    toolbox_name:str=""
    azure_ai_search_endpoint:str=""
    azure_ai_search_index:str=""
    jwt_secret:str="change-me"
    max_parallel_tasks:int=8
    max_agent_steps:int=12
    tool_timeout_seconds:float=30
    approval_secret:str="change-me"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()

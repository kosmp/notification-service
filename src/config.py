from pydantic_settings import BaseSettings, SettingsConfigDict


class PydanticSettings(BaseSettings):
    rabbitmq_default_user: str = None
    rabbitmq_default_pass: str = None
    rabbitmq_port: str = None

    mongodb_port: str = None
    mongo_initdb_root_username: str = None
    mongo_initdb_root_password: str = None
    mongo_initdb_database: str = None

    model_config = SettingsConfigDict(env_file=".env")


settings = PydanticSettings()

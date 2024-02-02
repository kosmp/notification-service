from pydantic_settings import BaseSettings, SettingsConfigDict


class PydanticSettings(BaseSettings):
    rabbitmq_default_user: str = None
    rabbitmq_default_pass: str = None
    rabbitmq_port: int = None
    rabbitmq_host: str = None

    mongodb_port: int = None
    mongodb_host: str = None
    mongo_initdb_root_username: str = None
    mongo_initdb_root_password: str = None
    mongo_initdb_database: str = None

    localstack_endpoint_url: str = None
    localstack_access_key_id: str = None
    localstack_secret_access_key: str = None

    model_config = SettingsConfigDict(env_file=".env")


settings = PydanticSettings()

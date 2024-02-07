from pydantic_settings import BaseSettings, SettingsConfigDict


class PydanticSettings(BaseSettings):
    rabbitmq_default_user: str = None
    rabbitmq_default_pass: str = None
    rabbitmq_port: int = None
    rabbitmq_host: str = None
    rabbitmq_vhost: str = None
    rabbitmq_email_queue_name: str = None

    mongodb_port: int = None
    mongodb_root_username: str = None
    mongodb_primary_host: str = None
    mongodb_root_password: str = None
    mongo_initdb_database: str = None
    mongodb_replica_set_key: str = None
    mongodb_replica_set_name: str = None

    localstack_endpoint_url: str = None
    localstack_access_key_id: str = None
    localstack_secret_access_key: str = None
    localstack_region_name: str = None
    localstack_sender_email: str = None

    model_config = SettingsConfigDict(env_file=".env")


settings = PydanticSettings()

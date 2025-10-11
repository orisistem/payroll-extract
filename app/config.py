from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # --- Informações gerais ---
    app_name: str = "Payroll Extract API"
    environment: str = "development"  # development | production | test
    debug: bool = True

    # --- Banco de Dados ---
    database_url: str = f"file:{BASE_DIR}/prisma/data.db"

    # --- Logs ---
    log_level: str = "INFO"
    log_dir: Path = BASE_DIR / "logs"

    # --- Exportação ---
    export_dir: Path = BASE_DIR / "exports"

    # --- Configuração do Prisma ---
    prisma_log_queries: bool = False  # ativa logs SQL detalhados (útil para debug)

    # --- Configurações do FastAPI ---
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True  # útil para desenvolvimento

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instância global de configurações
settings = Settings()

# Cria diretórios necessários
settings.log_dir.mkdir(exist_ok=True)
settings.export_dir.mkdir(exist_ok=True)

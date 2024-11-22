import os
from dotenv import load_dotenv
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Carregar as variáveis do arquivo .env
load_dotenv()

# Importar a base que contém as informações de metadata
from models.base import Base

from models import Conta, AnbimaDebentures

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Other values from the config can be acquired
# Example: my_important_option = config.get_main_option("my_important_option")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine. By skipping the Engine creation,
    we don't need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    # Obter a URL do banco de dados da variável de ambiente
    url = os.getenv("DATABASE_PUBLIC_URL")  # Usar a variável de ambiente DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Obter configuração da seção alembic
    configuration = config.get_section(config.config_ini_section)
    
    # Substituir a URL com a variável de ambiente
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_PUBLIC_URL")
    
    # Criar engine com a configuração atualizada
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Verificar se estamos em modo offline ou online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from orchx_api.core.database import Base, get_db
from orchx_api.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Instantiate mock kernel dependencies
    from orchx_core.config import KernelConfig, SecurityConfig, RuntimeConfig
    from orchx_runtime.bus import InMemoryEventBus
    from orchx_runtime.context import KernelContext
    from orchx_runtime.agent_registry import AgentRegistry
    from orchx_runtime.capability_registry import CapabilityRegistry
    from orchx_runtime.provider_registry import ProviderRegistry
    from orchx_runtime.tool_registry import ToolRegistry
    from orchx_runtime.workflow_registry import WorkflowRegistry
    from orchx_runtime.kernel import Kernel

    config = KernelConfig(
        project_name="OrchX Test OS",
        security=SecurityConfig(
            secret_key="testsecretkey",
            enable_sandbox=True
        ),
        runtime=RuntimeConfig(
            plugin_dir="test_plugins"
        )
    )
    event_bus = InMemoryEventBus()
    context = KernelContext(
        config=config,
        event_bus=event_bus,
        provider_registry=ProviderRegistry(),
        agent_registry=AgentRegistry(),
        tool_registry=ToolRegistry(),
        workflow_registry=WorkflowRegistry(),
        capability_registry=CapabilityRegistry()
    )
    app.state.kernel = Kernel(context)
    app.state.kernel_context = context
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac
        
    app.dependency_overrides.clear()

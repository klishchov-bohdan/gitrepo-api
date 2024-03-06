from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.database import get_async_session, async_session_maker

app = FastAPI(
    title=settings.PROJECT_NAME,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    get_trigger_stmt = text('''
        SELECT * FROM information_schema.triggers WHERE trigger_name = 'check_rating';
    ''')
    create_trigger_func_stmt = text('''
        CREATE OR REPLACE FUNCTION update_rating()
        RETURNS TRIGGER
        LANGUAGE PLPGSQL
        AS $$
        BEGIN
            UPDATE repository as main
            SET position_prev = position_cur, position_cur = subquery.rating
            FROM (SELECT id, RANK() OVER (ORDER BY stars DESC) AS rating
                FROM repository) as subquery
            WHERE main.id = subquery.id;
            RETURN NULL;
        END;
        $$
    ''')
    create_trigger_stmt = text('''
        CREATE TRIGGER check_rating
        AFTER UPDATE OR INSERT OR DELETE
        ON repository
        FOR EACH ROW
        WHEN (pg_trigger_depth() < 1)
        EXECUTE PROCEDURE update_rating();
    ''')
    async with async_session_maker() as session:
        result = await session.execute(get_trigger_stmt)
        if len(result.all()) == 0:
            await session.execute(create_trigger_func_stmt)
            await session.execute(create_trigger_stmt)
            await session.commit()

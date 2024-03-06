from datetime import datetime

from sqlalchemy import text

from app.models import Repository
from app.utils.repo import SQLAlchemyRepository


class RepositoryRepo(SQLAlchemyRepository):
    model = Repository

    async def find_top100_stars(self, sort_by: str, sort_strategy: str):
        stmt = text(f'''
                    SELECT *
                    FROM {self.model.__tablename__}
                    ORDER BY {sort_by} {sort_strategy} 
                    LIMIT 100
                ''')
        result = await self.session.execute(stmt)
        res_columns = result.keys()
        rows_values = result.all()
        return [dict(zip(res_columns, row_values)) for row_values in rows_values]

    async def get_activity(self, repository_name: str, owner: str, since: datetime, until: datetime):
        data = {
            'repository_name': repository_name,
            'owner': owner,
            'since': since,
            'until': until
        }
        stmt = text(f'''
                    SELECT
                        DATE(ra.pushed_at) AS date,
                        COUNT(*) AS commits,
                        ARRAY_AGG(DISTINCT a.name) AS authors
                    FROM
                        repository_author ra
                    JOIN
                        repository r ON ra.repository_id = r.id
                    JOIN
                        author a ON ra.author_id = a.id
                    WHERE
                        ra.pushed_at BETWEEN :since AND :until
                        AND r.repo = :repository_name
                        AND r.owner = :owner
                    GROUP BY
                        DATE(ra.pushed_at)
                    ORDER BY
                        DATE(ra.pushed_at);
                ''')
        result = await self.session.execute(stmt, data)
        res_columns = result.keys()
        rows_values = result.all()
        return [dict(zip(res_columns, row_values)) for row_values in rows_values]

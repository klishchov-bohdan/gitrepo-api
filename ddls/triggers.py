from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

rating_update_func = PGFunction(
    schema="public",
    signature="rating_update_func()",
    definition="""
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
            """)

rating_update_trigger = PGTrigger(
    schema="public",
    signature="rating_update_trigger",
    on_entity="public.repository",
    is_constraint=False,
    definition="""
                    AFTER UPDATE OR INSERT OR DELETE
                        ON repository
                        FOR EACH ROW
                        WHEN (pg_trigger_depth() < 1)
                        EXECUTE PROCEDURE rating_update_func();
                """)

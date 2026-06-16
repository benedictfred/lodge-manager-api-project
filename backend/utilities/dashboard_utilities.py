from sqlalchemy import or_, and_, Select
from app.core.enums import RoomStatus
from app.schemas.dashboard import DashboardFilters


def apply_dashboard_filters(filters: dict ,  filter_by: DashboardFilters, stmt: Select):
    if not filter_by:
        return stmt

    all_conditions = []
    if filter_by.room_status_filters:
        for status in filter_by.room_status_filters:
            sql_expr = filters.get(status)

            if sql_expr is not None:
                if status == RoomStatus.OCCUPIED:
                    if not filter_by.financial_filters:
                        all_conditions.append(sql_expr)
                else:
                    all_conditions.append(sql_expr)


    if filter_by.financial_filters:
        for badge in filter_by.financial_filters:
            sql_expr = filters.get(badge)
            if sql_expr is not None:
                all_conditions.append(and_(*sql_expr))

    if all_conditions:
        stmt = stmt.where(or_(*all_conditions))

    return stmt
     
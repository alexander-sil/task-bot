from .start import register_start_handler
from .create_task import register_create_task_handlers
from .delete_task import register_delete_task_handlers
from .edit_task import register_edit_task_handlers
from .list_tasks import register_list_task_handler
from .comment_task import register_comment_task_handlers
from handlers.create_task import register_create_task_handlers
from db import async_session


def register_handlers(dp, db_pool):
    register_start_handler(dp, async_session)
    register_create_task_handlers(dp, async_session)
    register_delete_task_handlers(dp, async_session)
    register_edit_task_handlers(dp, async_session)
    register_list_task_handler(dp, async_session)
    register_comment_task_handlers(dp, async_session)

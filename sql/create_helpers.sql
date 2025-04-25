-- Триггер на обновление задачи

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;


-- автозаполнение end_time в time_entries, если duration и start_time заданы

CREATE OR REPLACE FUNCTION fill_end_time()
RETURNS TRIGGER AS $$
BEGIN
   IF NEW.end_time IS NULL AND NEW.duration IS NOT NULL THEN
       NEW.end_time := NEW.start_time + NEW.duration;
   END IF;
   RETURN NEW;
END;


CREATE TRIGGER fill_time_entries_end_time
BEFORE INSERT OR UPDATE ON time_entries
FOR EACH ROW
EXECUTE FUNCTION fill_end_time();



-- представление task_details, отображает:
-- Название задачи
-- Статус
-- Имя пользователя
-- Дата дедлайна
-- Общее время, потраченное на задачу

CREATE OR REPLACE VIEW task_details AS
SELECT
    t.id AS task_id,
    t.title,
    s.status,
    u.first_name || ' ' || u.last_name AS user_fullname,
    t.due_date,
    COALESCE(SUM(te.duration), INTERVAL '0') AS total_time_spent
FROM tasks t
LEFT JOIN statuses s ON t.id = s.task_id
LEFT JOIN users u ON t.user_id = u.id
LEFT JOIN time_entries te ON t.id = te.task_id
GROUP BY t.id, t.title, s.status, u.first_name, u.last_name, t.due_date;


-- индекс Индекс на task_id в comments — ускоряет выборку комментариев по задаче, если их много

CREATE INDEX IF NOT EXISTS idx_comments_task_id ON comments(task_id);


-- Индекс на status в statuses — для частой фильтрации задач:

CREATE INDEX IF NOT EXISTS idx_statuses_status ON statuses(status);

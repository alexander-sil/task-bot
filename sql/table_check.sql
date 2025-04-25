SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name IN ('users', 'tasks', 'time_entries', 'comments');

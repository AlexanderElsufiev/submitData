

-- Скрипт для модификации существующей базы данных
-- Добавляем поле status в таблицу pereval_added

-- 1. Добавляем столбец status
ALTER TABLE public.pereval_added
ADD COLUMN IF NOT EXISTS status VARCHAR(8) DEFAULT 'new';

-- 2. Добавляем ограничение на допустимые значения
ALTER TABLE public.pereval_added
ADD CONSTRAINT status_check
CHECK (status IN ('new', 'pending', 'accepted', 'rejected'));



-- 3. Обновляем существующие записи (если есть) на значение по умолчанию
UPDATE public.pereval_added
SET status = 'new'
WHERE status IS NULL;

-- 4. Создаем индекс для ускорения поиска по статусу
CREATE INDEX IF NOT EXISTS idx_pereval_added_status
ON public.pereval_added (status);

-- 5. Добавляем комментарии для документации
COMMENT ON COLUMN public.pereval_added.status IS 'Статус модерации: new, pending, accepted, rejected';
/**/
-- Проверяем результат
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'pereval_added'
  AND table_schema = 'public'
ORDER BY ordinal_position;
/**/



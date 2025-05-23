-- Тестовые данные для системы управления оборудованием
-- Порядок вставки соответствует порядку зависимостей внешних ключей

-- Пользователи (users)
INSERT INTO users (id, username, full_name, email, role, password_hash) VALUES 
(1, 'admin', 'Администратор Системы', 'admin@example.com', 'admin', '$2b$12$6CrakMQ7.ye4.tjZPZV8sOcZgWUkBzMQ5EOytanJVhDKRa0CfLMAC'), -- пароль: admin123
(2, 'manager', 'Менеджер Иванов', 'manager@example.com', 'manager', '$2b$12$tTRluKaAXEfJLcQXPyDKluihMkMPiV4Jp.ZsPtM0CetVMZ3UT7oKO'), -- пароль: manager123
(3, 'tech', 'Техник Петров', 'tech@example.com', 'technician', '$2b$12$NQcVKGdptLBDcepuhGKzBOA.aNUxxdQYgq22/.RGHnmL7ys6JLG0O'); -- пароль: tech123

-- Локации (locations)
INSERT INTO locations (id, name, parent_id, description, created_by) VALUES
(1, 'Главный офис', NULL, 'Центральное здание компании', 1),
(2, 'Дата-центр', 1, 'Серверное помещение', 1),
(3, 'Отдел разработки', 1, 'Кабинеты разработчиков', 2),
(4, 'Серверная №1', 2, 'Основная серверная', 2),
(5, 'Серверная №2', 2, 'Резервная серверная', 2),
(6, 'Склад', 1, 'Складские помещения', 3);

-- Типы комплектующих (part_types)
INSERT INTO part_types (id, name, description, expected_failure_interval_days, created_by) VALUES
(1, 'Процессор', 'Центральный процессор компьютера', 1825, 1),  -- ~5 лет
(2, 'Оперативная память', 'Модули памяти', 1095, 1),  -- ~3 года
(3, 'Жесткий диск', 'HDD накопитель', 730, 2),  -- ~2 года
(4, 'SSD накопитель', 'Твердотельный накопитель', 1460, 2),  -- ~4 года
(5, 'Блок питания', 'Источник питания компьютера', 1095, 3);  -- ~3 года

-- Типы устройств (device_types)
INSERT INTO device_types (id, manufacturer, model, expected_lifetime_months, part_type_id, created_by) VALUES
(1, 'Dell', 'PowerEdge R740', 60, 1, 1),  -- Сервер
(2, 'HP', 'ProLiant DL380', 60, 1, 1),    -- Сервер
(3, 'Cisco', 'Catalyst 9300', 48, 2, 2),  -- Коммутатор
(4, 'Dell', 'Latitude 7420', 36, 4, 3),   -- Ноутбук
(5, 'HP', 'EliteBook 840', 36, 4, 3);     -- Ноутбук

-- Устройства (devices)
INSERT INTO devices (id, serial_number, type_id, purchase_date, warranty_end, current_location_id, status, created_by) VALUES
(1, 'DELL-SRV-001', 1, '2022-01-15', '2025-01-15', 4, 'active', 1),
(2, 'DELL-SRV-002', 1, '2022-01-15', '2025-01-15', 4, 'active', 1),
(3, 'HP-SRV-001', 2, '2021-10-10', '2024-10-10', 5, 'active', 2),
(4, 'CISCO-SW-001', 3, '2022-05-20', '2025-05-20', 4, 'active', 2),
(5, 'CISCO-SW-002', 3, '2022-05-20', '2025-05-20', 5, 'maintenance', 2),
(6, 'DELL-LT-001', 4, '2023-03-01', '2026-03-01', 3, 'active', 3),
(7, 'DELL-LT-002', 4, '2023-03-01', '2026-03-01', 3, 'active', 3),
(8, 'HP-LT-001', 5, '2022-11-15', '2025-11-15', 3, 'inactive', 3),
(9, 'HP-LT-002', 5, '2022-11-15', '2025-11-15', 6, 'repair', 3),
(10, 'DELL-SRV-003', 1, '2021-07-05', '2024-07-05', 6, 'decommissioned', 1);

-- Перемещения (movements)
INSERT INTO movements (id, device_id, from_location_id, to_location_id, moved_at, performed_by, notes) VALUES
(1, 1, NULL, 4, '2022-01-20 10:00:00+03', 1, 'Первоначальная установка'),
(2, 2, NULL, 4, '2022-01-20 11:30:00+03', 1, 'Первоначальная установка'),
(3, 3, NULL, 5, '2021-10-15 09:45:00+03', 2, 'Первоначальная установка'),
(4, 5, 4, 5, '2023-03-15 14:20:00+03', 2, 'Перемещение для технического обслуживания'),
(5, 9, 3, 6, '2023-05-10 16:00:00+03', 3, 'Отправлен в ремонт'),
(6, 10, 4, 6, '2023-10-05 11:15:00+03', 1, 'Перемещен на склад для списания');

-- События инвентаризации (inventory_events)
INSERT INTO inventory_events (id, event_date, location_id, performed_by, notes) VALUES
(1, '2023-01-10', 4, 1, 'Ежегодная инвентаризация серверной №1'),
(2, '2023-01-15', 5, 2, 'Ежегодная инвентаризация серверной №2'),
(3, '2023-06-20', 3, 3, 'Проверка наличия оборудования отдела разработки');

-- Записи инвентаризации (inventory_items)
INSERT INTO inventory_items (id, inventory_event_id, device_id, found, condition, comments) VALUES
(1, 1, 1, TRUE, 'excellent', 'Устройство в отличном состоянии'),
(2, 1, 2, TRUE, 'good', 'Необходима очистка от пыли'),
(3, 1, 4, TRUE, 'excellent', 'Устройство в отличном состоянии'),
(4, 2, 3, TRUE, 'good', NULL),
(5, 2, 5, TRUE, 'needs_maintenance', 'Наблюдаются ошибки в логах'),
(6, 3, 6, TRUE, 'excellent', NULL),
(7, 3, 7, TRUE, 'good', NULL),
(8, 3, 8, FALSE, NULL, 'Устройство не найдено на месте');

-- Задачи обслуживания (maintenance_tasks)
INSERT INTO maintenance_tasks (id, device_id, task_type, scheduled_date, completed_date, status, assigned_to, notes) VALUES
(1, 1, 'Плановое обслуживание', '2023-07-15', '2023-07-16', 'completed', 3, 'Очистка от пыли, проверка температурного режима'),
(2, 2, 'Плановое обслуживание', '2023-07-20', '2023-07-21', 'completed', 3, 'Очистка от пыли, проверка температурного режима'),
(3, 5, 'Внеплановый ремонт', '2023-03-16', '2023-04-05', 'completed', 3, 'Замена неисправного блока питания'),
(4, 3, 'Плановое обслуживание', '2023-10-10', NULL, 'pending', 3, 'Регулярная проверка'),
(5, 4, 'Обновление прошивки', '2023-11-15', NULL, 'pending', 3, 'Установка новой версии ПО');

-- Записи о неисправностях (failure_records)
INSERT INTO failure_records (id, device_id, part_type_id, failure_date, resolved_date, description) VALUES
(1, 5, 5, '2023-03-15', '2023-04-05', 'Вышел из строя блок питания'),
(2, 9, 4, '2023-05-10', NULL, 'Неисправность SSD накопителя'),
(3, 3, 2, '2023-08-20', '2023-08-25', 'Ошибка памяти, заменен модуль');

-- Предложения по замене (replacement_suggestions)
INSERT INTO replacement_suggestions (id, part_type_id, suggestion_date, forecast_replacement_date, generated_by, status, comments) VALUES
(1, 3, '2023-06-10', '2023-12-10', 'system', 'pending', 'Рекомендуется заменить жесткие диски из-за высокой наработки'),
(2, 5, '2023-07-15', '2023-10-15', 'system', 'approved', 'Превентивная замена блоков питания'),
(3, 2, '2023-09-01', '2024-03-01', 'manual', 'rejected', 'Не требуется, модули памяти были недавно заменены');

-- Отчеты о списании (write_off_reports)
INSERT INTO write_off_reports (id, device_id, report_date, reason, disposed_by, approved_by) VALUES
(1, 10, '2023-10-10', 'Моральный износ, экономически нецелесообразно дальнейшее использование', 3, 1); 
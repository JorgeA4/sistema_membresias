-- DATOS INICIALES DE LA BASE DE DATOS NEXUM
USE Nexum;

START TRANSACTION;

INSERT INTO rol (codigo, nombre, descripcion) VALUES
('ADM', 'Administrador', 'Control total de la plataforma Nexum: configuración de planes, gestión de miembros, usuarios y recompensas.'),
('CAJ', 'Cajero', 'Registro de compras asociadas a la membresía del cliente al momento de la venta.'),
('GER', 'Gerente de Sucursal', 'Supervisión de operaciones del programa, validación de canjes especiales y reportes.');

INSERT INTO plan (codigo, nombre, descripcion) VALUES
('BAS', 'Plan Nexum Basic', 'Plan de entrada con acumulación de puntos estándar y descuentos en días seleccionados.'),
('PRE', 'Plan Nexum Premium', 'Plan preferencial con mayor porcentaje de acumulación, cashback y descuentos entre semana.'),
('VIP', 'Plan Nexum Black Elite', 'Plan exclusivo VIP con máxima bonificación de cashback, puntos sin caducidad y descuentos diarios.');

INSERT INTO config_cashback (num, porcentaje, limite_min_mensual) VALUES
(1, 0.02, 100.00), (2, 0.02, 100.00), (3, 0.05, 150.00),
(4, 0.05, 150.00), (5, 0.08, 200.00), (6, 0.06, 120.00);

INSERT INTO config_puntos (num, porcentaje, vigencia_meses) VALUES
(1, 0.05, 12), (2, 0.05, 12), (3, 0.10, 18),
(4, 0.10, 24), (5, 0.15, NULL), (6, 0.12, 12);

INSERT INTO config_descuento (num, porcentaje, monto_minimo) VALUES
(1, 0.05, 200.00), (2, 0.08, 200.00), (3, 0.12, 300.00),
(4, 0.15, 250.00), (5, 0.20, 200.00), (6, 0.18, 250.00);

INSERT INTO dia_aplicable_desc (config_descuento, dia_semana) VALUES
(1, 2), (1, 4), (2, 2), (2, 4),
(3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
(4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7);

INSERT INTO miembro (num, nombre, primer_apellido, segundo_apellido, telefono, correo, `contraseña`, fecha_registro) VALUES
(1, 'Damian', 'Cornejo', 'Gallegos', '5512345678', 'damian.cornejo@gmail.com', '$2b$12$3hZiItohEsJNK8rM8ehzhezHiz7wTb6ccERoASErRI6TI2swcjk7W', '2024-01-10'),
(2, 'Valeria', 'Hernández', 'Cruz', '8187654321', 'valeria.hdz@outlook.com', '$2b$12$ro3dEmATYx3iXbn3naYq1uOVCYo/qIV69sE9j1PY3MtiSVwL4YYuC', '2024-03-15'),
(3, 'Alejandro', 'Torres', 'García', '3398761234', 'alex.torres@hotmail.com', '$2b$12$.wF2XMCmonjr0dK2kDxO0uc.CIKYT3cejH9.OMQWNFLOQ0BGv6XHy', '2024-05-20'),
(4, 'Daniela Sofía', 'Vargas', 'Morales', '5567890123', 'daniela.vargas@yahoo.com', '$2b$12$9fscKB3DHMo/uiwp4D1lqO4B3Rv1IlTjIUoPu5mLfSJenRWx..wWW', '2024-08-01'),
(5, 'José Luis', 'Navarro', 'Delgado', '8112349876', 'jluis.navarro@gmail.com', '$2b$12$I.6tKxHwpsfYdottGcWeaebWWkvpcV2l/zxMNhbEEChVjB6o2D8na', '2024-11-12'),
(6, 'Gabriela', 'Pineda', 'Soto', '5543218765', 'gaby.pineda@icloud.com', '$2b$12$sNqmyozjtkHxqLNEmE9fZu6hvALpqa6q8MfYe0S.rPHu60k7.qKnO', '2025-01-10'),
(7, 'Mauricio', 'Castro', 'Ortiz', '3321098765', 'mau.castro@empresa.com', '$2b$12$1TRF1kc7Ml7DhyR1VgWhW.LljxiDQpgJ4SYd7v3zHcGp0XB0ZUCoe', '2025-02-18'),
(8, 'Fernanda', 'Montes', 'Ruiz', '8123456789', 'fer.montes@gmail.com', '$2b$12$8dEo4yW2IjfxFn4qksr6EOk2EjMypqvlaWynVB3MlHGU8BdfG.lqS', '2025-04-22'),
(9, 'Ricardo', 'Salinas', 'Paredes', '5589012345', 'ricardo.salinas@outlook.com', '$2b$12$eC67r6MDr93hBm92/7UW8OfnHcTPaWojfA4pU3uBM50ut.UIVYIgC', '2025-07-05'),
(10, 'Lucía', 'Gómez', 'Bautista', '3310987654', 'lucia.gomez@gmail.com', '$2b$12$/B3aS25tDuiWQailgugRguISCFgnCZUoZQWEqqK5nUnuHMt8Wv6MC', '2025-09-30'),
(11, 'Patricia', 'Sánchez', 'Mendoza', '5556789012', 'patricia.sanchez@gmail.com', '$2b$12$XwRpGP49EqLpHceVfx.spOz9iX.aSKCIIsKEgU6gOHcrPag7joEte', '2023-12-01');

INSERT INTO recompensa (codigo, nombre, descripcion) VALUES
('CUP50', 'Cupón de Descuento $50 MXN', 'Cupón digital aplicable en cualquier compra mínima de $150 MXN.'),
('BEB01', 'Bebida de Especialidad', 'Bebida artesanal o de temporada tamaño grande de cortesía en sucursal.'),
('POS01', 'Postre Gourmet de la Casa', 'Rebanada de pastel o postre de repostería fina a elección.'),
('BOL01', 'Tote Bag Ecológica Nexum', 'Bolsa reutilizable de algodón orgánico con diseño exclusivo Nexum Rewards.'),
('BON200', 'Bono Monedero $200 MXN', 'Bono de saldo electrónico directo para compras sin mínimo de consumo.');

INSERT INTO version_plan (num, fecha_inicio, fecha_final, precio, plazo_meses, aplica_en, plan, config_cashback, config_puntos, config_descuento, version_base_de_promo) VALUES
(1, '2024-01-01', '2024-12-31', 299.00, 6, 'AMBAS', 'BAS', 1, 1, 1, NULL),
(2, '2025-01-01', '2026-12-31', 499.00, 12, 'AMBAS', 'BAS', 2, 2, 2, NULL),
(3, '2024-01-01', '2025-12-31', 599.00, 6, 'AMBAS', 'PRE', 3, 3, 3, NULL),
(4, '2025-01-01', '2026-12-31', 999.00, 12, 'AMBAS', 'PRE', 4, 4, 4, NULL),
(5, '2025-01-01', '2027-12-31', 1599.00, 12, 'AMBAS', 'VIP', 5, 5, 5, NULL),
(6, '2026-11-01', '2026-12-31', 799.00, 12, 'RENOVACION', 'PRE', 6, 6, 6, 4);

INSERT INTO version_recompensa (num, fecha_inicio, fecha_final, costo_puntos, limite_canjes, recompensa) VALUES
(1, '2025-01-01', '2026-12-31', 100, 5, 'CUP50'),
(2, '2025-01-01', '2026-12-31', 150, 4, 'BEB01'),
(3, '2025-01-01', '2026-12-31', 250, 3, 'POS01'),
(4, '2025-01-01', '2026-12-31', 400, 2, 'BOL01'),
(5, '2025-01-01', '2026-12-31', 600, 1, 'BON200'),
(6, '2024-01-01', '2024-06-30', 120, 3, 'CUP50'),
(7, '2024-07-01', '2024-12-31', 110, 3, 'CUP50');

INSERT INTO membresia (num, fecha_contratacion, estado, miembro, version_plan_actual) VALUES
(1, '2024-01-10', 'ACTIVA', 1, 4),
(2, '2024-03-15', 'ACTIVA', 2, 4),
(3, '2024-05-20', 'ACTIVA', 3, 2),
(4, '2024-08-01', 'CANCELADA', 4, 5),
(5, '2024-11-12', 'CANCELADA', 5, 2),
(6, '2025-01-10', 'ACTIVA', 6, 4),
(7, '2025-02-18', 'CANCELADA', 7, 5),
(8, '2025-04-22', 'CANCELADA', 8, NULL),
(9, '2025-07-05', 'CANCELADA', 9, 2),
(10, '2025-09-30', 'CANCELADA', 10, 4),
(11, '2024-01-01', 'CANCELADA', 11, NULL),
(12, '2024-07-01', 'CANCELADA', 11, NULL),
(13, '2025-01-01', 'ACTIVA', 11, 2);

INSERT INTO usuario (num, nombre, primer_apellido, segundo_apellido, telefono, correo, `contraseña`, fecha_registro, rol) VALUES
(1, 'Jorge Manuel', 'Aguilera', 'Perez', '8115429810', 'jorge.aguilera@nexum.mx', '$2b$12$NW1tdD0jwE60dBeAgE4gFOxfNNNQyoXBJFIoEl4avpT4yhV0qhjJ.', '2024-01-01', 'ADM'),
(2, 'Luis Adolfo', 'Nieto', 'Aguilera', '5541829301', 'luis.nieto@nexum.mx', '$2b$12$FUsGwJSX5G11s31RkHKFIeAmQkh0prBznhn8OmxKgN1Ty9MDbWfBi', '2024-01-05', 'GER'),
(3, 'Ivan Manuel', 'Ruiz', 'Gonzales', '3312984570', 'ivan.ruiz@nexum.mx', '$2b$12$4OfYBlPGgUF3o49oadezVumtpS6kIYQtSgEOJa12J3GY8iao2neeq', '2024-01-15', 'CAJ'),
(4, 'Ana Sofía', 'Ramos', 'Gómez', '8182736450', 'ana.ramos@nexum.mx', '$2b$12$0cxib20SL9ShyQ6cdp4PXOxaWemzS2rBCxokBB0XRIBX300xYWf8a', '2024-02-01', 'CAJ'),
(5, 'Jorge Alberto', 'Morales', 'Ríos', '5523849102', 'jorge.morales@nexum.mx', '$2b$12$tWFPd6roL5MJ2837fy9hB.sIiSN4gQtQa/4rvo/BbJgoRICo91ZmC', '2024-03-01', 'CAJ');

INSERT INTO renovacion (num, fecha_pago, monto_pagado, fecha_inicio_periodo, fecha_fin_periodo, membresia, version_plan_comprado) VALUES
(1, '2024-01-10', 299.00, '2024-01-10', '2024-07-09', 1, 1),
(2, '2024-07-08', 299.00, '2024-07-10', '2025-01-09', 1, 1),
(3, '2025-01-08', 599.00, '2025-01-10', '2025-07-09', 1, 3),
(4, '2025-07-05', 599.00, '2025-07-10', '2026-01-09', 1, 3),
(5, '2026-01-05', 999.00, '2026-01-10', '2027-01-09', 1, 4),
(6, '2026-11-15', 799.00, '2027-01-10', '2028-01-09', 1, 6),
(7, '2024-03-15', 599.00, '2024-03-15', '2024-09-14', 2, 3),
(8, '2024-09-10', 599.00, '2024-09-15', '2025-03-14', 2, 3),
(9, '2025-03-12', 999.00, '2025-03-15', '2026-03-14', 2, 4),
(10, '2026-03-10', 999.00, '2026-03-15', '2027-03-14', 2, 4),
(11, '2024-05-20', 299.00, '2024-05-20', '2024-11-19', 3, 1),
(12, '2024-11-15', 499.00, '2024-11-20', '2025-11-19', 3, 2),
(13, '2025-11-15', 499.00, '2025-11-20', '2026-11-19', 3, 2),
(14, '2024-08-01', 1599.00, '2024-08-01', '2025-07-31', 4, 5),
(15, '2025-07-28', 1599.00, '2025-08-01', '2026-07-31', 4, 5),
(16, '2024-11-12', 499.00, '2024-11-12', '2025-11-11', 5, 2),
(17, '2025-01-10', 999.00, '2025-01-10', '2026-01-09', 6, 4),
(18, '2026-01-08', 999.00, '2026-01-10', '2027-01-09', 6, 4),
(19, '2025-02-18', 1599.00, '2025-02-18', '2026-02-17', 7, 5),
(20, '2025-04-22', 299.00, '2025-04-22', '2025-10-21', 8, 1),
(21, '2025-07-05', 499.00, '2025-07-05', '2026-07-04', 9, 2),
(22, '2025-09-30', 999.00, '2025-09-30', '2026-09-29', 10, 4),
(23, '2024-01-01', 299.00, '2024-01-01', '2024-06-30', 11, 1),
(24, '2024-07-01', 299.00, '2024-07-01', '2024-12-31', 12, 1),
(25, '2025-01-01', 499.00, '2025-01-01', '2025-12-31', 13, 2);

INSERT INTO compra (num, monto_base, porcentaje_descuento, descuento_nominal, cashback_aplicado, monto_final, membresia, usuario) VALUES
(1, 550.00, 0.15, 82.50, 0.00, 467.50, 1, 3),
(2, 820.00, 0.15, 123.00, 0.00, 697.00, 1, 4),
(3, 400.00, 0.15, 60.00, 20.00, 320.00, 1, 3),
(4, 1250.00, 0.15, 187.50, 0.00, 1062.50, 1, 5),
(5, 680.00, 0.15, 102.00, 0.00, 578.00, 1, 4),
(6, 950.00, 0.15, 142.50, 35.00, 772.50, 1, 3),
(7, 320.00, 0.15, 48.00, 0.00, 272.00, 1, 5),
(8, 1400.00, 0.15, 210.00, 50.00, 1140.00, 1, 4),
(9, 780.00, 0.15, 117.00, 0.00, 663.00, 1, 3),
(10, 1100.00, 0.15, 165.00, 0.00, 935.00, 1, 5),
(11, 630.00, 0.15, 94.50, 25.00, 510.50, 1, 4),
(12, 890.00, 0.15, 133.50, 0.00, 756.50, 1, 3),
(13, 600.00, 0.15, 90.00, 0.00, 510.00, 2, 3),
(14, 1200.00, 0.15, 180.00, 30.00, 990.00, 2, 4),
(15, 450.00, 0.08, 36.00, 0.00, 414.00, 3, 3),
(16, 1800.00, 0.20, 360.00, 0.00, 1440.00, 4, 5),
(17, 2200.00, 0.20, 440.00, 50.00, 1710.00, 4, 4),
(18, 520.00, 0.15, 78.00, 0.00, 442.00, 6, 3),
(19, 1650.00, 0.20, 330.00, 0.00, 1320.00, 7, 5),
(20, 380.00, 0.08, 30.40, 0.00, 349.60, 9, 4),
(21, 920.00, 0.15, 138.00, 0.00, 782.00, 10, 3);

INSERT INTO transaccion_puntos (num, movimiento, saldo, fecha, concepto, compra, version_recompensa, membresia) VALUES
(1, 100, 100, '2026-01-10', 'Bono inicial de fidelidad por renovación Premium', NULL, NULL, 1),
(2, 46, 146, '2026-01-18', 'Puntos acumulados por compra #1 (10% monto final)', 1, NULL, 1),
(3, 69, 215, '2026-02-10', 'Puntos acumulados por compra #2 (10% monto final)', 2, NULL, 1),
(4, 32, 247, '2026-03-05', 'Puntos acumulados por compra #3 (10% monto final)', 3, NULL, 1),
(5, -100, 147, '2026-03-10', 'Canje de recompensa: Cupón de Descuento $50 MXN', NULL, 1, 1),
(6, 106, 253, '2026-03-22', 'Puntos acumulados por compra #4 (10% monto final)', 4, NULL, 1),
(7, 58, 311, '2026-04-14', 'Puntos acumulados por compra #5 (10% monto final)', 5, NULL, 1),
(8, -150, 161, '2026-04-20', 'Canje de recompensa: Bebida de Especialidad', NULL, 2, 1),
(9, 77, 238, '2026-05-02', 'Puntos acumulados por compra #6 (10% monto final)', 6, NULL, 1),
(10, 27, 265, '2026-06-11', 'Puntos acumulados por compra #7 (10% monto final)', 7, NULL, 1),
(11, 114, 379, '2026-07-04', 'Puntos acumulados por compra #8 (10% monto final)', 8, NULL, 1),
(12, 66, 445, '2026-08-19', 'Puntos acumulados por compra #9 (10% monto final)', 9, NULL, 1),
(13, 93, 538, '2026-09-08', 'Puntos acumulados por compra #10 (10% monto final)', 10, NULL, 1),
(14, 51, 589, '2026-10-03', 'Puntos acumulados por compra #11 (10% monto final)', 11, NULL, 1),
(15, 75, 664, '2026-10-25', 'Puntos acumulados por compra #12 (10% monto final)', 12, NULL, 1),
(16, 51, 51, '2026-04-05', 'Puntos acumulados por compra #13', 13, NULL, 2),
(17, 99, 150, '2026-06-15', 'Puntos acumulados por compra #14', 14, NULL, 2),
(18, -100, 50, '2026-07-01', 'Canje de recompensa: Cupón de Descuento $50 MXN', NULL, 1, 2),
(19, 21, 21, '2026-02-20', 'Puntos acumulados por compra #15', 15, NULL, 3),
(20, 216, 216, '2026-03-10', 'Puntos acumulados por compra #16 (15% VIP)', 16, NULL, 4),
(21, 257, 473, '2026-05-18', 'Puntos acumulados por compra #17 (15% VIP)', 17, NULL, 4),
(22, -250, 223, '2026-06-01', 'Canje de recompensa: Postre Gourmet de la Casa', NULL, 3, 4),
(23, 44, 44, '2026-04-20', 'Puntos acumulados por compra #18', 18, NULL, 6),
(24, 198, 198, '2026-02-10', 'Puntos acumulados por compra #19', 19, NULL, 7),
(25, 17, 17, '2026-06-20', 'Puntos acumulados por compra #20', 20, NULL, 9),
(26, 78, 78, '2026-09-20', 'Puntos acumulados por compra #21', 21, NULL, 10),
(27, -100, 564, '2026-11-01', 'Canje de recompensa: Cupón de Descuento $50 MXN', NULL, 1, 1),
(28, -100, 464, '2026-11-10', 'Canje de recompensa: Cupón de Descuento $50 MXN', NULL, 1, 1);

INSERT INTO transaccion_cashback (num, monto, saldo, fecha, concepto, compra, membresia) VALUES
(1, 50.00, 50.00, '2026-01-10', 'Bono inicial de bienvenida cashback', NULL, 1),
(2, 23.38, 73.38, '2026-01-18', 'Cashback 5% generado en compra #1', 1, 1),
(3, 34.85, 108.23, '2026-02-10', 'Cashback 5% generado en compra #2', 2, 1),
(4, -20.00, 88.23, '2026-03-05', 'Cashback aplicado en pago de compra #3', 3, 1),
(5, 16.00, 104.23, '2026-03-05', 'Cashback 5% generado en compra #3', 3, 1),
(6, 53.13, 157.36, '2026-03-22', 'Cashback 5% generado en compra #4', 4, 1),
(7, 28.90, 186.26, '2026-04-14', 'Cashback 5% generado en compra #5', 5, 1),
(8, -35.00, 151.26, '2026-05-02', 'Cashback aplicado en pago de compra #6', 6, 1),
(9, 38.63, 189.89, '2026-05-02', 'Cashback 5% generado en compra #6', 6, 1),
(10, 13.60, 203.49, '2026-06-11', 'Cashback 5% generado en compra #7', 7, 1),
(11, -50.00, 153.49, '2026-07-04', 'Cashback aplicado en pago de compra #8', 8, 1),
(12, 57.00, 210.49, '2026-07-04', 'Cashback 5% generado en compra #8', 8, 1),
(13, 33.15, 243.64, '2026-08-19', 'Cashback 5% generado en compra #9', 9, 1),
(14, 46.75, 290.39, '2026-09-08', 'Cashback 5% generado en compra #10', 10, 1),
(15, -25.00, 265.39, '2026-10-03', 'Cashback aplicado en pago de compra #11', 11, 1),
(16, 25.53, 290.92, '2026-10-03', 'Cashback 5% generado en compra #11', 11, 1),
(17, 37.83, 328.75, '2026-10-25', 'Cashback 5% generado en compra #12', 12, 1),
(18, 25.50, 25.50, '2026-04-05', 'Cashback generado en compra #13', 13, 2),
(19, -20.00, 5.50, '2026-06-15', 'Cashback aplicado en compra #14', 14, 2),
(20, 49.50, 55.00, '2026-06-15', 'Cashback generado en compra #14', 14, 2),
(21, 115.20, 115.20, '2026-03-10', 'Cashback 8% VIP generado en compra #16', 16, 4),
(22, -50.00, 65.20, '2026-05-18', 'Cashback aplicado en compra #17', 17, 4),
(23, 136.80, 202.00, '2026-05-18', 'Cashback 8% VIP generado en compra #17', 17, 4);

COMMIT;

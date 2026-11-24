-- BASE DE DATOS NEXUM

CREATE DATABASE Nexum;
USE Nexum;

-- Crear la tabla config_cashback
CREATE TABLE config_cashback (
    num INT PRIMARY KEY AUTO_INCREMENT,
    porcentaje DECIMAL(10,2) NOT NULL,
    limite_min_mensual DECIMAL(10,2)
);

-- Crear la tabla config_puntos
CREATE TABLE config_puntos (
    num INT PRIMARY KEY AUTO_INCREMENT,
    porcentaje DECIMAL(10,2) NOT NULL,
    vigencia_meses INT
);

-- Crear la tabla config_descuento
CREATE TABLE config_descuento (
    num INT PRIMARY KEY AUTO_INCREMENT,
    porcentaje DECIMAL(10,2) NOT NULL,
    monto_minimo DECIMAL(10,2)
);

-- Crear la tabla dia_aplicable_desc
CREATE TABLE dia_aplicable_desc (
    config_descuento INT,
    dia_semana INT,
    PRIMARY KEY (config_descuento, dia_semana),
    CHECK (dia_semana IN (1, 2, 3, 4, 5, 6, 7)),
    FOREIGN KEY (config_descuento) REFERENCES config_descuento(num)
);

-- Crear la tabla plan
CREATE TABLE plan (
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(500)
);

-- Crear la tabla miembro
CREATE TABLE miembro (
    num INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    telefono VARCHAR(10) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    `contraseña` VARCHAR(255) NOT NULL,
    fecha_registro DATE NOT NULL
);

-- Crear la tabla recompensa
CREATE TABLE recompensa (
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500)
);

-- Crear la tabla rol
CREATE TABLE rol (
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(500)
);

-- Crear la tabla version_plan
CREATE TABLE version_plan (
    num INT PRIMARY KEY AUTO_INCREMENT,
    fecha_inicio DATE NOT NULL,
    fecha_final DATE NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    plazo_meses INT NOT NULL,
    aplica_en VARCHAR(25) NOT NULL,
    plan VARCHAR(10) NOT NULL,
    config_cashback INT UNIQUE,
    config_puntos INT UNIQUE,
    config_descuento INT UNIQUE,
    version_base_de_promo INT,
    CHECK (aplica_en IN ('CONTRATACION', 'RENOVACION', 'AMBAS')),
    CHECK (fecha_final >= fecha_inicio),
    FOREIGN KEY (plan) REFERENCES plan(codigo),
    FOREIGN KEY (config_cashback) REFERENCES config_cashback(num),
    FOREIGN KEY (config_puntos) REFERENCES config_puntos(num),
    FOREIGN KEY (config_descuento) REFERENCES config_descuento(num)
);

ALTER TABLE version_plan
ADD CONSTRAINT fk_version_plan_base_promo
FOREIGN KEY (version_base_de_promo) REFERENCES version_plan(num);

-- Crear la tabla version_recompensa
CREATE TABLE version_recompensa (
    num INT PRIMARY KEY AUTO_INCREMENT,
    fecha_inicio DATE NOT NULL,
    fecha_final DATE NOT NULL,
    costo_puntos INT NOT NULL,
    limite_canjes INT,
    recompensa VARCHAR(10) NOT NULL,
    FOREIGN KEY (recompensa) REFERENCES recompensa(codigo)
);

-- Crear la tabla membresia
CREATE TABLE membresia (
    num INT PRIMARY KEY AUTO_INCREMENT,
    fecha_contratacion DATE NOT NULL,
    estado VARCHAR(15) NOT NULL,
    miembro INT NOT NULL,
    version_plan_actual INT,
    CHECK (estado IN ('ACTIVA', 'SUSPENDIDA', 'CANCELADA')),
    FOREIGN KEY (miembro) REFERENCES miembro(num),
    FOREIGN KEY (version_plan_actual) REFERENCES version_plan(num)
);

-- Crear la tabla usuario
CREATE TABLE usuario (
    num INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    telefono VARCHAR(10),
    correo VARCHAR(150) NOT NULL UNIQUE,
    `contraseña` VARCHAR(255) NOT NULL,
    fecha_registro DATE NOT NULL,
    rol VARCHAR(10) NOT NULL,
    FOREIGN KEY (rol) REFERENCES rol(codigo)
);

-- Crear la tabla renovacion
CREATE TABLE renovacion (
    num INT PRIMARY KEY AUTO_INCREMENT,
    fecha_pago DATE NOT NULL,
    monto_pagado DECIMAL(10,2) NOT NULL,
    fecha_inicio_periodo DATE NOT NULL,
    fecha_fin_periodo DATE NOT NULL,
    membresia INT NOT NULL,
    version_plan_comprado INT NOT NULL,
    FOREIGN KEY (membresia) REFERENCES membresia(num),
    FOREIGN KEY (version_plan_comprado) REFERENCES version_plan(num)
);

-- Crear la tabla compra
CREATE TABLE compra (
    num INT PRIMARY KEY AUTO_INCREMENT,
    monto_base DECIMAL(10,2) NOT NULL,
    porcentaje_descuento DECIMAL(10,2) NOT NULL,
    descuento_nominal DECIMAL(10,2) NOT NULL,
    cashback_aplicado DECIMAL(10,2) NOT NULL,
    monto_final DECIMAL(10,2) NOT NULL,
    membresia INT NOT NULL,
    usuario INT NOT NULL,
    FOREIGN KEY (membresia) REFERENCES membresia(num),
    FOREIGN KEY (usuario) REFERENCES usuario(num)
);

-- Crear la tabla transaccion_puntos
CREATE TABLE transaccion_puntos (
    num INT PRIMARY KEY AUTO_INCREMENT,
    movimiento INT NOT NULL,
    saldo INT NOT NULL,
    fecha DATETIME NOT NULL,
    concepto VARCHAR(255),
    compra INT,
    version_recompensa INT,
    membresia INT NOT NULL,
    FOREIGN KEY (compra) REFERENCES compra(num),
    FOREIGN KEY (version_recompensa) REFERENCES version_recompensa(num),
    FOREIGN KEY (membresia) REFERENCES membresia(num)
);

-- Crear la tabla transaccion_cashback
CREATE TABLE transaccion_cashback (
    num INT PRIMARY KEY AUTO_INCREMENT,
    monto DECIMAL(10,2) NOT NULL,
    saldo DECIMAL(10,2) NOT NULL,
    fecha DATETIME NOT NULL,
    concepto VARCHAR(255),
    compra INT,
    membresia INT NOT NULL,
    FOREIGN KEY (compra) REFERENCES compra(num),
    FOREIGN KEY (membresia) REFERENCES membresia(num)
);

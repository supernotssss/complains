-- Active: 1681283610647@@127.0.0.1@3306@complains
-- phpMyAdmin SQL Dump
-- version 8.0.31
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 15-09-2021 a las 07:43:48
-- Versión del servidor: 10.4.6-MariaDB
-- Versión de PHP: 7.3.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `flask_login`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE users (
id INT(11) NOT NULL AUTO_INCREMENT,
name VARCHAR(100) NOT NULL,
email VARCHAR(100) NOT NULL,
username VARCHAR(30) NOT NULL,
password VARCHAR(100) NOT NULL,
register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);
--
-- Volcado de datos para la tabla `user`
--
CREATE TABLE articles (
id INT(11) NOT NULL AUTO_INCREMENT,
title VARCHAR(255) NOT NULL,
author VARCHAR(100) NOT NULL,
body TEXT NOT NULL,
create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (id)
);



INSERT INTO users (name, email, username, password) VALUES ('张三', 'zhangsan@example.com', 'zhangsan', '123456');

SELECT * FROM articles;



SELECT * FROM articles WHERE id = 1;



INSERT INTO articles (title, author, body) VALUES ('标题', 'zhangsan', '内容');
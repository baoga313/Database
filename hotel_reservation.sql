CREATE DATABASE IF NOT EXISTS hotel_reservation;
USE hotel_reservation;

CREATE TABLE `Guest` (
  `id` INT AUTO_INCREMENT,
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `email` VARCHAR(100),
  `phone_number` VARCHAR(15),
  PRIMARY KEY (`id`)
);

CREATE TABLE `Reservation` (
  `id` INT AUTO_INCREMENT,
  `guest_id` INT,
  `payment_status` VARCHAR(100) NOT NULL ,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`guest_id`) REFERENCES `Guest`(`id`)
);

CREATE TABLE `Room` (
  `id` INT AUTO_INCREMENT,
  `type` VARCHAR(100),
  `price_per_night` DECIMAL(10,2),
  `capacity` INT,
  PRIMARY KEY (`id`)
);

CREATE TABLE `Room_reservation` (
  `reservation_id` INT ,
  `room_id` INT,
  `check_in_date` DATE, 
  `check_out_date` DATE,
  `status` ENUM('Reserved', 'Check-in', 'Checked-out', 'Cancelled') NOT NULL,
  PRIMARY KEY (`reservation_id`,`room_id`),
  FOREIGN KEY (`reservation_id`) REFERENCES `Reservation`(`id`) ,
  FOREIGN KEY (`room_id`) REFERENCES `Room`(`id`)
);

CREATE TABLE `Vehicles` (
  `id` INT AUTO_INCREMENT,
  `type` VARCHAR(50),
  `brand` VARCHAR(50),
  `color` VARCHAR(40),
  `room_id` INT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`room_id`) REFERENCES `Room`(`id`)
);

CREATE TABLE `Payment` (
  `id` INT AUTO_INCREMENT,
  `reservation_id` INT,
  `payment_method` ENUM ('Credit Card', 'PayPal', 'Cash', 'Debit Card'),
  `status` VARCHAR(50),
  `payment_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`reservation_id`) REFERENCES `Reservation`(`id`)
);

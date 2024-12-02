CREATE DATABASE hotel_reservation;

USE hotel_reservation;

-- Guest Table
CREATE TABLE Guest (
    GuestID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(15),
    Password VARCHAR(255) NOT NULL
);

-- Room Table
CREATE TABLE Room (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    RoomType VARCHAR(50) NOT NULL,
    PricePerNight DECIMAL(10, 2) NOT NULL,
    Capacity INT NOT NULL
);

-- Vehicle Table
CREATE TABLE Vehicle (
    VehicleID INT AUTO_INCREMENT PRIMARY KEY,
    Brand VARCHAR(50) NOT NULL,
    Type VARCHAR(50) NOT NULL,
    Capacity INT NOT NULL
);

-- Reservation Table
CREATE TABLE Reservation (
    ReservationID INT AUTO_INCREMENT PRIMARY KEY,
    GuestID INT NOT NULL,
    Status ENUM('Pending', 'Reserved', 'Checked In', 'Cancelled') NOT NULL,
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID)
);

-- RoomReservation Table (Allows multiple rooms per reservation)
CREATE TABLE RoomReservation (
    RoomReservationID INT AUTO_INCREMENT PRIMARY KEY,
    ReservationID INT NOT NULL,
    RoomID INT NOT NULL,
    CheckInDate DATE NOT NULL,
    CheckOutDate DATE NOT NULL,
    Status ENUM('Pending', 'Reserved', 'Checked In', 'Cancelled') NOT NULL,
    Quantity INT NOT NULL,
    FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

-- VehicleReservation Table (Allows multiple vehicles per reservation)
CREATE TABLE VehicleReservation (
    VehicleReservationID INT AUTO_INCREMENT PRIMARY KEY,
    ReservationID INT NOT NULL,
    VehicleID INT NOT NULL,
    Quantity INT NOT NULL,
    FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID),
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID)
);

-- Payment Table (References RoomReservation for payment details)
CREATE TABLE Payment (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    ReservationID INT NOT NULL,
    PaymentMethod ENUM('Credit Card', 'Debit Card', 'PayPal') NOT NULL,
    Status ENUM('Pending', 'Completed', 'Cancelled') NOT NULL,
    PaymentDate DATE NOT NULL,
    TotalPrice DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID)
);

INSERT INTO Room (RoomType, PricePerNight, Capacity) VALUES
('King Room', 400, 2),
('Queen Room', 300, 2),
('Twin Room', 200, 2),
('Single Room', 100, 1);

INSERT INTO Vehicle (Brand, Type, Capacity) VALUES
('Honda', 'SUV', 5),
('Honda', 'Sedan', 4),
('Honda', 'MiniVan', 7),
('Toyota', 'SUV', 5),
('Toyota', 'Sedan', 4),
('Toyota', 'MiniVan', 7),
('BMW', 'SUV', 5),
('BMW', 'Sedan', 4),
('BMW', 'MiniVan', 7);
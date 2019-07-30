-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jul 30, 2019 at 08:47 PM
-- Server version: 5.7.23
-- PHP Version: 7.2.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fluencyboxdb`
--

DELIMITER $$
--
-- Procedures
--
DROP PROCEDURE IF EXISTS `p_GetAllUsers`$$
CREATE DEFINER=`Sanjay`@`%` PROCEDURE `p_GetAllUsers` ()  NO SQL
select FirstName, LastName, UserName from t_users$$

DROP PROCEDURE IF EXISTS `p_GetUserByUID`$$
CREATE DEFINER=`Sanjay`@`%` PROCEDURE `p_GetUserByUID` (IN `p_User_UID` VARCHAR(100))  NO SQL
BEGIN
SELECT User_UID, FirstName, LastName, Email_Address, PhoneNumber, CreatedOn from t_users where User_UID = p_User_UID;
END$$

DROP PROCEDURE IF EXISTS `p_GetValidUser`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `p_GetValidUser` (IN `p_Email_Address` VARCHAR(50))  NO SQL
BEGIN
SELECT User_UID, Password from t_users where Email_Address = p_Email_Address;
END$$

DROP PROCEDURE IF EXISTS `p_Registration`$$
CREATE DEFINER=`Sanjay`@`%` PROCEDURE `p_Registration` (IN `p_User_UID` VARCHAR(100), IN `p_FirstName` VARCHAR(50), IN `p_LastName` VARCHAR(50), IN `p_EmailAddress` VARCHAR(50), IN `p_Password` VARCHAR(100), IN `p_PhoneNumber` VARCHAR(25))  NO SQL
BEGIN
    IF (SELECT EXISTS (SELECT 1 FROM t_users WHERE Email_Address = p_EmailAddress) ) THEN
     
        SELECT '01';
     
    ELSE
     
        insert into t_users
        (
            User_UID,
            FirstName,
            LastName,
            Email_Address,
            Password,
            PhoneNumber
        )
        values
        (
            p_User_UID,
            p_FirstName,
            p_LastName,
            p_EmailAddress,
            p_Password,
            p_PhoneNumber
        );
     	SELECT '00';
    END IF;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `t_users`
--

DROP TABLE IF EXISTS `t_users`;
CREATE TABLE IF NOT EXISTS `t_users` (
  `UserID` int(11) NOT NULL AUTO_INCREMENT,
  `User_UID` varchar(100) NOT NULL,
  `FirstName` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `Username` varchar(25) DEFAULT NULL,
  `Email_Address` varchar(50) NOT NULL,
  `Password` varchar(100) NOT NULL,
  `PhoneNumber` varchar(25) NOT NULL,
  `ProfilePicture` varchar(100) DEFAULT 'DefaultPicture.jpg',
  `LastPasswordChangedOn` datetime DEFAULT NULL,
  `FailedLoginAttempts` int(11) NOT NULL DEFAULT '0',
  `IsLocked` tinyint(1) NOT NULL DEFAULT '0',
  `ChangePasswordOnNextLogon` tinyint(1) NOT NULL DEFAULT '0',
  `PasswordResetToken` varchar(100) DEFAULT NULL,
  `CreatedOn` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` int(11) DEFAULT NULL,
  `ModifiedOn` timestamp NULL DEFAULT NULL,
  `ModifiedBy` int(11) DEFAULT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `t_users`
--

INSERT INTO `t_users` (`UserID`, `User_UID`, `FirstName`, `LastName`, `Username`, `Email_Address`, `Password`, `PhoneNumber`, `ProfilePicture`, `LastPasswordChangedOn`, `FailedLoginAttempts`, `IsLocked`, `ChangePasswordOnNextLogon`, `PasswordResetToken`, `CreatedOn`, `CreatedBy`, `ModifiedOn`, `ModifiedBy`) VALUES
(1, 'fd7f12ee-5fbd-41b1-bb51-645f0aa8deb5', 'Sanjay', 'Mehta', 'Sanjay7', 'sanjum308@hotmail.com', 'hashed', '+254 724639000', 'DefaultPicture.jpg', NULL, 0, 0, 0, NULL, '2019-07-30 12:46:14', 1, NULL, NULL),
(2, 'a7554825-27e7-41df-9335-902b1c30ecac', 'Jitu', 'Mehta', 'Jitu7', 'ja_m2001@yahoo.com', 'hashed', '+254 722344777', 'DefaultPicture.jpg', NULL, 0, 0, 0, NULL, '2019-07-30 14:25:11', 1, NULL, NULL),
(3, 'd3151ed2-6ca5-4bfd-8904-21b4755f2aa6', 'Sapna', 'Mehta', NULL, 'sapu@hotmail.com', 'sha256$zqh53R5C$808992efb7f7cd6e2b03450de3da08a04be89261fc5e7b16b887023a38def73d', '+254 722818999', 'DefaultPicture.jpg', NULL, 0, 0, 0, NULL, '2019-07-30 15:47:37', NULL, NULL, NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

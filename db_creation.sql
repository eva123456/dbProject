SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `API` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `API` ;

-- -----------------------------------------------------
-- Table `API`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `API`.`User` (
  `idUser` INT NOT NULL AUTO_INCREMENT,
  `about` VARCHAR(100) DEFAULT '',
  `email` VARCHAR(50) NOT NULL DEFAULT '',
  `isAnonymous` TINYINT(1) NOT NULL DEFAULT false,
  `name` VARCHAR(50) DEFAULT '',
  `username` VARCHAR(50) DEFAULT '',
  PRIMARY KEY (`idUser`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;


-- -----------------------------------------------------
-- Table `API`.`Forum`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `API`.`Forum` (
  `idForum` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `short_name` VARCHAR(45) NOT NULL,
  `user` INT NOT NULL,
  PRIMARY KEY (`idForum`),
  INDEX `user_idx` (`user` ASC),
  CONSTRAINT `user`
    FOREIGN KEY (`user`)
    REFERENCES `API`.`User` (`idUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;


-- -----------------------------------------------------
-- Table `API`.`Thread`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `API`.`Thread` (
  `idThread` INT NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `dislikes` INT NOT NULL DEFAULT 0,
  `forum` INT NOT NULL,
  `isClosed` TINYINT(1) NOT NULL DEFAULT false,
  `isDeleted` TINYINT(1) NOT NULL DEFAULT false,
  `likes` INT NOT NULL DEFAULT 0,
  `message` TEXT NOT NULL,
  `points` INT NOT NULL DEFAULT 0,
  `posts` INT NOT NULL DEFAULT 0,
  `slug` VARCHAR(45) NOT NULL DEFAULT '',
  `title` VARCHAR(45) NOT NULL,
  `user` INT NOT NULL,
  PRIMARY KEY (`idThread`),
  INDEX `forum_idx` (`forum` ASC),
  INDEX `user_idx` (`user` ASC),
  CONSTRAINT `forum_key`
    FOREIGN KEY (`forum`)
    REFERENCES `API`.`Forum` (`idForum`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `user_key`
    FOREIGN KEY (`user`)
    REFERENCES `API`.`User` (`idUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;


-- -----------------------------------------------------
-- Table `API`.`Post`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `API`.`Post` (
  `idPost` INT NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `dislikes` INT NOT NULL DEFAULT 0,
  `forum` INT NOT NULL,
  `isApproved` TINYINT(1) NOT NULL DEFAULT false,
  `isDeleted` TINYINT(1) NOT NULL DEFAULT false,
  `isEdited` TINYINT(1) NOT NULL DEFAULT false,
  `isHighlighted` TINYINT(1) NOT NULL DEFAULT false,
  `isSpam` TINYINT(1) NOT NULL DEFAULT false,
  `likes` INT NOT NULL DEFAULT 0,
  `message` TEXT NOT NULL,
  `parent` INT NULL,
  `points` INT NOT NULL DEFAULT 0,
  `thread` INT NOT NULL,
  `user` INT NOT NULL,
  PRIMARY KEY (`idPost`),
  INDEX `forum_idx` (`forum` ASC),
  INDEX `user_idx` (`user` ASC),
  INDEX `thread_idx` (`thread` ASC),
  INDEX `parent_idx` (`parent` ASC),
  CONSTRAINT `p_forum_key`
    FOREIGN KEY (`forum`)
    REFERENCES `API`.`Forum` (`idForum`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `p_user_key`
    FOREIGN KEY (`user`)
    REFERENCES `API`.`User` (`idUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `p_thread_key`
    FOREIGN KEY (`thread`)
    REFERENCES `API`.`Thread` (`idThread`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `parent_key`
    FOREIGN KEY (`parent`)
    REFERENCES `API`.`Post` (`idPost`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `API`.`Follow`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `API`.`Follow` (
  `user` INT NOT NULL,
  `follower` INT NULL,
  `followee` INT NULL,
  `idFollow` INT NOT NULL AUTO_INCREMENT,
  INDEX `follower_idx` (`follower` ASC),
  INDEX `followee_idx` (`followee` ASC),
  INDEX `user_idx` (`user` ASC),
  PRIMARY KEY (`idFollow`),
  CONSTRAINT `follower_key`
    FOREIGN KEY (`follower`)
    REFERENCES `API`.`User` (`idUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `followee_key`
    FOREIGN KEY (`followee`)
    REFERENCES `API`.`User` (`idUser`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `follow_user_key`
    FOREIGN KEY (`user`)
    REFERENCES `API`.`User` (`idUser`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;


-- -----------------------------------------------------
-- Table `API`.`Subscriptions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `API`.`Subscriptions` (
  `user` INT NOT NULL,
  `subscription` INT NULL,
  `idSubscription` INT NOT NULL AUTO_INCREMENT,
  INDEX `user_idx` (`user` ASC),
  INDEX `subscription_idx` (`subscription` ASC),
  PRIMARY KEY (`idSubscription`),
  CONSTRAINT `s_user_key`
    FOREIGN KEY (`user`)
    REFERENCES `API`.`User` (`idUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `s_subscrpt_key`
    FOREIGN KEY (`subscription`)
    REFERENCES `API`.`Thread` (`idThread`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

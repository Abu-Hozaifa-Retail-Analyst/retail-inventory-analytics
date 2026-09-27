-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 01_create_database.sql
-- ============================================================
-- Creates the SQL Server database for this project.
-- Run this script connected to the 'master' database.
-- ============================================================

USE master;
GO

-- Drop-and-recreate pattern: makes this script safely re-runnable
-- during development (SSMS: run this whenever you want a clean
-- database), rather than erroring on a second run. Not something
-- you'd want in a production script -- flagged here deliberately
-- since it is destructive.
IF DB_ID(N'GulfMartRetailAnalytics') IS NOT NULL
BEGIN
    ALTER DATABASE GulfMartRetailAnalytics SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE GulfMartRetailAnalytics;
END
GO

CREATE DATABASE GulfMartRetailAnalytics
COLLATE SQL_Latin1_General_CP1_CI_AS;
GO

-- SIMPLE recovery model: minimal transaction-log overhead, the
-- right choice for an analytics database that is rebuilt from
-- source files rather than needing point-in-time log recovery.
ALTER DATABASE GulfMartRetailAnalytics SET RECOVERY SIMPLE;
GO

PRINT 'Database GulfMartRetailAnalytics created successfully.';
GO
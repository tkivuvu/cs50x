-- Keep a log of any SQL queries you execute as you solve the mystery.

-- 1.finding the description of the crime.
SELECT description, id, year, month, day, street
FROM crime_scene_reports
WHERE month = 7 AND day = 28
AND street = 'Humphrey Street';

-- 2.finding the names and transcipts of the people interviewed.
SELECT transcript, name
FROM interviews
WHERE month = 7 AND day = 28;

-- 3.finding info on the license plates that left the bakery within 10 min
-- of the crime.
SELECT activity, license_plate, hour, minute
FROM bakery_security_logs
WHERE month = 7 AND day = 28
AND hour = 10 AND minute BETWEEN 16 AND 26;

-- 4.finding the account numbers and amounts withdrawn of everyone that withdrew
-- money at the specific location mentioned in the interviews on the day of the crime.
SELECT account_number, amount
FROM atm_transactions
WHERE month = 7 AND day = 28
AND atm_location = 'Leggett Street'
AND transaction_type = 'withdraw';

-- 5.these are the names etc of people whose license plate left the bakery
-- within 10 minutes of the crime.
SELECT name, license_plate, passport_number, id
FROM people
WHERE license_plate IN ('5P2BI95', '94KL13X','6P58WS2'
,'4328GD8','G412CB7','L93JTIZ','322W7JE','0NTHK55');

-- 6.these are the callers and receivers that lasted less than a minute on the
-- day of the crime.
SELECT caller, receiver, duration
FROM phone_calls
WHERE month = 7 AND day = 28
AND duration < 60;

-- 7.finding the name, id, and abbreviation of the airport in the city of Fiftyville.
SELECT full_name, city, abbreviation, id
FROM airports
WHERE city = 'Fiftyville';

-- 8.finding earliest flights out of Fiftyville the day after the crime.
SELECT id, origin_airport_id, destination_airport_id,
hour, minute
FROM flights
WHERE month = 7 AND day = 29 AND year = 2024
AND origin_airport_id = 8;

-- 9.used numbers from callers (and then receivers in next query) that lasted less
-- than a min to find name, id and match number plates from bakery who left within 10min of crime.
SELECT name, id
FROM people
WHERE phone_number
IN ('(130) 555-0289','(499) 555-9472',
'(367) 555-5533','(499) 555-9472','(286) 555-6063',
'(770) 555-1861','(031) 555-6622','(826) 555-1652',
'(338) 555-6650');

-- 10.similar to previous query but this one deals with receivers not callers to find
-- the accomplice.
SELECT name, phone_number, passport_number, id
FROM people
WHERE phone_number
IN ('(996) 555-8899','(892) 555-8872',
'(375) 555-8161','(717) 555-1342','(676) 555-6554',
'(725) 555-3243','(910) 555-3251','(066) 555-9701',
'(704) 555-2131');

-- 11.join tables for bank accounts and for people to see if they match suspects.
SELECT name, id, phone_number, passport_number
FROM people
JOIN bank_accounts ON people.id = bank_accounts.person_id
WHERE account_number IN (28500762,28296815,76054385,
49610011,16153065,25506511,81061156,26013199);

-- 12.finding the four phone numbers of my main suspects.
SELECT name, phone_number
FROM people
WHERE id IN (398010,514354,560886,686048)

-- 13.finding the destination airport from the earliest flight out
-- the day after the crime.
SELECT DISTINCT airports.id, abbreviation, full_name, city
FROM airports
JOIN flights ON airports.id = flights.destination_airport_id
WHERE airports.id = 4;

-- 14.finding the passengers on flight_id 36 as this is the first
-- flight out the next day after the crime and matching them to
-- passport numbers I gathered from my 4 main suspects.
SELECT people.name, passengers.passport_number,
passengers.seat
FROM passengers
JOIN people ON passengers.passport_number = people.passport_number
WHERE flight_id = 36
ORDER BY seat ASC;







-- this is for 9.txt namely finding the names, id of the callers
-- from the timeframe stated in the info from interviews.
-- as per cs50AI this is the one way you can make sure to include
-- a repeated number as in (499) 555-9472 which is both the second
-- and fourth number the other way (as in query 10) would only produce it once

SELECT name, id
FROM people
WHERE phone_number = '(130) 555-0289'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(499) 555-9472'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(367) 555-5533'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(499) 555-9472'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(286) 555-6063'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(770) 555-1861'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(031) 555-6622'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(826) 555-1652'
UNION ALL
SELECT name, id
FROM people
WHERE phone_number = '(338) 555-6650';

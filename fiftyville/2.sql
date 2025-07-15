SELECT people.name, passengers.passport_number,
passengers.seat
FROM passengers
JOIN people ON passengers.passport_number = people.passport_number
WHERE flight_id = 36
ORDER BY seat ASC;

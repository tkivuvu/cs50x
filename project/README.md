# NBA STATS HUB (WEB APP)
#### Video Demo:  <https://youtu.be/nJ7tGkmkohQ>
#### Description:
I have built a web app that displays real-time NBA stats using data from a public API. The project was built with Flask, SQL, JavaScript, and styled with HTML/CSS. I will first describe what is in my helpers.py which mostly consists of the retrieval process from the API then I will discuss the programming of the templates in my app.py, which on the other hand, has to do with the way in which I am displaying the retrieved data, and finally I will touch on the html templates themselves and the css that styles them.


My helpers.py module manages data retrieval and caching for the web application. It connects to the NBAAPI.COM API to fetch player statistics across four key categories: regular season totals, regular season advanced stats, playoff totals, and playoff advanced stats.


At the core of the module is the initiaze_db() function, which creates and manages a local SQLite database (nba_cache.db) with four distinct tables for each stat type. This enables efficient caching and reduces repeat API calls by storing and reusing data with a 24-hour window.


Each fetch_ function -- fetch_player_totals(), fetch_player_advanced(), fetch_playoff_totals(), and fetch_advanced_playoffs() -- uses the tenacity retry decorator to ensure a form of defense against temporary API failures. These functions:
   - Query the external NBA API for player data by name and season.
   - Check for existing cached results to minimize external requests.
   - Store new or updated results into the database.
   - Return both a "combined" team view (e.g for players traded mid-season) and full team-by-team data where applicable.


Additionally, a custom error() helper renders user-friendly error messages using an error.html template.


By handling API access, caching, error handling, and data structuring, this module forms the backend foundation of the application's stat lookup system and ensures fast, reliable, user queries across historical NBA seasons.


The app.py file serves as the core backend of the application, built using Flask. It handles routing, form submission, data retrieval, and rendering of templates for various player statistics features.


The application allows users to search and visualize NBA player data across multiple categories:
   - Player Totals (Regular Season & Playoffs): View traditional box score stats like points, rebounds, and assists with automatic per-game and percentage calculations.
   - Advanced Stats (Regular Season & PLayoffs): Access advanced metrics such as true shooting percentage, free throw rate, and minutes per game, with support for players who've played on multiple teams in a season.
   - Shot Distribution: Displays how a player's scoring attempts are distributed across three-point shots, two-point shots, and free throws.
   - Quick Access Tool: Provides a fast way to navigate directly to a player's page using only their name and season.


Each POST route handles input validation (player name and season), fetches data via utility functions (e.g, fetch_player_totals, fetch_advanced_playoffs), processes the raw stats into meaningful metrics, and returns the appropriate HTML template. Players in the Hall of Fame are also identified using a trailing asterisk convention which comes from the API.


GET requests load search forms, while POST requests process and display the results.


The way in which I have designed my code is modular and robust, supporting broad uses (e.g, new endpoints, more metrics) while maintaining a clean separation between logic, data, and presentation layers.


I have many templates in my project so I will not be talking about each one of them as there are close to 20 of them, however, I will discuss the overall presentation of them and will discuss two in particular as they all follow this similar pattern.


My templates directory is well organized and follows a clean, modular structure using jinja2 templating. At its core is layout.html, which serves as a base template. It defines a consistent layout across all pages, featuring a Bootstrap-powered responsive navbar, a dynamic title block, and a main content container using {% block main %}. It also includes custom styles, Google Fonts, and a footer crediting the data source.


Each individual page template extends layout.html and fills in the defined blocks. For instance, index.html acts as a homepage dashboard, giving users a friendly entry point to different features. It uses Bootstrap cards to link out to core app functionalities like player totals, advanced stats, playoff stats, player comparisons, and shot distribution. It essentially serves as a feature map.


Templates like player_shot_distribution_search.html and player_shot_distribution.html illustrate a typical search-display pattern. The search template renders a form to submit player name and season, while the result template shows a pie chart (served by a backend route) alongside key shot attempt breakdowns. This pattern is mirrored for other stat types and visualizations, making the user interaction feel consistent and predictable.


Navigation is intuitive thanks to the dropdowns in the navbar and embedded quick search. Flask messaging support is included, and each view keeps a clear visual hierarchy using Bootstrap components. Overall, the templates work together to deliver a cohesive, interactive user experience, enabling users to move seamlessly between search, data, and visual analysis.


Finally, as it pertains to my css styling, it is a clean NBA-themed aesthetic using custom color variables (--nba-blue, --nba-red, --court-color). The page background features a soft gradient, and the Roboto Condensed font is used site-wide for a modern, sporty feel.
   - The navbar uses NBA-themed colors with hover effects that turn red.
   - Buttons (.btn) change text color on hover for interactivity.
   - Card elements (.stat-card, .stats-card) have smooth hover animations for depth and emphasis.
   - Text headings and paragraphs inside containers are mostly center-aligned, while .card-text remains left-aligned.
   - .center-error is a utility class designed to center vertically and horizontally, mainly used for error displays.
Overall, the styles aim to balance clarity, responsiveness, and a polished NBA-branded user experience.


Finally, I have included in my code comments pertaining to what is happening in parts of the code (including any use of A.I) and also comments that make it more readable by separating by categories how my code is structured. A requirements.txt also lists a few number of libraries/modules that are needed to run the program.




# Book Review Web Application

In this web app, users are able to register for the website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. The web application also uses the a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users are able to query for book details and book reviews programmatically via the website’s API.

### API usage:
Going to route `/api/<isbn>` where `<isbn>` is an ISBN number

returns a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. 

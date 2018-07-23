# Book Review Web Application

In this web app, users are able to register for the website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. The web application also uses the a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users are able to query for book details and book reviews programmatically via the website’s API.

### How to run
<ul>
  <li> pip3 install -r requirements.txt </li> <br> 
  
  <li> export DATABASE_URL=postgres://fsjyxeeokidnbn:4e5b26c98b0e36de49b6f907fd4bdf591acade7a39ebe190f9a644e5419d7080@ec2-184-73-199-189.compute-1.amazonaws.com:5432/ddlj6unc26nb4e </li> <br> 

  <li> export FLASK_APP=application.py </li> <br> 

  <li> flask run </li> <br> 
</ul>

### API usage
Going to route `/api/<isbn>` where `<isbn>` is an ISBN number

returns a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. 

### Demo
![alt text](https://github.com/ibmlih/bookreview/blob/master/demo.png)

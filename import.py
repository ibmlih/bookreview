import csv, os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def main():
    # Set up database
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))

    with open("books.csv", "r") as f:
        reader = csv.reader(f)

        # Skip the first line
        next(reader)

        # Insert into database
        for isbn, title, author, year in reader:
            db.execute('INSERT INTO "book" ("isbn", "title", "author", "year") VALUES (:isbn, :title, :author, :year)',
                {"isbn":isbn, "title":title, "author":author, "year":year})
            print("Added a row.")

        db.commit()


if __name__ == '__main__':
    main()

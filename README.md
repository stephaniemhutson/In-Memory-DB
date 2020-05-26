# In memory database
Stephanie Hutson, 2020-05-26

This in memory database is a python script which will allow you to `GET`, `SET`,
`COUNT` and `DELETE` data.

## How to Use

Run the following command:

`python app.py [optional:path/to/database.csv]`

If you do not submit a path to a csv file, the database csv (`db.csv`) that is in
this directory will be used.

### Commands:

`GET [key]`
Gets the value from the database. Any whitespace around the keys or values will
be ignored.

`SET [key] [value]`
Sets the value to a certain key in the database. If the key already exists it
will replace the value, if it does not a new row will be added.

`DELETE [key]`
Deletes the row from the database that has the key.

`COUNT [value]`
Gets the number of keys set to the given value

`END`
Ends the program and makes final changes to the database file. If any changes
exist in a transaction that has not been committed, they will not be saved.

`BEGIN`
Begins a transaction.

`COMMIT`
Closes a transaction and saves the state of the changes made to the database.

`ROLLBACK`
Closes a transaction and reverts the data to before the transaction was begun.

If you exit using a keyboard interruption, all changes made that are not still
within a transaction will be saved to the database file.

## Limitations

In order to keep the speed of getting/setting/counting up we do some
preprocessing on database load, and wait to save to the old db file until either
a commit or you exit the program.

What this means is the following:

 - If your database is large (over a million rows), there will be a delay on
   database load, save, and commit.
 - If you have the database open in multiple places on your machine, changes
   made to the database in one instance will not be visible to the other
   instance until either a commit or the program has exited.

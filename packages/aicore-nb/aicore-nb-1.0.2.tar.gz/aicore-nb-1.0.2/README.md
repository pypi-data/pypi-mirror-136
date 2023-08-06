# Teaching Tools

Run `python aicore_nb_tool` in your terminal and let the magic happen.

You can also install the package to work in any directory and without worrying about dependencies. Simply run `pip install aicore-nb-tools`, and once installed run `python -m aicore_nb_tool`. It will ask you for the API token, please, ask the team how to get one.

The script connects to an S3 bucket with the questions. Those questions are stored usign the lesson id, and in order to get those ids, it connects to an RDS to make a query to check it.
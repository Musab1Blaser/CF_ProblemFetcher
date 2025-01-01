# CF_ProblemFetcher
Return a list of codeforces problems of specified ratings, that are unsolved by a group of users. Ideal for ensuring fairness when creating contests.

## How to Use
1. Install required libraries using `pip install -r requirements.txt`
2. In <strong>search_unsolved.py</strong>:
    - In main, update list of users with your list of users (codeforces handles)
    - In main, update ratings list to contain the problem ratings you want to filter by
3. Now run.

## Tip
If you want to further filter by tags, you can do so in the resulting .xlsx file
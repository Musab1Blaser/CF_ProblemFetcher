import requests
import time
import pandas as pd

def fetch_user_status(handle):
    """Fetch the problem statuses for a given user."""
    try:
        response = requests.get(f"https://codeforces.com/api/user.status?handle={handle}")
        time.sleep(0.5)  # To avoid hitting the rate limit
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            return data['result']
        else:
            print(f"Error fetching data for {handle}: {data.get('comment', 'Unknown error')}")
    except requests.RequestException as e:
        print(f"Request failed for {handle}: {e}")
    return []

def fetch_problemset():
    """Fetch the list of problems from Codeforces."""
    try:
        response = requests.get("https://codeforces.com/api/problemset.problems")
        time.sleep(0.5)  # To avoid hitting the rate limit
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            return data['result']['problems']
        else:
            print("Error fetching problemset: " + data.get('comment', 'Unknown error'))
    except requests.RequestException as e:
        print(f"Request failed for problemset: {e}")
    return []

def get_unsolved_problems(users, ratings):
    """Find unsolved problems for the given users for each rating in ratings."""
    problemset = fetch_problemset()
    if not problemset:
        return {}

    problems_by_rating = {
        rating: {
            (problem['contestId'], problem['index']): problem
            for problem in problemset if problem.get('rating') == rating and 'contestId' in problem
        }
        for rating in ratings
    }

    solved_problems = set()
    for user in users:
        submissions = fetch_user_status(user)
        for submission in submissions:
            problem = submission['problem']
            if 'contestId' in problem and 'rating' in problem:
                solved_problems.add((problem['contestId'], problem['index']))

    unsolved_problems_by_rating = {
        rating: [
            problem for key, problem in problems.items()
            if key not in solved_problems
        ]
        for rating, problems in problems_by_rating.items()
    }
    return unsolved_problems_by_rating

def save_to_excel(unsolved_problems_by_rating, filename="unsolved_problems.xlsx"):
    """Save the unsolved problems to an Excel file with each rating on a different sheet."""
    with pd.ExcelWriter(filename) as writer:
        for rating, problems in unsolved_problems_by_rating.items():
            df = pd.DataFrame(problems)
            if 'points' in df.columns:
                df = df.drop(columns=['points'])
            df['link'] = df.apply(lambda row: f'=HYPERLINK("https://codeforces.com/contest/{row['contestId']}/problem/{row['index']}")', axis=1)
            df.to_excel(writer, sheet_name=f"Rating {rating}", index=False)

def main():
    users = ["tourist", "Benq", "rainboy"]
    users = [user.strip() for user in users]
    ratings = [1300, 1500, 1700, 1900, 2100, 2300]

    unsolved_problems_by_rating = get_unsolved_problems(users, ratings)
    save_to_excel(unsolved_problems_by_rating)

    # for rating, unsolved_problems in unsolved_problems_by_rating.items():
    #     if unsolved_problems:
    #         print(f"Unsolved problems of rating {rating} for users {', '.join(users)}:")
    #         for problem in unsolved_problems:
    #             print(f"{problem['contestId']}{problem['index']} - {problem['name']}")
    #     else:
    #         print(f"No unsolved problems of rating {rating} found for users {', '.join(users)}.")

if __name__ == "__main__":
    main()
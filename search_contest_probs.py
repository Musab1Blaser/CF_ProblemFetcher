import requests
import time
import pandas as pd

def fetch_problems_by_div(contests_by_div):
    """Fetch the list of problems for a specific division from Codeforces."""
    try:
        response = requests.get("https://codeforces.com/api/problemset.problems")
        time.sleep(0.5)  # To avoid hitting the rate limit
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            problems = data['result']['problems']
            problems_by_div = {div: [problem for problem in problems if problem['contestId'] in contests] for div, contests in contests_by_div.items()}
            return problems_by_div
        else:
            print("Error fetching problemset: " + data.get('comment', 'Unknown error'))
    except requests.RequestException as e:
        print(f"Request failed for problemset: {e}")
    return []

def get_contests(divs):
    """Fetch the list of contests from Codeforces."""
    try:
        response = requests.get("https://codeforces.com/api/contest.list")
        time.sleep(0.5)  # To avoid hitting the rate limit
        response.raise_for_status()
        data = response.json()
        contests = data['result']
        if data['status'] == 'OK':
            contests_by_div = {div: {contest['id']: contest['name'] for contest in contests if (f'Div. {div}' in contest['name'])} for div in divs}
            return contests_by_div
        else:
            print("Error fetching contests: " + data.get('comment', 'Unknown error'))
    except requests.RequestException as e:
        print(f"Request failed for contests: {e}")
    return []

def save_problems_to_excel(problems_by_div, contests_by_div, filename="problems_by_div.xlsx"):
    """Save the problems to an Excel file with each division on a different sheet."""
    with pd.ExcelWriter(filename) as writer:
        for div, problems in problems_by_div.items():
            contest_names = contests_by_div[div]
            data = []
            for problem in problems:
                contest_name = contest_names.get(problem['contestId'], 'Unknown Contest')
                problem_id = f"{problem['contestId']}{problem['index']}"
                problem_link = f'https://codeforces.com/contest/{problem["contestId"]}/problem/{problem["index"]}'
                data.append({
                    'Contest Name': contest_name,
                    'Problem ID': problem_id,
                    'Rating': problem.get('rating', 'Unrated'),
                    'Problem Title': f'=HYPERLINK("{problem_link}", "{problem["name"]}")',
                    'Tags': ', '.join(problem.get('tags', []))
                })
                
            # Recent problems first, A before B
            df = pd.DataFrame(data)
            df['Contest ID'] = df['Problem ID'].str.extract(r'(\d+)').astype(int)
            df['Problem Index'] = df['Problem ID'].str.extract(r'(\D+)$')
            df = df.sort_values(by=['Contest ID', 'Problem Index'], ascending=[False, True])
            df = df.drop(columns=['Contest ID', 'Problem Index'])
            df.to_excel(writer, sheet_name=f"Div {div}", index=False)

def main():
    divs = [3, 4]
    
    # Fetch contests by division
    contests_by_div = get_contests(divs)
    
    # Fetch problems by division
    problems_by_div = fetch_problems_by_div(contests_by_div)
    
    # Save problems to Excel
    save_problems_to_excel(problems_by_div, contests_by_div)

if __name__ == "__main__":
    main()
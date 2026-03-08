import openai
from openai import OpenAI

# Read diff file
with open('diff.txt', 'r') as file:
    diff = file.read()

# Query Chat-GPT
# Don't need to set api key here as long as OPENAI_API_KEY is set in environment variable
client = OpenAI()

try:
    completion = client.chat.completions.create(
        messages=[
            {'role': 'system',
             'content': 'Act as a senior software engineer conducting a code review on a django project.'
                        'Provide concise and actionable feedback.',
             },
            {'role': 'user',
             'content': 'Provide concise, actionable feedback in Markdown format, paying special attention'
                        'to Django convention, security, and code efficiency, and in each case mentioning the'
                        f'file name and line number for the suggestion. Here\'s the pull request diff:\n{diff}',
             },
        ],
        model='o3',
    )
    feedback = completion.choices[0].message.content
    print(feedback)

# Handle potential errors when querying OpenAI
except openai.APIConnectionError as e:
    print('Connection could not be established.')
    print(e.__cause__)
    feedback = '***Connection Not Established***\n\nNo AI code review available.'

except openai.RateLimitError:
    print('AI Code Review is unavailable rate limit occured.')
    feedback = '***Quota Exceeded***\n\nNo AI code review available.'

except openai.APIStatusError as e:
    print("Error occured when trying to query OpenAI")
    print(e.status_code)
    print(e.response)
    print(e.message)
    feedback = f'***{e.message}***\n\nNo AI code review available.'

# remove beginning code block
feedback = feedback.replace('```markdown', '')  # remove code markdown code blocks
feedback = feedback.replace('```', '')  # remove instances of code blocks

with open("feedback.md", "w") as file:
    file.write(f'## AI Code Review Feedback\n{feedback}')

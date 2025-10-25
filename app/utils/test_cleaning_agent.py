import pandas as pd
from app.utils.cleaning_tools import get_cleaning_agent  # Import the function from your cleaning_tools.py

# Create a sample DataFrame for testing
df = pd.DataFrame({
    'A': [1, 2, None, 4],
    'B': ['a', 'b', 'c', 'd'],
    'C': [None, 2.5, 3.5, None]
})

# Initialize the cleaning agent
agent = get_cleaning_agent(df)

# Run the agent (it should execute the tools based on your mock LLM)
result = agent.run("Clean the data")  # Or any prompt that you want to test

# Print the result
print(result)

# Optionally, print the cleaned DataFrame to check the actual changes
print("\nCleaned DataFrame:")
print(df)

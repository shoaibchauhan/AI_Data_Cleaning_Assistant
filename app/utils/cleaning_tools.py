from langchain.tools import tool
import pandas as pd
import numpy as np

# 1️⃣ Fill missing values
def fill_missing_values(df: pd.DataFrame):
    string_cols = df.select_dtypes(include=["object"]).columns
    for col in string_cols:
        df[col] = df[col].fillna("Unknown")  # Fill string missing values
    # Numeric columns (int, float) remain NaN
    return df

# 2️⃣ Remove duplicates
def remove_duplicates(df: pd.DataFrame):
    df = df.drop_duplicates(subset=["email", "signup_date"], keep="first").reset_index(drop=True)
    return df

# 3️⃣ Normalize strings
def normalize_strings(df: pd.DataFrame):
    string_cols = df.select_dtypes(include=["object"]).columns
    for col in string_cols:
        if col == "name":
            df[col] = df[col].str.title().str.strip()  # Capitalize names
        elif col == "email":
            df[col] = df[col].str.lower().str.strip()  # Lowercase emails
    return df

# Cleaning agent using the three main points
class MockCleaningAgent:
    def __init__(self, df: pd.DataFrame):
        self.df = df

        @tool
        def missing_value_tool(input: str) -> str:
            """Fills missing values in string columns with 'Unknown', keeps numeric NaN"""
            fill_missing_values(self.df)
            return "✅ Missing values handled ('Unknown' for strings, NaN for numeric)"

        @tool
        def duplicate_remover(input: str) -> str:
            """Removes duplicate rows based on email + signup_date"""
            self.df = remove_duplicates(self.df)
            return "✅ Duplicates removed"

        @tool
        def format_normalizer(input: str) -> str:
            """Normalizes string columns (capitalize names, lowercase emails)"""
            normalize_strings(self.df)
            return "✅ String columns normalized"

        self.tools = [missing_value_tool, duplicate_remover, format_normalizer]

    def run(self, prompt: str):
        print("🤖 AI Agent Starting Data Cleaning Process...\n")
        results = []

        for i, tool in enumerate(self.tools, 1):
            print(f"📋 Step {i}: Using {tool.name} - {tool.description}")
            result = tool.invoke("execute")
            results.append(result)
            print(f"   {result}\n")

        print("✨ All data cleaning operations completed successfully!\n")
        return self.df

# Function to get the cleaning agent
def get_cleaning_agent(df: pd.DataFrame):
    return MockCleaningAgent(df)

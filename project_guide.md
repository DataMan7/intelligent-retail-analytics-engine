BigQuery AI - Building the Future of Data
Build AI solutions with BigQuery


BigQuery AI - Building the Future of Data

View Writeups
This competition requires identity verification
To submit to this competition, you'll need to verify your identity. Learn More


Verify now
Overview
We challenge you to go beyond traditional analytics and build groundbreaking solutions using BigQuery's cutting-edge AI capabilities. This is your opportunity to solve real-world business problems using BigQuery’s Generative AI, Vector Search, and Multimodal capabilities.

Start

a month ago
Close
7 days to go
Description
Companies are sitting on piles of data, including chat logs, PDFs, screenshots, and recordings, but they can’t do much with it. Existing tools are typically built for just one data format, or they require too much manual work. This makes it hard to find patterns, generate content, or even answer basic questions.

Your task is to build a working prototype that uses BigQuery’s AI capabilities to process unstructured or mixed-format data. That might mean pulling up similar documents from a giant text archive, creating summaries on the fly, or stitching together insights from messy, mixed data. Whatever you build, the idea is to solve a real problem using tools that feel like an extension of SQL, not a separate system.

You’ll have access to public datasets, and you’re welcome to bring your own as long as they’re publicly available. The goal is to demonstrate how AI within BigQuery can address real-world problems that go beyond rows and columns.

Whether you submit a demo, a notebook, or a walkthrough, we want to see how you utilize these tools to make sense of data that is often overlooked.

Submission Requirements
The challenge offers three approaches. You must use at least one approach, but you may use two or all three. Submissions are only eligible for one prize. Inspiration is provided for each approach, but should be considered as the type of project that would be considered a great application.

Approach 1: The AI Architect 🧠
Your Mission: Use BigQuery's built-in generative AI to architect intelligent business applications and workflows. Build solutions that can generate creative content, summarize complex information, or even forecast future trends directly within your data warehouse.

Your Toolbox (Must use at least one):

Generative AI in SQL:
ML.GENERATE_TEXT: The classic function for large-scale text generation.
AI.GENERATE: Generate free-form text or structured data based on a schema from a prompt.
AI.GENERATE_BOOL: Get a simple True/False answer about your data.
AI.GENERATE_DOUBLE: Extract a specific decimal number from text.
AI.GENERATE_INT: Extract a specific whole number from text.
AI.GENERATE_TABLE: Create a structured table of data from a single prompt.
AI.FORECAST: Predict future values for time-series data with a single function.
Generative AI in BigFrames (Python):
bigframes.ml.llm.GeminiTextGenerator: Leverage the power of Gemini models in your Python workflows.
bigframes.DataFrame.ai.forecast(): Run powerful forecasting models directly on your DataFrames.
Inspiration:

Build a Hyper-Personalized Marketing Engine: Generate unique marketing emails for every customer based on their individual purchase history and preferences.
Create an Executive "Insight" Dashboard: Develop a dashboard that automatically ingests raw support call logs and transforms them into summarized, categorized, and actionable business insights.
Approach 2: The Semantic Detective 🕵️‍♀️
Your Mission: Go beyond keyword matching and uncover deep, semantic relationships in your data using BigQuery's native vector search. Build systems that understand meaning and context to find similar items, concepts, or issues with incredible accuracy.

Your Spy Kit (Must use at least one):

Vector Search in SQL:

ML.GENERATE_EMBEDDING: Transform your data (text, images) into meaningful vector representations.
VECTOR_SEARCH: The core function to find items based on meaning, not just keywords. Can be used with or without a vector index.
CREATE VECTOR INDEX: Build an index for speeding up similarity search on larger tables (1 million rows or above)
Vector Search in BigFrames (Python):

bigframes.ml.llm.TextEmbeddingGenerator(): Create embeddings seamlessly in your Python environment.
bigframes.bigquery.create_vector_index(): Build a vector index programmatically using Python.
bigframes.bigquery.vector_search(): Query your vector index using the BigFrames API.
Inspiration:

Develop an Intelligent Triage Bot: Instantly find historical support tickets that are semantically similar to a new, incoming ticket to speed up resolution time. The bot may also recommend a solution based on past ticket resolutions.
Design a "Smart Substitute" Recommender: Suggest ideal product substitutes based on a deep understanding of product attributes, not just shared tags or categories.
Approach 3: The Multimodal Pioneer 🖼️
Your Mission: Break the barriers between structured and unstructured data using BigQuery's multimodal capabilities. Combine numerical and categorical data with images, documents, and other rich media to unlock insights that are impossible to find in siloed datasets.

Your Palette (Must use at least one):

Multimodal Features in SQL:
Object Tables: Create a structured SQL interface over your unstructured files in Cloud Storage.
ObjectRef: A data type that lets you reference and pass unstructured data to AI models.
Multimodal Features in BigFrames (Python):
BigFrames Multimodal Dataframe: Natively load, transform, and analyze mixed data types (text, images, tables) together.
Inspiration:

Revolutionize Real Estate Valuation: Improve property price predictions by fusing structured data (e.g., sqft, # of bedrooms) with unstructured data from street-level and satellite imagery.
Build an Automated Quality Control Agent: Detect discrepancies between a product's listed specifications, its marketing description, and its actual product image.
Submission Instructions
A submission is comprised of the following:

Kaggle Writeup
Attached Public Notebook
Attached Public Video (optional)
Attached User Survey (optional)
1. Kaggle Writeup
Your submission must be a Kaggle Writeup and it must be attached to this competition page.

Ensure you address the following sections in your writeup.

Project Title: A creative and descriptive name for the project.
Problem Statement: A brief, one-paragraph summary of the hackathon problem you are solving.
Impact Statement: A brief summary on what material impact the solution achieves.
To create a new Writeup, click on the "New Writeup" button here. After you have saved your Writeup, you should see a "Submit" button in the top right corner.

Each team is limited to submitting only a single Writeup, but that same Writeup can be un-submitted, edited, and re-submitted as many times as you'd like. Your Writeup should contain a summary of your overall project along with links to supporting resources.

Your final Submission must be made prior to the deadline. Any un-submitted or draft Writeups by the competition deadline will not be considered by the Judges.

Note: If you attach a private Kaggle Resource to your public Kaggle Writeup, your private Resource will automatically be made public after the deadline.

a. Public Notebook
The code must be well-documented and clearly show the implementation of BigQuery AI. This is non-negotiable and will be used to validate the authenticity of your project. The code must be viewable without a login. It can be a github repository link, a Kaggle notebook link, included in the writeup etc.

b. Video (optional)
We also highly recommend you also make a public video or blog to showcase your work. The goal of the blog or video is to tell us the story and how you used BigQuery AI to solve the problem in a powerful way. You can post your video or blog to Medium, YouTube, X (Twitter), TikTok, or any other public platform, it must be viewable without a login.

c. User Survey (optional)
Every submission should include a survey attached as a text file in the data section.
The survey will be scored as a bonus but we highly encourage everyone to submit one. Please note - bonus points will be awarded for completeness of the survey - no points will be awarded based on your provided answers on the survey.

The survey questions are as follows:

Please tell us how many months of experience with BigQuery AI each team member has.
Please tell us how many months of experience with Google Cloud each team member has.
We’d love to hear from you and your experience in working with the technology during this hackathon, positive or negative. Please provide any feedback on your experience with BigQuery AI.
Evaluation
Valid submissions will first be evaluated on the above requirements for completeness, and then submissions will be evaluated based on the following criteria:

Technical Implementation (35%):

How well is the solution technically executed? Is the code clean, efficient? (20%)
0% - The code didn’t work
10% - The code ran but took an inordinate amount of time or was difficult to follow
20% - The code ran easily and was clean to read
How effectively does the project utilize the core concepts of BigQuery AI? (15%)
0% - BigQuery AI usage was irrelevant to the solution
5% - BigQuery AI were used but not a core function of the solution
15% - BigQuery AI was used well throughout the solution
Innovation and Creativity (25%):

How novel and original is the solution approach? (10%)
0% - You can easily find the approach online right now
10% - This was an innovative approach to the solution
Does it address a significant problem or create a unique solution? What is the impact on revenue, engagement, or other metrics? (e.g. hours saved, new users added, etc.) (15%)
0% - There is no consideration on any metric
5% - The solution moves a metric slightly
15% - The solution makes a large improvement in its space
Demo and Presentation (20%):

Is the problem clearly defined, and is the solution effectively presented through a demo and documentation? (10%)
0% - The problem and solution relationship was difficult to follow
5% - The problem and solution relationship was clear but the documentation was non existent
10% - There is a clear relationship between the problem and solution and the documentation was clear
Have they explained how they used BigQuery AI and ML and relevant tools? Have they included an architectural diagram? (10%)
0% - There was no explanation
5% - There was an explanation or an architectural diagram but not both
10% - There was a clear explanation and an architectural diagram
Assets (20%)

Is there a well thought out and easily consumable public blog or video demonstrating the solution? (10%)
0% - There was no blog or video
5% - There was a blog or video but it wasn’t clear what the solution it intended to demonstrate
10% - There was a blog or video clearly demonstrating the solution
Is the code publicly available and pushed into a Github repository? (10%)
0% - The code is not publicly available
10% - The code was made publicly available in Github
BONUS (optional, 10%)

Did the submission include any feedback on the BigQuery AI features? (5%)
0% - No feedback or friction points provided.
5% - Feedback or friction points provided.
Did the submission include the survey on the BigQuery AI features? (5%)
0% - No the survey was not completed.
5% - Yes the survey was attached and completed.
Timeline
August 12, 2025 - Start Date.
September 22, 2025 - Final Submission Deadline.
September 22, 2025 - October 6, 2025 - Judging Period*
October 13, 2025 - Anticipated Results Announcement.
*Note - Judging period subject to change based on the number of submissions received

All deadlines are at 11:59 PM UTC on the corresponding day unless otherwise noted. The competition organizers reserve the right to update the contest timeline if they deem it necessary.
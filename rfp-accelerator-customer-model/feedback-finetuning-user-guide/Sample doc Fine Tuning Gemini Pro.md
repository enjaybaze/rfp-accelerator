## Fine-Tuning a Gemini Pro Model for RFP Accelerator: A User Guide

This guide provides a practical, step-by-step approach to fine-tuning a Gemini Pro model for answering questions related to Request for Proposals (RFPs). We'll use Python and Google Cloud AI Platform for this purpose.

**1\. Data Preparation & Cleaning**

First, we need a dataset of RFP questions, contexts and its ground truth dataset.

```py
import pandas as pd

def load_data(file_path):
"""Loads data from an csv file."""
data = pd.read_csv(file_path)
return data

# Load the dataset
data = load_data("rfp_data.csv")
```

The dataset should be in the following format.

| Column | Dtype |
| :---- | :---- |
| exp\_id | object |
| question | object |
| search\_refinement | object |
| generated\_ans | object |
| ground\_truth | object |
| previous\_qes | object |
| context | object |

**2\. Context Enhancement with Paraphrasing**

- To improve the model's understanding, we can enrich the context by paraphrasing the ground truth information using a pre-trained language model.  
- This also ensures that the ground truth information is contained in the context, in different variations.

```py
from transformers import pipeline

def paraphrase_text(text):
"""Paraphrases the given text using a pre-trained model."""
paraphrases = paraphraser(text, num_return_sequences=1)
return paraphrases[0]['paraphrased_text']

# Example:
text = "<sample ground truth>"
paraphrased_text = paraphrase_text(text)
print(f"Original: {text}\nParaphrased: {paraphrased_text}")
```

We can integrate this paraphrasing function into our data processing pipeline to enrich the context of each training example.

**3\. Creating a JSONL Dataset**

For fine-tuning, we need to format our data into a JSON Lines (JSONL) file. Each line in the file will represent a single training example:

```
{"input": "<Question> <context + <Paraphrased Ground Truth> >", "output": "<ground truth>"}
```

We can iterate through our dataframe and create a JSONL file with the desired structure and split it into a test/validation jsonl file.

**4\. Fine-tuning the Gemini Pro Model**

We'll use Google Cloud's vertexai Python library for fine-tuning. Here we are following supervised finetuning approach(SFT)

```py
import vertexai

def finetune_model(project_id, location, training_data_uri,
validation_data_uri, model_display_name):
"""
Fine-tunes a Gemini Pro model using the provided data.
# Define training parameters
# ...
# Start fine-tuning job
# ...
# Wait for job completion and return tuned model information
"""

tuned_model_name, tuned_model_endpoint = finetune_model(
project_id="your-project-id",
location="us-central1",
training_data_uri="gs://your-bucket/training_data.jsonl",
validation_data_uri="gs://your-bucket/validation_data.jsonl",
model_display_name="rfp-classifier-v1",
)
```

**5\. Utilizing the Fine-tuned Model**

Once the fine-tuning job completes, we can use the tuned model to generate new RFP answers.

```py
def generate(prompt,job_endpoint):
    model = GenerativeModel(
    job_endpoint,
  )
    responses = model.generate_content(
      prompt,
      generation_config={
    "max_output_tokens": 2048,
    "temperature": 1,
    "top_p": 1,
},
      safety_settings={
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
},
      stream=True,
  )
    # print(responses)
    s=''
    for response in responses:
        s=s+response.text
    return s


query=f"""
System: You are an intelligent AI assistant helping the customer with their RFP questions on different services.

Strictly Use ONLY the following pieces of context to answer the question at the end. Think step-by-step manner and then answer.
Do not try to make up an answer:
 - if exact same question answer pair is present within the context output the same answer without altering words.
 - If the answer to the question cannot be determined from the context alone, say "I cannot determine the answer to that."
 - If the context is empty, just say "I do not know the answer to that."
 - Read the context clearly, Think and answer in best possible way.
 - Sometimes, you will be given with previous questions. The previous question helps us to understand the context well.
 - Do not consider previous question if it is not relevant.
 - Sometimes you will be given with search refinement, that guides you better and closer topic what user is expecting.
 - If same question answer pair is available within context, then write the exact same answer as output.
 - Never mention source names in the output.
 - Answer to the question in third person perspective, not the first person.
 - Never mention in the answer to verify the answer in the internet.

Search refinement keywords: [{search_refinement}]
Previous question: {prev_questions}
Present questions: {question}
===============================================================================
{context}
===============================================================================
Date today: {date}
Search refinement keywords: [{search_refinement}]
Previous question: {prev_questions}
Present questions: {question}
Descriptive Answer in {language} with markdown formatting and proper explaination (never include questions, never use big markdown headers like #, ##, #### within answer).
AI Answer: 
"""
print(generate(query,job_endpoint))

```

This guide provides a high-level overview of the fine-tuning process. Remember to adapt the code snippets and parameters to your specific dataset and desired model performance.

By following these steps, you can leverage the power of Gemini Pro and fine-tuning to build a custom RFP analysis system tailored to your specific needs.  

# Web Cat API

## Introduction

Web Cat is a Python-based API designed to facilitate the integration of website content with ChatGPT via a custom GPT. The parses a website's content and then seamlessly integrates these insights into your chat, enhancing the user experience with dynamic, context-aware interactions.

I find it very useful when I am ideating on a concept and I want to pull in additional info without just a copy and paste of the contents into the chat. 

## Getting Started

### Prerequisites

- Python 3.8 or later
- Flask

### Running the API

1. To start the Flask server locally:
   
    a. `cd app`

    b. `python3 app.py`

## Examples

Here's a quick example of how to use the API:

Calling ping to check that the service is up:

`curl -X POST -H "Content-Type: application/json" -d '{"url": "https://www.iana.org/help/example-domains", "output_format": "TEXT"}' http://localhost:4000/scrape`

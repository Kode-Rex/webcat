# Web Cat API

## Introduction

Web Cat is a Python-based API designed to facilitate the integration of website content with chat applications through a custom GPT model. This innovative API parses website content, processes it through a GPT model for contextual understanding and response generation, and then seamlessly integrates these insights into your chat application, enhancing the user experience with dynamic, context-aware interactions.

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

`curl -X GET -H "Content-Type: application/json" http://localhost:4000/ping`

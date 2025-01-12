# Family Stories

A Python application that helps families collect and preserve their stories by sending weekly questions and storing responses.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

**Family Stories** is an automated system designed to facilitate the collection and preservation of family narratives. It operates by sending weekly questions to family members via email, collecting their responses, and storing them securely in a MongoDB database. The system also sends confirmation emails upon receipt of responses and includes features like rate limiting and health monitoring to ensure smooth operation.

## Features

- **Automated Emailing:** Sends weekly questions to designated family members.
- **Response Collection:** Gathers and stores responses in a MongoDB database.
- **Confirmation Emails:** Sends acknowledgments when responses are received.
- **Rate Limiting:** Ensures compliance with email provider limits.
- **Health Monitoring:** Continuously monitors the system's health and status.
- **Containerized Service:** Easily deployable using Docker.

## Prerequisites

- **Python 3.9** or higher
- **MongoDB:** For storing responses and application state.
- **SMTP-enabled Email Account:** Gmail is recommended for sending emails.
- **Docker** (optional): For containerized deployment.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/family-stories.git
cd family-stories
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with the following variables:

```plaintext
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
```

### 3. Install Dependencies

Using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Prepare CSV Files

Ensure the following CSV files are present in the root directory:

- `emails.csv`: Contains family members' names and email addresses.
- `questions.csv`: Lists the weekly questions and the person who posed each question.
- `quotes.csv`: Includes quotes and their authors to be featured in the emails.

### 5. Configure Application

Rename `config/config.yml.template` to `config/config.yml` and update the placeholders with your actual credentials and settings.

```bash
cp config/config.yml.template config/config.yml
```

Edit `config/config.yml` to reflect your configurations:

```yaml
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  imap_server: "imap.gmail.com"
  username: "${EMAIL_USERNAME}"
  password: "${EMAIL_PASSWORD}"
  rate_limit:
    delay_between_emails: 5  # seconds
    max_emails_per_hour: 100 # prevent hitting email provider limits

database:
  mongodb_uri: "mongodb://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@vds.dannydemosi.com:9091"
  database_name: "app"

healthcheck:
  test: ["CMD", "python", "-c", "from app import FamilyStoriesApp; app = FamilyStoriesApp(); print(app.health_check())"]
  interval: 1m
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Usage

### Running the Application

#### Using Docker

Ensure you have Docker installed. Then, build and run the container:

```bash
docker-compose up --build
```

#### Without Docker

Run the main application script:

```bash
python app/main.py
```

### Scheduling

The application is configured to:

- **Send Weekly Questions:** Every Sunday at 6:00 AM.
- **Check Email Responses:** Every hour.

These schedules are managed using the `schedule` library and can be adjusted in the `app/main.py` file.

## Testing

To run tests, navigate to the `tests/` directory and execute the test scripts:

```bash
python tests/test_send_question.py
```

Ensure that your testing environment is correctly set up with appropriate CSV files and configurations.

## Deployment

The application can be easily deployed using Docker for consistency across environments. Refer to the [Installation](#installation) section for Docker setup instructions.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Push to your fork and create a pull request.

Please ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any questions or feedback, please contact [your_email@example.com](mailto:your_email@example.com).




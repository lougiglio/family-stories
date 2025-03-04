# Family Stories Application

A Python application that sends weekly questions to family members and collects their responses via email.

## Deployment & Management

### Initial Setup

#### Option A: New Installation
1. Create and navigate to your project directory:
   ```bash
   mkdir -p /opt/family-stories  # Linux/Mac
   cd /opt/family-stories
   # OR for Windows:
   mkdir family-stories
   cd family-stories
   ```

2. Initialize git and add remote repository:
   ```bash
   git init
   git remote add origin https://github.com/yourusername/family-stories.git
   git fetch
   git checkout main
   ```

#### Option B: Existing Directory
If you already have a family-stories directory:
```bash
cd family-stories  # if not already in the directory
git init
git remote add origin https://github.com/yourusername/family-stories.git
git fetch
git checkout -f main  # -f flag to overwrite existing files
```

### Configuration
1. Create and configure `.env` file:
   ```bash
   cp .env.template .env
   # Edit .env with your MongoDB and Email credentials
   ```

2. Install Docker and Docker Compose:
   - For Linux:
     ```bash
     sudo apt-get update
     sudo apt-get install -y docker.io docker-compose
     ```
   - For Windows:
     Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

### Running the Application

#### Linux/Mac
1. Start the application (from the project root directory):
   ```bash
   # Make sure you're in the project root directory, not the build directory
   cd build
   docker-compose up --build
   ```

#### Windows
1. Start the application (from the project root directory):
   ```powershell
   cd build
   docker compose --env-file ../.env up --build
   ```

2. Check application status:
   ```bash
   docker compose ps
   docker compose logs -f
   ```

3. Stop the application:
   ```bash
   docker compose down
   ```

### Updating the Application
1. Pull latest changes from GitHub:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart the container (from project root):
   ```bash
   cd build
   docker compose --env-file ../.env up --build
   ```

### Troubleshooting
- View application logs:
  ```bash
  cd build
  docker compose logs -f
  ```

- Check MongoDB connection:
  ```bash
  docker compose exec family-stories ping mongodb
  ```

- Restart the application:
  ```bash
  cd build
  docker compose restart
  ```

#### Windows-Specific Issues
- If environment variables are not being properly loaded, you can use the provided PowerShell script:
  ```powershell
  cd build
  ./run.ps1
  ```

## Configuration Files
- `.env` - Environment variables for MongoDB and Email settings
- `build/config.yml` - Application configuration
- `assets/` - Contains CSV files for emails, questions, and quotes

## Data Files
- `assets/emails.csv` - Family member contact information
- `assets/questions.csv` - Weekly questions
- `assets/quotes.csv` - Inspirational quotes 

## Email Configuration Features

### Weekly Questions Control
To control which family members receive weekly questions, add a `ReceiveQuestions` column to your `assets/emails.csv` file:

```csv
Name,Email,ReceiveQuestions
John Doe,john.doe@example.com,1
Jane Smith,jane.smith@example.com,1
Bob Johnson,bob.johnson@example.com,0
```

Set the value to 1 for family members who should receive weekly questions, and 0 for those who should not.

### Email Forwarding Feature
The application can automatically forward family member responses to other family members. This allows everyone to see each other's stories and memories.

To control which family members receive forwarded responses, add a `ReceiveForwards` column to your `assets/emails.csv` file:

```csv
Name,Email,ReceiveForwards,ReceiveQuestions
John Doe,john.doe@example.com,1,1
Jane Smith,jane.smith@example.com,1,1
Bob Johnson,bob.johnson@example.com,0,1
Alice Johnson,alice.johnson@example.com,1,0
```

Set the value to 1 for family members who should receive forwarded responses, and 0 for those who should not.

If these columns are not present, all family members will receive both weekly questions and forwarded responses by default. 
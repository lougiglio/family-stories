# Family Stories Application

A Python application that sends weekly questions to family members and collects their responses via email.

## VM Deployment & Management

### Initial Setup

#### Option A: New Installation
1. Create and navigate to your project directory:
   ```bash
   mkdir -p /opt/family-stories
   cd /opt/family-stories
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
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   ```

### Running the Application
1. Start the application (from the project root directory):
   ```bash
   # Make sure you're in the project root directory, not the build directory
   docker-compose -f build/docker-compose.yml up -d
   ```

2. Check application status:
   ```bash
   docker-compose -f build/docker-compose.yml ps
   docker-compose -f build/docker-compose.yml logs -f
   ```

3. Stop the application:
   ```bash
   docker-compose -f build/docker-compose.yml down
   ```

### Updating the Application
1. Pull latest changes from GitHub:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart the container (from project root):
   ```bash
   docker-compose -f build/docker-compose.yml down
   docker-compose -f build/docker-compose.yml up -d --build
   ```

### Troubleshooting
- View application logs:
  ```bash
  cd build
  docker-compose logs -f
  ```

- Check MongoDB connection:
  ```bash
  docker-compose exec family-stories ping mongodb-host
  ```

- Restart the application:
  ```bash
  cd build
  docker-compose restart
  ```

## Configuration Files
- `.env` - Environment variables for MongoDB and Email settings
- `build/config.yml` - Application configuration
- `assets/` - Contains CSV files for emails, questions, and quotes

## Data Files
- `assets/emails.csv` - Family member contact information
- `assets/questions.csv` - Weekly questions
- `assets/quotes.csv` - Inspirational quotes 
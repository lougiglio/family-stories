# Family Stories Application

A Python application that sends weekly questions to family members and collects their responses via email.

## VM Deployment & Management

### Initial Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/family-stories.git
   cd family-stories
   ```

2. Create and configure `.env` file:
   ```bash
   cp .env.template .env
   # Edit .env with your MongoDB and Email credentials
   ```

3. Install Docker and Docker Compose:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   ```

### Running the Application
1. Start the application:
   ```bash
   cd build
   docker-compose up -d
   ```

2. Check application status:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

3. Stop the application:
   ```bash
   docker-compose down
   ```

### Updating the Application
1. Pull latest changes from GitHub:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart the container:
   ```bash
   cd build
   docker-compose down
   docker-compose up -d --build
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
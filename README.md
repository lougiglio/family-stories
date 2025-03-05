# Family Stories Application

A Python application that sends weekly questions to family members and collects their responses via email. The application also forwards responses to other family members, allowing everyone to share in the stories and memories.

## Features

- **Weekly Questions**: Automatically sends weekly questions to selected family members
- **Response Collection**: Collects and stores email responses in a MongoDB database
- **Email Forwarding**: Forwards responses to other family members (configurable)
- **Selective Distribution**: Control which family members receive questions and/or forwarded responses

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
1. Create and configure `.env` file in the build directory:
   ```bash
   cd build
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
   docker compose --env-file .env up --build
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

### Proxmox Deployment
To deploy in Proxmox:

1. Create a Linux Container (LXC) or Virtual Machine (VM) in Proxmox
2. Install Docker and Docker Compose:
   ```bash
   apt update
   apt install -y apt-transport-https ca-certificates curl software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
   add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   apt update
   apt install -y docker-ce docker-ce-cli containerd.io docker-compose git
   ```

3. Clone the repository and configure:
   ```bash
   mkdir -p /opt/family-stories
   cd /opt/family-stories
   git init
   git remote add origin https://github.com/yourusername/family-stories.git
   git fetch
   git checkout main
   cd build
   cp .env.template .env
   nano .env  # Edit with your credentials
   ```

4. Start the application:
   ```bash
   # Already in the build directory
   docker-compose --env-file .env up -d --build
   ```

5. Set up auto-start on boot:
   ```bash
   cat > /etc/systemd/system/family-stories.service << 'EOL'
   [Unit]
   Description=Family Stories Application
   After=docker.service
   Requires=docker.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/opt/family-stories/build
   ExecStart=/usr/bin/docker-compose --env-file .env up -d
   ExecStop=/usr/bin/docker-compose down
   TimeoutStartSec=0

   [Install]
   WantedBy=multi-user.target
   EOL

   systemctl enable family-stories.service
   systemctl start family-stories.service
   ```

### Updating the Application
1. Pull latest changes from GitHub:
   ```bash
   cd /opt/family-stories
   git pull origin main
   ```

2. Rebuild and restart the container:
   ```bash
   cd build
   docker-compose --env-file .env up -d --build
   ```

### Troubleshooting
- View application logs:
  ```bash
  cd /opt/family-stories/build
  docker-compose logs -f
  ```

- Check MongoDB connection:
  ```bash
  docker-compose exec family-stories ping mongodb
  ```

- Restart the application:
  ```bash
  cd /opt/family-stories/build
  docker-compose restart
  ```

## Configuration Files
- `build/.env` - Environment variables for MongoDB and Email settings
- `build/config.yml` - Application configuration
- `assets/` - Contains CSV files for emails, questions, and quotes

## Data Files

### Family Members Configuration (assets/emails.csv)
The `emails.csv` file controls who receives weekly questions and forwarded responses:

```csv
Name,Email,ReceiveForwards,ReceiveQuestions
Matt,mggummow@gmail.com,1,1
Kelly,gummowkelly@gmail.com,0,1
Bryanna,bryanna.gummow@missionary.org,1,0
```

- **Name**: Family member's name
- **Email**: Family member's email address
- **ReceiveForwards**: Set to 1 to receive forwarded responses, 0 to opt out
- **ReceiveQuestions**: Set to 1 to receive weekly questions, 0 to opt out

### Other Data Files
- `assets/questions.csv` - Weekly questions to send to family members
- `assets/quotes.csv` - Inspirational quotes to include with weekly questions

## How It Works

1. **Weekly Questions**: Every Sunday at 6 AM, the application sends the current question to family members who have `ReceiveQuestions=1`
2. **Response Collection**: When family members reply to the question email, the application:
   - Stores the response in the MongoDB database
   - Sends a confirmation email to the responder
   - Forwards the response to all family members who have `ReceiveForwards=1` (except the original responder)
3. **Email Checking**: The application checks for new responses every 15 minutes between 6 AM and 10 PM 
================================================================================
                    BACKEND SETUP GUIDE - TEAM COLLABORATION HUB
================================================================================

PROJECT OVERVIEW
================================================================================
This is the backend server for Team Collaboration Hub built with Node.js and Express.
The application uses MongoDB for database management and includes comprehensive 
middleware for handling requests, authentication, and error management.

TECHNOLOGY STACK
================================================================================
- Runtime: Node.js (v18 or higher)
- Framework: Express.js (v5.2.1)
- Database: MongoDB (v5.0 or higher)
- ODM: Mongoose (v9.4.1)
- Environment Management: dotenv (v17.4.1)
- CORS: cors (v2.8.6)
- Development: nodemon (v3.1.14)

PREREQUISITES
================================================================================
Before setting up the backend, ensure you have installed:

1. Node.js and npm
   - Download from: https://nodejs.org/
   - Verify installation: node --version && npm --version
   
2. MongoDB
   - Option A: Local Installation (https://www.mongodb.com/try/download/community)
   - Option B: MongoDB Atlas (Cloud) - Create free account at https://www.mongodb.com/cloud/atlas
   
3. Git (for version control)
   - Download from: https://git-scm.com/

INSTALLATION STEPS
================================================================================

STEP 1: Navigate to Backend Directory
   Open PowerShell/Command Prompt and run:
   
   cd Backend

STEP 2: Install Dependencies
   Run the following command to install all required packages from package.json:
   
   npm install
   
   This will install:
   - express: Web framework for Node.js
   - mongoose: MongoDB object modeling
   - cors: Cross-Origin Resource Sharing middleware
   - dotenv: Environment variable management
   - nodemon: Auto-restart development server (dev only)

STEP 3: Environment Configuration
   Create a .env file in the Backend directory with the following variables:
   
   Sample .env file:
   ================
   # Server Configuration
   PORT=3000
   NODE_ENV=development
   
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017/team-collaboration-hub
   
   # Alternative for MongoDB Atlas:
   # MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database-name?retryWrites=true&w=majority
   
   # API Settings
   API_VERSION=v1
   
   Save this file as: .env (in the Backend directory)

STEP 4: MongoDB Setup

   Option A: Local MongoDB Installation
   
   1. Start MongoDB service:
      - Windows: Press Windows key, search "MongoDB", start the service
      - Or run: mongod (in terminal)
   
   2. Verify MongoDB is running:
      - Open another terminal and run: mongo
      - If successful, you'll see the MongoDB shell
   
   Option B: MongoDB Atlas (Cloud)
   
   1. Go to: https://www.mongodb.com/cloud/atlas
   2. Create a free account and log in
   3. Create a new project and cluster
   4. Get your connection string (looks like): 
      mongodb+srv://username:password@cluster.mongodb.net/database-name
   5. Add this URI to your .env file under MONGODB_URI

RUNNING THE SERVER
================================================================================

Development Mode (with auto-reload):
   npm run dev
   
   Output should show:
   Server is running on port 3000
   
Production Mode:
   npm start

Testing the Server:
   Open your browser and visit: http://localhost:3000
   Or use Postman/Thunder Client to test API endpoints

DIRECTORY STRUCTURE
================================================================================
Backend/
├── src/
│   ├── server.js              # Main server entry point
│   ├── config/                # Configuration files
│   │   ├── database.js        # MongoDB connection
│   │   └── constants.js       # Application constants
│   ├── models/                # Mongoose schemas and models
│   │   └── User.js            # User model example
│   ├── controllers/           # Request handlers
│   │   └── userController.js  # User operations
│   ├── routes/                # API route definitions
│   │   └── userRoutes.js      # User routes
│   ├── middleware/            # Custom middleware
│   │   ├── auth.js            # Authentication middleware
│   │   └── errorHandler.js    # Error handling
│   └── utils/                 # Helper functions
│       ├── validators.js      # Input validation
│       └── logger.js          # Logging utility
├── package.json               # Project dependencies
├── .env                       # Environment variables (create this)
├── .gitignore                 # Git ignore rules
└── README.TXT                 # This file

PACKAGE.JSON DETAILS
================================================================================
The package.json file contains:

Scripts:
- npm start        : Run server in production mode
- npm run dev      : Run server with nodemon (development)
- npm test         : Run test suite (to be configured)

Dependencies:
- express: Web framework for building REST APIs
- mongoose: ODM for MongoDB
- cors: Handle cross-origin requests
- dotenv: Load environment variables from .env file

Dev Dependencies:
- nodemon: Watch for file changes and auto-restart server

SETTING UP PROJECT STRUCTURE
================================================================================
Create the following folders in the src/ directory:

mkdir src\config
mkdir src\models
mkdir src\controllers
mkdir src\routes
mkdir src\middleware
mkdir src\utils

Then create files as shown in the directory structure above.

COMMON SETUP ISSUES & SOLUTIONS
================================================================================

Issue 1: "module not found" error after npm install
Solution: 
- Clear npm cache: npm cache clean --force
- Delete node_modules: rmdir node_modules /s /q
- Reinstall: npm install

Issue 2: MongoDB connection fails
Solution:
- Verify MongoDB is running (check MongoDB service in Services)
- Check MONGODB_URI in .env file
- For MongoDB Atlas, ensure IP is whitelisted in Network Access

Issue 3: Port 3000 already in use
Solution:
- Change PORT in .env file to another number (e.g., 3001, 3002)
- Or kill the process using port 3000

Issue 4: nodemon not recognized
Solution:
- Install nodemon globally: npm install -g nodemon
- Or use: npx nodemon src/server.js

ADDITIONAL SETUP RECOMMENDATIONS
================================================================================

1. Create .gitignore file in Backend directory:
   
   node_modules/
   .env
   .DS_Store
   *.log

2. Database Connection Best Practices:
   - Use connection pooling
   - Set timeout values
   - Handle connection errors gracefully

3. Security Setup:
   - Use strong passwords for MongoDB
   - Enable authentication in MongoDB
   - Use HTTPS in production
   - Implement rate limiting
   - Validate all inputs

4. Logging:
   - Implement structured logging
   - Log all API requests and errors
   - Monitor server performance

5. API Documentation:
   - Use Swagger/OpenAPI for documentation
   - Document all endpoints
   - Include request/response examples

NEXT STEPS
================================================================================

1. Complete initial setup following steps above
2. Test server connection: npm run dev
3. Create database models in src/models/
4. Create API routes in src/routes/
5. Create controllers in src/controllers/
6. Implement authentication middleware
7. Set up error handling
8. Add input validation
9. Write API documentation
10. Set up deployment configuration

DEVELOPMENT WORKFLOW
================================================================================

1. Start development server:
   npm run dev

2. Create/modify files in src/ directory

3. Test endpoints using:
   - Postman (https://www.postman.com/)
   - Thunder Client (VS Code extension)
   - Insomnia (https://insomnia.rest/)

4. Monitor logs for errors and issues

5. Commit changes to git regularly:
   git add .
   git commit -m "Description of changes"
   git push

USEFUL COMMANDS
================================================================================

npm install              # Install dependencies
npm install <package>   # Install new package
npm install -D <pkg>    # Install dev dependency
npm list               # List installed packages
npm outdated           # Check for outdated packages
npm update             # Update packages
npm run dev            # Start dev server with nodemon
npm start              # Start production server
npm test               # Run tests
npm cache clean        # Clear npm cache

DEPLOYMENT NOTES
================================================================================

For production deployment:

1. Set NODE_ENV=production in .env
2. Use a production-grade database (MongoDB Atlas recommended)
3. Configure proper error handling
4. Set up environment-specific variables
5. Use a process manager (PM2, Forever, etc.)
6. Enable HTTPS
7. Implement comprehensive logging
8. Set up monitoring and alerting
9. Configure backup strategies
10. Use a reverse proxy (Nginx, etc.)

RESOURCES & DOCUMENTATION
================================================================================

- Node.js: https://nodejs.org/docs/
- Express.js: https://expressjs.com/
- MongoDB: https://docs.mongodb.com/
- Mongoose: https://mongoosejs.com/
- npm: https://docs.npmjs.com/
- dotenv: https://github.com/motdotla/dotenv

SUPPORT & TROUBLESHOOTING
================================================================================

If you encounter issues:

1. Check the error message carefully
2. Search error message in official documentation
3. Check GitHub issues for similar problems
4. Review server logs for detailed error information
5. Check internet connection and firewall settings
6. Verify all prerequisite software is installed correctly

================================================================================
                              END OF SETUP GUIDE
================================================================================

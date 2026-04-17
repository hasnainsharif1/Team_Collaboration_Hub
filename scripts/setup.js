import dotenv from 'dotenv';
import connectDB from '../src/config/database.js';
import Admin from '../src/models/admin.model.js';

dotenv.config();

const setupAdmin = async () => {
  try {
    await connectDB();
    console.log('🔧 Setting up admin user...');

    const email = process.argv[2] || process.env.ADMIN_EMAIL || 'admin@teamhub.com';
    const password = process.argv[3] || process.env.ADMIN_PASSWORD;
    const name = process.argv[4] || process.env.ADMIN_NAME || 'Team Hub Admin';

    if (!password) {
      console.error('❌ Password is required. Provide as argument or set ADMIN_PASSWORD in .env');
      process.exit(1);
    }

    console.log(`🔍 Checking if admin exists: ${email}`);

    const existingAdmin = await Admin.findOne({ email });
    if (existingAdmin) {
      console.log(`✅ Admin already exists: ${email}`);
      return;
    }

    console.log(`📝 Creating admin: ${email}`);
    const admin = new Admin({ name, email, password });
    await admin.save();
    console.log(`✅ Admin created successfully: ${email}`);

    process.exit(0);
  } catch (error) {
    console.error('❌ Setup error:', error.message);
    process.exit(1);
  }
};

setupAdmin();
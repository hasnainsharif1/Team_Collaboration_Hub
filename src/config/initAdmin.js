import Admin from '../models/admin.model.js';

const initAdmin = async () => {
  try {
    console.log('🔧 Starting admin initialization...');

    const email = process.env.ADMIN_EMAIL || 'admin@teamhub.com';
    const password = process.env.ADMIN_PASSWORD || 'Admin@123';
    const name = process.env.ADMIN_NAME || 'Team Hub Admin';

    console.log(`🔍 Checking if admin exists: ${email}`);

    const existingAdmin = await Admin.findOne({ email });
    if (existingAdmin) {
      console.log(`✅ Default admin already exists: ${email}`);
      return;
    }

    console.log(`📝 Creating new admin: ${email}`);
    const admin = new Admin({ name, email, password });
    await admin.save();
    console.log(`✅ Default admin created successfully: ${email}`);
  } catch (error) {
    console.error('❌ Admin initialization error:', error.message || error);
    console.error('Full error:', error);
  }
};

export default initAdmin;


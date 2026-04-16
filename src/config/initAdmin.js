import Admin from '../models/admin.model.js';

const initAdmin = async () => {
  try {
    const email = process.env.ADMIN_EMAIL || 'admin@teamhub.com';
    const password = process.env.ADMIN_PASSWORD || 'Admin@123';
    const name = process.env.ADMIN_NAME || 'Team Hub Admin';

    const existingAdmin = await Admin.findOne({ email });
    if (existingAdmin) {
      console.log(`Default admin already exists: ${email}`);
      return;
    }

    const admin = new Admin({ name, email, password });
    await admin.save();
    console.log(`Default admin created: ${email}`);
  } catch (error) {
    console.error('Admin initialization error:', error.message || error);
  }
};

export default initAdmin;

import mongoose from 'mongoose';

const connectDB = async () => {
  try {
    const mongoURL = process.env.MONGODB_URI;
    console.log(`Connecting to MongoDB at ${mongoURL}`);

    await mongoose.connect(mongoURL);

    console.log('MongoDB connected!!');
  } catch (error) {
    console.error('DB Connection Error:', error.message || error);
    process.exit(1);
  }
};

export default connectDB;
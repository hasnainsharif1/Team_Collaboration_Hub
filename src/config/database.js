import mongose from 'mongoose';

const connectDB = async () => {
    try {
       const mongoURL = process.env.MONGODB_URI;
       
       console.log(` Connecting to mongose at ${MONGODB_URI}`);
       
       const connectionInstance =  await mongose.connect(mongoURL);

       console.log(`MongoDB connected!!`);
       
       
    } catch (error) {
        console.log(`DB Connection Error ${error}`);
        
    }
}

export default connectDB;
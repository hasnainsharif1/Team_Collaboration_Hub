import express from "express";
import { registerUser, loginUser, logoutUser } from "../controllers/user.controller.js";
import validateRequest from "../middleware/validateRequest.js";

const router = express.Router();

router.post(
  "/register",
  validateRequest({
    body: {
      firstName: { required: true, type: "string", minLength: 2 },
      lastName: { required: true, type: "string", minLength: 2 },
      email: {
        required: true,
        type: "string",
        pattern: /^\S+@\S+\.\S+$/,
        patternMessage: "Please provide a valid email.",
      },
      password: { required: true, type: "string", minLength: 6 },
    },
  }),
  registerUser
);

router.post(
  "/login",
  validateRequest({
    body: {
      email: {
        required: true,
        type: "string",
        pattern: /^\S+@\S+\.\S+$/,
        patternMessage: "Please provide a valid email.",
      },
      password: { required: true, type: "string" },
    },
  }),
  loginUser
);

router.post("/logout", logoutUser);

export default router;
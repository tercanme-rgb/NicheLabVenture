import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithRedirect,
  getRedirectResult,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signOut,
  setPersistence,
  browserLocalPersistence,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCrAeW_WvzENswPLKcOn6_7Zrk0OjNvrmA",
  authDomain: "nichelab-5427c.firebaseapp.com",
  projectId: "nichelab-5427c",
  storageBucket: "nichelab-5427c.firebasestorage.app",
  messagingSenderId: "892086112182",
  appId: "1:892086112182:web:9bd8d175cd8e512c63fb17",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
auth.onAuthStateChanged = onAuthStateChanged.bind(null, auth);

const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: "select_account" });

let authReadyPromise = null;

function getErrorTarget() {
  return document.getElementById("auth-error");
}

function clearAuthError() {
  const box = getErrorTarget();
  if (!box) return;
  box.textContent = "";
  box.style.display = "none";
}

function showAuthError(error) {
  const code = error?.code || "unknown";
  const details = error?.message ? ` (${error.message})` : "";

  const map = {
    "auth/invalid-credential": "Sign-in failed. Check your email and password.",
    "auth/user-not-found": "No account was found for that email.",
    "auth/wrong-password": "The password is incorrect.",
    "auth/invalid-email": "Enter a valid email address.",
    "auth/email-already-in-use": "An account already exists with that email.",
    "auth/weak-password": "Choose a stronger password.",
    "auth/account-exists-with-different-credential": "This email is already linked to a different sign-in method.",
    "auth/unauthorized-domain": "This domain is not authorized in Firebase Authentication.",
    "auth/operation-not-allowed": "This sign-in method is not enabled in Firebase Authentication.",
    "auth/popup-blocked": "Your browser blocked the sign-in window.",
    "auth/popup-closed-by-user": "The sign-in window was closed before completion.",
    "auth/cancelled-popup-request": "Another sign-in attempt interrupted the previous one.",
    "auth/network-request-failed": "Network error during sign-in. Check your connection and try again.",
  };

  const message = map[code] || `Authentication failed: ${code}${details}`;
  const box = getErrorTarget();

  if (box) {
    box.textContent = message;
    box.style.display = "block";
  } else {
    alert(message);
  }

  console.error("Firebase auth error:", error);
}

async function ensureAuthReady() {
  if (authReadyPromise) return authReadyPromise;

  authReadyPromise = (async () => {
    try {
      await setPersistence(auth, browserLocalPersistence);
    } catch (error) {
      console.warn("Could not set auth persistence:", error);
    }

    try {
      await getRedirectResult(auth);
      clearAuthError();
    } catch (error) {
      showAuthError(error);
    }
  })();

  return authReadyPromise;
}

export async function signInWithGoogle() {
  clearAuthError();
  await ensureAuthReady();

  try {
    await signInWithRedirect(auth, googleProvider);
  } catch (error) {
    showAuthError(error);
  }
}

export async function signInWithEmail(email, password) {
  clearAuthError();
  await ensureAuthReady();

  try {
    await signInWithEmailAndPassword(auth, email, password);
  } catch (error) {
    showAuthError(error);
  }
}

export async function createAccount(email, password) {
  clearAuthError();
  await ensureAuthReady();

  try {
    await createUserWithEmailAndPassword(auth, email, password);
  } catch (error) {
    showAuthError(error);
  }
}

export async function signOutUser() {
  clearAuthError();

  try {
    await signOut(auth);
  } catch (error) {
    showAuthError(error);
  }
}

ensureAuthReady();

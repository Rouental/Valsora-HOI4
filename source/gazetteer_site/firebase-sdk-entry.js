// The parts of the Firebase web SDK the Valsora Gazetteer uses, as one ES module.
export { initializeApp } from "firebase/app";
export { getFirestore, initializeFirestore, connectFirestoreEmulator, doc, collection, getDoc, getDocs, setDoc, deleteDoc,
         onSnapshot, query, where, limit } from "firebase/firestore";
export { getAuth, connectAuthEmulator, GoogleAuthProvider, signInWithPopup, signInWithCredential,
         onAuthStateChanged, signOut } from "firebase/auth";

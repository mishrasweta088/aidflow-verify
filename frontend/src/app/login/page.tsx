"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();

  async function handleLogin() {
    setMessage("Logging in...");

    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();

        localStorage.setItem("access_token", data.access_token);

        setMessage("Login successful. Token saved.");
        setEmail("");
        setPassword("");

        router.push("/dashboard");
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Login failed.");
      }
    } catch {
      setMessage("Backend may be waking up. Please wait 30 seconds and try again.");
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
      <div className="mx-auto max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8">
        <nav className="mb-6 flex gap-4 text-sm text-slate-300">
          <Link href="/" className="hover:text-white">Home</Link>
          <Link href="/login" className="hover:text-white">Login</Link>
          <Link href="/register" className="hover:text-white">Register</Link>
        </nav>
        <h1 className="text-3xl font-bold">Login</h1>
        <p className="mt-2 text-slate-400">
          Sign in to manage aid requests, verification tasks, or donor claims.
        </p>

        <form className="mt-8 space-y-4">
          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />

          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <button
            type="button"
            onClick={handleLogin}
            className="w-full rounded-lg bg-white px-4 py-3 font-semibold text-slate-950 hover:bg-slate-200"
          >
            Login
          </button>
        </form>

        {message && <p className="mt-4 text-sm text-slate-300">{message}</p>}
      </div>
    </main>
  );
}
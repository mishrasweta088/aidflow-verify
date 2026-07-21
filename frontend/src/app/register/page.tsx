"use client";

import Link from "next/link";
import { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("requester");
  const [message, setMessage] = useState("");

  async function handleRegister() {
    setMessage("Registering...");

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          role,
          full_name: fullName,
          phone: "1234567890",
          address: "Binghamton, NY",
          latitude: 42.0987,
          longitude: -75.918,
        }),
      });

      if (response.ok) {
        setMessage("Account created successfully. You can now login.");
        setFullName("");
        setEmail("");
        setPassword("");
        setRole("requester");
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Registration failed.");
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
        <h1 className="text-3xl font-bold">Create Account</h1>
        <p className="mt-2 text-slate-400">
          Register as a requester, volunteer, donor, or admin.
        </p>

        <form className="mt-8 space-y-4">
          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
            placeholder="Full name"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
          />

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

          <select
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
            value={role}
            onChange={(event) => setRole(event.target.value)}
          >
            <option value="requester">Requester</option>
            <option value="volunteer">Volunteer</option>
            <option value="donor">Donor</option>
            <option value="admin">Admin</option>
          </select>

          <button
            type="button"
            onClick={handleRegister}
            className="w-full rounded-lg bg-white px-4 py-3 font-semibold text-slate-950 hover:bg-slate-200"
          >
            Register
          </button>
        </form>

        {message && <p className="mt-4 text-sm text-slate-300">{message}</p>}

        {message.includes("Account created successfully") && (
          <Link
            href="/login"
            className="mt-4 block rounded-lg bg-emerald-500 px-4 py-3 text-center font-semibold text-white hover:bg-emerald-600"
          >
            Go to Login
          </Link>
        )}

        {message.includes("Account created successfully") && (
          <Link
            href="/login"
            className="mt-4 block rounded-lg bg-emerald-500 px-4 py-3 text-center font-semibold text-white hover:bg-emerald-600"
          >
            Go to Login
          </Link>
        )}
      </div>
    </main>
  );
}

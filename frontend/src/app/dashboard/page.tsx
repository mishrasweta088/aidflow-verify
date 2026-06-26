"use client";

import { useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

type User = {
  id: string;
  email: string;
  role: string;
};

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [message, setMessage] = useState("Loading dashboard...");

  useEffect(() => {
    async function fetchCurrentUser() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setMessage("No login token found. Please login first.");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
        setMessage("");
      } else {
        setMessage("Session invalid. Please login again.");
      }
    }

    fetchCurrentUser();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
      <div className="mx-auto max-w-3xl rounded-2xl border border-slate-800 bg-slate-900 p-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>

        {message && <p className="mt-4 text-slate-300">{message}</p>}

        {user && (
          <div className="mt-6 space-y-3">
            <p className="text-slate-300">
              Logged in as: <span className="font-semibold text-white">{user.email}</span>
            </p>

            <p className="text-slate-300">
              Role: <span className="font-semibold text-white">{user.role}</span>
            </p>

            <div className="mt-8 rounded-xl border border-slate-700 bg-slate-950 p-6">
              <h2 className="text-xl font-semibold">AidFlow Verify Workflow</h2>
              <p className="mt-2 text-slate-400">
                Your role-based actions will appear here in the next steps.
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
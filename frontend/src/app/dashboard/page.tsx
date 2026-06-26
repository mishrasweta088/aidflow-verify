"use client";

import { useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

type User = {
  id: string;
  email: string;
  role: string;
};

type AidRequest = {
  id: string;
  title: string;
  description: string;
  category: string;
  address: string;
  status: string;
};

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [requests, setRequests] = useState<AidRequest[]>([]);
  const [message, setMessage] = useState("Loading dashboard...");

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("food");
  const [address, setAddress] = useState("");

  async function fetchMyRequests(token: string) {
    const response = await fetch(`${API_BASE_URL}/aid-requests/my`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      setRequests(data);
    }
  }

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
        await fetchMyRequests(token);
      } else {
        setMessage("Session invalid. Please login again.");
      }
    }

    fetchCurrentUser();
  }, []);

  async function handleCreateRequest() {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("Please login first.");
      return;
    }

    setMessage("Creating request...");

    const response = await fetch(`${API_BASE_URL}/aid-requests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title,
        description,
        category,
        address,
        latitude: 42.0987,
        longitude: -75.918,
      }),
    });

    if (response.ok) {
      setMessage("Aid request created successfully.");
      setTitle("");
      setDescription("");
      setCategory("food");
      setAddress("");

      await fetchMyRequests(token);
    } else {
      const errorData = await response.json();
      setMessage(errorData.detail || "Failed to create request.");
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
      <div className="mx-auto max-w-5xl space-y-8">
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>

          {message && <p className="mt-4 text-slate-300">{message}</p>}

          {user && (
            <div className="mt-6 space-y-2">
              <p className="text-slate-300">
                Logged in as:{" "}
                <span className="font-semibold text-white">{user.email}</span>
              </p>

              <p className="text-slate-300">
                Role:{" "}
                <span className="font-semibold text-white">{user.role}</span>
              </p>
            </div>
          )}
        </section>

        {user?.role === "requester" && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <h2 className="text-2xl font-bold">Create Aid Request</h2>

            <div className="mt-6 space-y-4">
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
                placeholder="Title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
              />

              <textarea
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
                placeholder="Description"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
              />

              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
              >
                <option value="food">Food</option>
                <option value="medicine">Medicine</option>
                <option value="shelter">Shelter</option>
                <option value="transport">Transport</option>
                <option value="other">Other</option>
              </select>

              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white"
                placeholder="Address"
                value={address}
                onChange={(event) => setAddress(event.target.value)}
              />

              <button
                type="button"
                onClick={handleCreateRequest}
                className="rounded-lg bg-white px-6 py-3 font-semibold text-slate-950 hover:bg-slate-200"
              >
                Submit Request
              </button>
            </div>
          </section>
        )}

        {user?.role === "requester" && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <h2 className="text-2xl font-bold">My Aid Requests</h2>

            <div className="mt-6 space-y-4">
              {requests.length === 0 && (
                <p className="text-slate-400">No aid requests yet.</p>
              )}

              {requests.map((request) => (
                <div
                  key={request.id}
                  className="rounded-xl border border-slate-700 bg-slate-950 p-5"
                >
                  <h3 className="text-xl font-semibold">{request.title}</h3>
                  <p className="mt-2 text-slate-400">{request.description}</p>
                  <p className="mt-2 text-sm text-slate-500">
                    Category: {request.category}
                  </p>
                  <p className="text-sm text-slate-500">
                    Address: {request.address}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-white">
                    Status: {request.status}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
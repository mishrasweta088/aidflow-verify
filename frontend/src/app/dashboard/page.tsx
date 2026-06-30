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

type NearbyVolunteer = {
  id: string;
  email: string;
  full_name: string;
  latitude: number;
  longitude: number;
  distance_meters: number;
};

type VerificationTask = {
  id: string;
  aid_request_id: string;
  volunteer_id: string;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [requests, setRequests] = useState<AidRequest[]>([]);
  const [verificationTasks, setVerificationTasks] = useState<VerificationTask[]>([]);
  const [message, setMessage] = useState("Loading dashboard...");
  const [nearbyVolunteers, setNearbyVolunteers] = useState<
    Record<string, NearbyVolunteer[]>
  >({});

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("food");
  const [address, setAddress] = useState("");

  async function fetchRequestsForRole(token: string, role: string) {
    let endpoint = "/aid-requests/my";

    if (role === "admin") {
      endpoint = "/aid-requests/admin/all";
    }

    if (role === "donor") {
      endpoint = "/aid-requests/verified";
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      setRequests(data);
    }
  }

  async function fetchVolunteerTasks(token: string) {
    const response = await fetch(`${API_BASE_URL}/verification-tasks/my`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      setVerificationTasks(data);
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

        if (data.role === "volunteer") {
          await fetchVolunteerTasks(token);
        } else {
          await fetchRequestsForRole(token, data.role);
        }
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

      await fetchRequestsForRole(token, "requester");
    } else {
      const errorData = await response.json();
      setMessage(errorData.detail || "Failed to create request.");
    }
  }

  async function handleAdminAction(
    requestId: string,
    action: "approve" | "reject"
  ) {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("Please login first.");
      return;
    }

    setMessage(`${action === "approve" ? "Approving" : "Rejecting"} request...`);

    const response = await fetch(
      `${API_BASE_URL}/aid-requests/${requestId}/${action}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.ok) {
      setMessage(
        `Request ${action === "approve" ? "approved" : "rejected"} successfully.`
      );
      await fetchRequestsForRole(token, "admin");
    } else {
      const errorData = await response.json();
      setMessage(errorData.detail || `Failed to ${action} request.`);
    }
  }

  async function handleFindVolunteers(requestId: string) {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("Please login first.");
      return;
    }

    setMessage("Finding nearby volunteers...");

    const response = await fetch(
      `${API_BASE_URL}/aid-requests/${requestId}/nearby-volunteers`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.ok) {
      const data = await response.json();

      setNearbyVolunteers((previous) => ({
        ...previous,
        [requestId]: data,
      }));

      setMessage("Nearby volunteers loaded.");
    } else {
      const errorData = await response.json();
      setMessage(errorData.detail || "Failed to find volunteers.");
    }
  }

  async function handleAssignVolunteer(requestId: string, volunteerId: string) {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("Please login first.");
      return;
    }

    setMessage("Assigning volunteer...");

    const response = await fetch(
      `${API_BASE_URL}/aid-requests/${requestId}/assign-volunteer`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          volunteer_id: volunteerId,
        }),
      }
    );

    if (response.ok) {
      setMessage("Volunteer assigned successfully.");
      await fetchRequestsForRole(token, "admin");
    } else {
      const errorData = await response.json();
      setMessage(errorData.detail || "Failed to assign volunteer.");
    }
  }

  async function handleVolunteerAction(
    taskId: string,
    action: "verify" | "reject"
  ) {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("Please login first.");
      return;
    }

    setMessage(`${action === "verify" ? "Verifying" : "Rejecting"} task...`);

    const response = await fetch(
      `${API_BASE_URL}/verification-tasks/${taskId}/${action}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          notes:
            action === "verify"
              ? "Verified from volunteer dashboard."
              : "Rejected from volunteer dashboard.",
        }),
      }
    );

    if (response.ok) {
      setMessage(
        `Task ${action === "verify" ? "verified" : "rejected"} successfully.`
      );
      await fetchVolunteerTasks(token);
    } else {
      const errorData = await response.json();
      setMessage(errorData.detail || `Failed to ${action} task.`);
    }
  }

  async function handleClaimRequest(requestId: string) {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setMessage("Please login first.");
      return;
    }

    setMessage("Claiming request...");

    const response = await fetch(`${API_BASE_URL}/aid-requests/${requestId}/claim`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      setMessage("Request claimed successfully.");
      await fetchRequestsForRole(token, "donor");
    } else {
      const errorData = await response.json();
      setMessage(errorData.detail || "Failed to claim request.");
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

        {user?.role === "admin" && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <h2 className="text-2xl font-bold">Admin Review Queue</h2>
            <p className="mt-2 text-slate-400">
              Review requests, approve/reject them, and assign volunteers.
            </p>

            <div className="mt-6 space-y-4">
              {requests.length === 0 && (
                <p className="text-slate-400">No aid requests found.</p>
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

                  {request.status === "submitted" && (
                    <div className="mt-4 flex gap-3">
                      <button
                        type="button"
                        onClick={() => handleAdminAction(request.id, "approve")}
                        className="rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 hover:bg-slate-200"
                      >
                        Approve
                      </button>

                      <button
                        type="button"
                        onClick={() => handleAdminAction(request.id, "reject")}
                        className="rounded-lg border border-slate-600 px-4 py-2 font-semibold text-white hover:bg-slate-900"
                      >
                        Reject
                      </button>
                    </div>
                  )}

                  {request.status === "admin_approved" && (
                    <div className="mt-4">
                      <button
                        type="button"
                        onClick={() => handleFindVolunteers(request.id)}
                        className="rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 hover:bg-slate-200"
                      >
                        Find Nearby Volunteers
                      </button>

                      {nearbyVolunteers[request.id] && (
                        <div className="mt-4 space-y-3">
                          {nearbyVolunteers[request.id].length === 0 && (
                            <p className="text-sm text-slate-400">
                              No nearby volunteers found.
                            </p>
                          )}

                          {nearbyVolunteers[request.id].map((volunteer) => (
                            <div
                              key={volunteer.id}
                              className="rounded-lg border border-slate-700 bg-slate-900 p-4"
                            >
                              <p className="font-semibold text-white">
                                {volunteer.full_name || volunteer.email}
                              </p>
                              <p className="text-sm text-slate-400">
                                {volunteer.email}
                              </p>
                              <p className="text-sm text-slate-500">
                                Distance:{" "}
                                {Math.round(volunteer.distance_meters)} meters
                              </p>

                              <button
                                type="button"
                                onClick={() => handleAssignVolunteer(request.id, volunteer.id)}
                                className="mt-3 rounded-lg border border-slate-600 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
                              >
                                Assign Volunteer
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {user?.role === "volunteer" && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <h2 className="text-2xl font-bold">My Verification Tasks</h2>
            <p className="mt-2 text-slate-400">
              Review assigned aid requests and verify or reject them.
            </p>

            <div className="mt-6 space-y-4">
              {verificationTasks.length === 0 && (
                <p className="text-slate-400">No verification tasks assigned.</p>
              )}

              {verificationTasks.map((task) => (
                <div
                  key={task.id}
                  className="rounded-xl border border-slate-700 bg-slate-950 p-5"
                >
                  <h3 className="text-xl font-semibold">Verification Task</h3>

                  <p className="mt-2 text-sm text-slate-400">
                    Aid Request ID: {task.aid_request_id}
                  </p>

                  <p className="mt-2 text-sm font-semibold text-white">
                    Status: {task.status}
                  </p>

                  {task.notes && (
                    <p className="mt-2 text-sm text-slate-400">
                      Notes: {task.notes}
                    </p>
                  )}

                  {task.status === "assigned" && (
                    <div className="mt-4 flex gap-3">
                      <button
                        type="button"
                        onClick={() => handleVolunteerAction(task.id, "verify")}
                        className="rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 hover:bg-slate-200"
                      >
                        Verify
                      </button>

                      <button
                        type="button"
                        onClick={() => handleVolunteerAction(task.id, "reject")}
                        className="rounded-lg border border-slate-600 px-4 py-2 font-semibold text-white hover:bg-slate-900"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {user?.role === "donor" && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <h2 className="text-2xl font-bold">Available Verified Requests</h2>
            <p className="mt-2 text-slate-400">
              Browse verified aid requests and claim one to fulfill.
            </p>

            <div className="mt-6 space-y-4">
              {requests.length === 0 && (
                <p className="text-slate-400">No verified requests available.</p>
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

                  <button
                    type="button"
                    onClick={() => handleClaimRequest(request.id)}
                    className="mt-4 rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 hover:bg-slate-200"
                  >
                    Claim Request
                  </button>
                </div>
              ))}
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
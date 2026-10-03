"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { API_URL } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);
      
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString()
      });
      
      if (!res.ok) throw new Error("Invalid credentials");
      
      const data = await res.json();
      login(data.access_token, data.refresh_token);
    } catch (e: any) {
      setError(e.message || "Failed to login");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 rounded bg-gray-50 p-6 shadow">
        <h1 className="text-2xl font-bold">Login</h1>
        {error && <div className="text-red-500">{error}</div>}
        <div>
          <label className="block text-sm font-medium">Email</label>
          <input 
            type="email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded border p-2" 
            required 
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Password</label>
          <input 
            type="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded border p-2" 
            required 
          />
        </div>
        <button type="submit" className="w-full rounded bg-blue-600 p-2 text-white hover:bg-blue-700">
          Sign In
        </button>
      </form>
    </div>
  );
}

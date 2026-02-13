import { useState } from "react";
import { login } from "../api";

const DEMO_USERS = [
    { email: "amrutha@company.com", name: "Amrutha", department: "HR" },
    { email: "harshini@company.com", name: "Harshini", department: "Engineering" },
    { email: "tanvi@company.com", name: "Tanvi", department: "Sales" },
    { email: "bhaskar@company.com", name: "Bhaskar", department: "Engineering" },
    { email: "arijith@company.com", name: "Arijith", department: "HR" },
];

export default function Login({ onLogin }) {
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(null);

    const handleLogin = async (user) => {
        setError(null);
        setLoading(user.email);
        try {
            const data = await login(user.email);
            onLogin(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(null);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card">
                <div className="login-header">
                    <div className="app-name">
                        <span className="mark">K</span>
                        Knowledge Base
                    </div>
                    <p className="subtitle">Internal document search &amp; AI answers</p>
                </div>

                <div className="section-label">Select a user</div>
                <div className="user-list">
                    {DEMO_USERS.map((u) => (
                        <button
                            key={u.email}
                            className="user-btn"
                            onClick={() => handleLogin(u)}
                            disabled={loading !== null}
                        >
                            <div className={`initials ${u.department.toLowerCase()}`}>
                                {u.name.slice(0, 2).toUpperCase()}
                            </div>
                            <div className="info">
                                <div className="name">
                                    {u.name}{loading === u.email ? " …" : ""}
                                </div>
                                <div className="dept">{u.department}</div>
                            </div>
                            <span className="chevron">›</span>
                        </button>
                    ))}
                </div>

                {error && <div className="login-error">{error}</div>}
            </div>
        </div>
    );
}

export type RiskProfile = "conservative" | "balanced" | "growth";

export type PortfolioBrief = {
  id: string;
  name: string;
  risk_profile: RiskProfile;
  ai_summary: string;
  created_at: string;
};

export type CreatePortfolioBrief = {
  name: string;
  risk_profile: RiskProfile;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(`API request failed (${response.status})`);
  }
  return (await response.json()) as T;
}

export const listBriefs = () => request<PortfolioBrief[]>("/briefs");

export const createBrief = (input: CreatePortfolioBrief) =>
  request<PortfolioBrief>("/briefs", {
    method: "POST",
    body: JSON.stringify(input),
  });

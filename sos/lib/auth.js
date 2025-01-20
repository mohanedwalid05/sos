class AuthService {
  static async login(retries = 3) {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch("/api/token", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
          body: new URLSearchParams({
            grant_type: "password",
            username: "demo",
            password: "demo",
          }).toString(),
        });

        if (!response.ok) {
          const error = await response.text();
          console.error("Login failed:", error);
          throw new Error(`Login failed: ${error}`);
        }

        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        return data.access_token;
      } catch (error) {
        console.error(`Login attempt ${i + 1} failed:`, error);
        if (i === retries - 1) throw error;
        // Wait before retrying (exponential backoff)
        await new Promise((resolve) =>
          setTimeout(resolve, Math.pow(2, i) * 1000)
        );
      }
    }
  }

  static getToken() {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("token");
  }

  static async ensureToken() {
    let token = this.getToken();
    if (!token) {
      token = await this.login();
    }
    return token;
  }

  static async fetchWithAuth(url, options = {}) {
    try {
      const token = await this.ensureToken();
      const headers = {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...options.headers,
        Authorization: `Bearer ${token}`,
      };

      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Token might be expired, try to login again
        localStorage.removeItem("token"); // Clear the invalid token
        const newToken = await this.login();
        headers.Authorization = `Bearer ${newToken}`;
        return fetch(apiUrl, {
          ...options,
          headers,
        });
      }

      return response;
    } catch (error) {
      if (error.name === "AbortError") {
        // Re-throw abort errors to be handled by the caller
        throw error;
      }
      console.error("API request failed:", error);
      throw error;
    }
  }
}

export default AuthService;

import apiClient from "../api";

export const agentApi = {
  /**
   * Retrieves registered concrete investigation agents list
   */
  list: async () => {
    try {
      const response = await apiClient.get("/api/v1/agents");
      return response.data;
    } catch (e) {
      // Fallback metadata aligning with backend AgentRegistry
      return [
        {
          id: "customer-investigator-01",
          name: "CustomerInvestigationAgent",
          description: "Audits consumer behavior velocity, category anomalies, and payment shifts.",
          version: "1.0.0",
          priority: 10,
          enabled: true,
          type: "Behavioral"
        },
        {
          id: "device-investigator-01",
          name: "DeviceInvestigationAgent",
          description: "Co-ordinates 7 network, browser, routing, and geo-consistency sub-analyzers.",
          version: "1.0.0",
          priority: 20,
          enabled: true,
          type: "Security & Device"
        },
        {
          id: "network-risk-investigator-01",
          name: "NetworkRiskAgent",
          description: "Analyzes identity parameters, shared devices/IPs, and fraud rings.",
          version: "1.0.0",
          priority: 30,
          enabled: true,
          type: "Relational Network"
        }
      ];
    }
  }
};
